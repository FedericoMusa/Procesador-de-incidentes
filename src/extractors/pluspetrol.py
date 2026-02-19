import re
from src.extractors.base_extractor import BaseExtractor
from src.transformation.coordinates import gk_to_decimal

class PluspetrolExtractor(BaseExtractor):
    def extract(self, text):
        data = {}
        data['OPERADOR'] = "Pluspetrol S.A."
        
        # [cite_start]Extracción de Concesión y Número [cite: 5, 6, 8]
        area = re.search(r'CONCESION:\s*(\w+)', text)
        [cite_start]data['AREA_CONCE'] = area.group(1) if area else "JCP" [cite: 6]
        
        num_com = re.search(r'COMUNICADO N°:\s*([\d/]+)', text)
        [cite_start]data['NUM_INC'] = num_com.group(1) if num_com else None [cite: 4]
        
        # [cite_start]Fecha y Hora [cite: 2, 3]
        fecha = re.search(r'FECHA:\s*(\d{2}/\d{2}/\d{4})', text)
        [cite_start]data['FECHA_MAIL'] = self.normalize_date(fecha.group(1)) if fecha else None [cite: 2]
        
        # [cite_start]Coordenadas Gauss-Krüger (X=S, Y=W en el PDF) [cite: 13]
        # Nota: Pluspetrol etiqueta X para la coordenada Norte y Y para la Este
        x_gk = re.search(r'X:\s*(\d+)', text)
        y_gk = re.search(r'Y:\s*(\d+)', text)
        
        if x_gk and y_gk:
            # [cite_start]Convertimos de GK Faja 2 a Decimal WGS84 [cite: 13]
            lat, lon = gk_to_decimal(float(x_gk.group(1)), float(y_gk.group(1)), faja=2)
            data['Y_COORD'] = lat
            data['X_COORD'] = lon
        
        # [cite_start]Magnitud: Mapeo de casilleros [cite: 9]
        if "BAJA" in text.upper():
            data['MAGNITUD'] = "Menor"
        elif "MEDIA" in text.upper():
            data['MAGNITUD'] = "Intermedio"
        
        # [cite_start]Volúmenes [cite: 15]
        vol = re.search(r'Vol\. derramado:\s*([\d,]+)', text)
        [cite_start]data['VOL_D_m3'] = float(vol.group(1).replace(',', '.')) if vol else 0.0 [cite: 15]
        
        return data