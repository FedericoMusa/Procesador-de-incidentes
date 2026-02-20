"""
Base class para todos los extractores de incidentes ambientales.
Define la interfaz común y utilidades compartidas (regex seguro,
normalización de fechas, conversión de coordenadas DMS→DD).
"""

import re
import logging
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)

# Rango geográfico válido para Mendoza (WGS84 grados decimales)
LAT_MIN, LAT_MAX = -39.0, -32.0  # -39.0 cubre Chihuido de la Sierra Negra (límite Mendoza/Neuquén)
LON_MIN, LON_MAX = -70.0, -67.0


class BaseExtractor(ABC):
    """Clase base abstracta para extractores de incidentes."""

    # ------------------------------------------------------------------ #
    #  Interfaz pública                                                    #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def extract(self, text: str) -> dict:
        """
        Extrae los campos del incidente desde el texto del PDF.
        Debe retornar un dict con las claves del esquema unificado.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    #  Helpers de regex (seguros: nunca lanzan AttributeError)            #
    # ------------------------------------------------------------------ #

    def _find(self, pattern: str, text: str, group: int = 1,
              flags: int = re.IGNORECASE) -> str | None:
        """Busca un patrón y retorna el grupo indicado, o None si no matchea."""
        match = re.search(pattern, text, flags)
        if match:
            try:
                return match.group(group).strip()
            except IndexError:
                return match.group(0).strip()
        return None

    def _find_float(self, pattern: str, text: str, group: int = 1,
                    flags: int = re.IGNORECASE) -> float | None:
        """Busca un patrón numérico y retorna float, o None si no matchea."""
        raw = self._find(pattern, text, group, flags)
        if raw is None:
            return None
        try:
            return float(raw.replace(',', '.'))
        except ValueError:
            logger.warning(f"No se pudo convertir a float: '{raw}'")
            return None

    # ------------------------------------------------------------------ #
    #  Normalización de fechas                                            #
    # ------------------------------------------------------------------ #

    DATE_FORMATS = [
        "%d/%m/%Y",   # 10/10/2025
        "%d/%m/%y",   # 10/10/25
        "%d-%m-%Y",   # 10-10-2025
        "%d-%m-%y",   # 10-10-25
        "%Y-%m-%d",   # 2025-10-10
    ]

    def normalize_date(self, raw: str | None) -> str | None:
        """
        Convierte cualquier formato de fecha soportado a dd-mm-yyyy.
        Retorna None si el valor es None o no puede parsearse.
        """
        if raw is None:
            return None
        raw = raw.strip()
        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(raw, fmt).strftime("%d-%m-%Y")
            except ValueError:
                continue
        logger.warning(f"Formato de fecha no reconocido: '{raw}'")
        return None

    # ------------------------------------------------------------------ #
    #  Conversión de coordenadas                                          #
    # ------------------------------------------------------------------ #

    def dms_to_dd(self, degrees: float, minutes: float,
                  seconds: float = 0.0, hemisphere: str = "S") -> float:
        """
        Convierte Grados° Minutos' Segundos'' a grados decimales.
        Aplica signo negativo automáticamente para S y W.
        """
        dd = degrees + minutes / 60.0 + seconds / 3600.0
        if hemisphere.upper() in ("S", "W"):
            dd = -dd
        return round(dd, 6)

    def parse_dms_string(self, raw: str) -> float | None:
        """
        Parsea strings de coordenadas en distintos formatos DMS:
          - '37 ° / 20.936 ''         → grados y minutos decimales
          - '37 ° / 20 ' / 56.2 '''   → grados, minutos y segundos
          - '33°30'57,62"'             → formato compacto
        Retorna grados decimales (siempre negativo para S/W).
        """
        # Formato compacto: 33°30'57,62" o 33°30′57,62″
        m = re.match(
            r"(\d+)[°º]\s*(\d+)[''′]\s*([\d.,]+)[\"″''′]?",
            raw.strip()
        )
        if m:
            deg = float(m.group(1))
            mins = float(m.group(2))
            secs = float(m.group(3).replace(',', '.'))
            return self.dms_to_dd(deg, mins, secs)

        # Formato con separadores / : '37 ° / 20 ' / 56.2 '''
        m = re.match(
            r"(\d+)\s*[°º]\s*/?\s*(\d+[\.,]?\d*)\s*[''′]\s*/?\s*([\d.,]+)",
            raw.strip()
        )
        if m:
            deg = float(m.group(1))
            mins = float(m.group(2).replace(',', '.'))
            secs = float(m.group(3).replace(',', '.'))
            return self.dms_to_dd(deg, mins, secs)

        # Solo grados y minutos: '37 ° / 20.936 ''
        m = re.match(
            r"(\d+)\s*[°º]\s*/?\s*([\d.,]+)\s*[''′]",
            raw.strip()
        )
        if m:
            deg = float(m.group(1))
            mins = float(m.group(2).replace(',', '.'))
            return self.dms_to_dd(deg, mins)

        logger.warning(f"No se pudo parsear coordenada DMS: '{raw}'")
        return None

    # ------------------------------------------------------------------ #
    #  Validación geográfica                                              #
    # ------------------------------------------------------------------ #

    def inferir_magnitud(self, vol_m3: float | None, ppm: float | None = None) -> str:
        """
        Infiere la magnitud del incidente a partir del volumen y PPM
        según la normativa Res. 24-04 / Dec. 437-93.

        Reglas (en orden de prioridad):
          - HC > 50 PPM y vol > 5 m3  → "Mayor"
          - HC < 50 PPM y vol > 10 m3 → "Mayor"
          - vol <= 5 m3 (con HC > 50)  → "Menor"
          - vol <= 10 m3 (con HC < 50) → "Menor"
          - Sin datos suficientes       → "No determinado"

        IMPORTANTE: este es un fallback cuando el PDF no informa magnitud.
        El valor real puede diferir si el incidente involucra cauces de agua
        u otros factores cualitativos que la normativa también considera.
        """
        if vol_m3 is None:
            return "No determinado"

        # PPM desconocida: usar umbral más conservador (HC > 50 asumido)
        if ppm is None:
            return "Mayor" if vol_m3 > 5 else "Menor"

        if ppm > 50:
            return "Mayor" if vol_m3 > 5 else "Menor"
        else:
            return "Mayor" if vol_m3 > 10 else "Menor"

    def validate_coordinates(self, lat: float | None,
                             lon: float | None) -> bool:
        """
        Verifica que las coordenadas estén dentro del bounding box de Mendoza.
        Retorna False (y loguea warning) si alguno es None o está fuera de rango.
        """
        if lat is None or lon is None:
            logger.warning("Coordenadas ausentes, registro rechazado.")
            return False

        lat_ok = LAT_MIN <= lat <= LAT_MAX
        lon_ok = LON_MIN <= lon <= LON_MAX

        if not lat_ok or not lon_ok:
            logger.warning(
                f"Coordenadas fuera de Mendoza: lat={lat}, lon={lon}. "
                f"Rango válido lat [{LAT_MIN}, {LAT_MAX}], "
                f"lon [{LON_MIN}, {LON_MAX}]."
            )
            return False
        return True