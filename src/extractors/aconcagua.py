import re
from src.extractors.base_extractor import BaseExtractor

class AconcaguaExtractor(BaseExtractor):
    def extract(self, text):
        data = {}
        # Mapeo según el "Área" como nombre principal
        data['AREA_CONCE'] = "Chañares Herrados"
        data['OPERADOR'] = "Aconcagua Energía"
        
        # Extracción por Regex de patrones clave
        num_pozo = re.search(r'CH-(\d+)', text)
        data['NUM_INC'] = f"CH-{num_pozo.group(1)}" if num_pozo else "S/N"
        
        fecha = re.search(r'(\d{2}/\d{2}/\d{4})', text)
        data['FECHA_MAIL'] = self.normalize_date(fecha.group(1)) if fecha else None
        
        # Datos cuantitativos
        vol = re.search(r'derramado\s+(\d+,\d+)', text)
        agua = re.search(r'(\d+,\d+)\s+%', text)
        data['VOL_D_m3'] = float(vol.group(1).replace(',', '.')) if vol else 0.0
        data['AGUA'] = float(agua.group(1).replace(',', '.')) if agua else 0.0
        
        # Georreferenciación decimal directa
        lat = re.search(r'Latitud Decimal\s+(-?\d+\.\d+)', text)
        lon = re.search(r'Longitud Decimal\s+(-?\d+\.\d+)', text)
        data['Y_COORD'] = float(lat.group(1)) if lat else None
        data['X_COORD'] = float(lon.group(1)) if lon else None
        
        data['INSTALACION'] = f"Pozo {num_pozo.group(0)}" if num_pozo else "Cañería"
        data['MAGNITUD'] = "Menor" # Aconcagua suele reportar incidentes menores en estos formatos
        
        return data