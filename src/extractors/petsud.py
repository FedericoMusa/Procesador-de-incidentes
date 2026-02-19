"""
Extractor para informes de Petróleos Sudamericanos.
Formato: tabla estructurada "Informe Preliminar Mendoza" con N° de Comunicado.
Sistema de coordenadas: DMS compacto (ej. 33°30'57,62").

ATENCIÓN: El PDF de ejemplo tiene una inconsistencia real en las coordenadas:
  Longitud reportada: 68°38'84,82" → los segundos (84,82) exceden 60,
  lo que indica un error de tipeo en el informe original. El extractor
  detecta este caso y lo marca como inválido para revisión manual.
"""

import logging
import re
from src.extractors.base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class PetSudExtractor(BaseExtractor):
    """
    Extrae datos de incidentes del formato de Petróleos Sudamericanos.
    """

    def extract(self, text: str) -> dict:
        data = {}

        # ── Identificación ──────────────────────────────────────────────
        data['OPERADOR'] = "Petróleos Sudamericanos"

        num_inc = self._find(r'N[°º]\s*DE\s*COMUNICADO\s+(\d+)', text)
        data['NUM_INC'] = f"PETSUD-{num_inc}" if num_inc else None

        # ── Área y ubicación ────────────────────────────────────────────
        data['AREA_CONCE'] = self._find(
            r'Área operativa\s*/\s*concesión\s+(.+)', text)
        data['YACIMIENTO'] = self._find(
            r'Yacimiento\s+(.+)', text)
        data['CUENCA'] = self._find(
            r'Cuenca\s+(.+)', text)

        # ── Instalación ─────────────────────────────────────────────────
        data['INSTALACION'] = self._find(
            r'Instalación asociada\s+(.+)', text)
        data['TIPO_INST'] = self._find(
            r'Tipo de instalación\s+(.+)', text)

        # ── Incidente ───────────────────────────────────────────────────
        data['SUBTIPO_INC'] = self._find(
            r'Subtipo de incidente\s+(.+)', text)
        data['CAUSA'] = self._find(
            r'Tipo de evento causante\s+(.+)', text)
        data['MAGNITUD'] = self._find(
            r'Magnitud del Incidente\s+(.+)', text)
        data['DESCRIPCION'] = self._find(
            r'Descripción de la rotura y afectación\s*\n(.+)', text)

        # ── Fecha ───────────────────────────────────────────────────────
        fecha_raw = self._find(
            r'Fecha de ocurrencia\s+(\d{1,2}/\d{1,2}/\d{4})', text)
        data['FECHA_INC'] = self.normalize_date(fecha_raw)
        data['HORA_INC'] = self._find(
            r'Hora de ocurrencia\s+(\d{1,2}:\d{2})', text)

        # ── Coordenadas DMS compacto ─────────────────────────────────────
        # Formato: "33°30'57,62"" — signo negativo se aplica por contexto (S/W)
        lat_raw = self._find(
            r'Coordenadas x\s*\(latitud\s*-\s*S\)\s+([\d°\'".,′″]+)', text)
        lon_raw = self._find(
            r'Coordenadas y\s*\(Longitud\s*-\s*O\)\s+([\d°\'".,′″]+)', text)

        lat_dd = self._parse_and_negate(lat_raw, "Latitud")
        lon_dd = self._parse_and_negate(lon_raw, "Longitud")

        data['Y_COORD'] = lat_dd
        data['X_COORD'] = lon_dd
        data['SRID_ORIGEN'] = "WGS84-DMS→DD"

        if not self.validate_coordinates(data['Y_COORD'], data['X_COORD']):
            logger.warning(
                f"[PetSud] Coordenadas inválidas en {data['NUM_INC']}. "
                "Verificar si hay error de tipeo en el informe original."
            )

        # ── Volúmenes ───────────────────────────────────────────────────
        data['VOL_D_m3'] = self._find_float(
            r'Volumen\s+m3?\s+derramado\s+([\d.,]+)', text)
        data['VOL_R_m3'] = self._find_float(
            r'Volumen\s+m3?\s+recuperado\s+([\d.,]+)', text)
        data['AGUA_PCT'] = self._find_float(
            r'%\s*AGUA\s+DERRAMADO\s+([\d.,]+)', text)
        data['AREA_AFECT_m2'] = self._find_float(
            r'Área\s+m2\s+([\d.,]+)', text)
        data['PPM_HC'] = self._find(
            r'Concentración de hidrocarburo\s*\(ppm\)\s+(.+)', text)

        # ── Recursos afectados ──────────────────────────────────────────
        # En PetSud los recursos se marcan con "x" en una tabla
        recursos = []
        for recurso in ["Suelo", "Cauce aluvional", "Agua superficial",
                        "Vegetacion", "Otros"]:
            pattern = rf'{recurso}\s+x'
            if re.search(pattern, text, re.IGNORECASE):
                recursos.append(recurso)
        data['RECURSOS'] = ", ".join(recursos) if recursos else None

        data['MEDIDAS'] = self._find(
            r'Medidas adoptadas\s+(.+?)(?:\n\n|\Z)', text, flags=re.DOTALL)

        return data

    def _parse_and_negate(self, raw: str | None, label: str) -> float | None:
        """Parsea DMS y aplica signo negativo (S/W siempre negativos en Mendoza)."""
        if raw is None:
            logger.warning(f"[PetSud] {label} no encontrada en el texto.")
            return None
        dd = self.parse_dms_string(raw)
        if dd is None:
            return None
        return -abs(dd)