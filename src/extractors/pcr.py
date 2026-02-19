import re
from src.extractors.base_extractor import BaseExtractor
from src.transformation.coordinates import gms_to_decimal

class PCRExtractor(BaseExtractor):
    def extract(self, text):
        data = {}
        data['OPERADOR'] = "PCR" [cite: 561]
        data['AREA_CONCE'] = "El Sosneado" [cite: 563]
        
        # Identificador único
        num_inc = re.search(r'MDZ-(\d+-\d+)', text)
        data['NUM_INC'] = num_inc.group(0) if num_inc else None [cite: 558]
        
        fecha = re.search(r'Fecha:\s+(\d{2}-\d{2}-\d{4})', text)
        data['FECHA_MAIL'] = self.normalize_date(fecha.group(1)) if fecha else None [cite: 565]
        
        # Normalización de Magnitud (Bajo -> Menor)
        if "BAJO" in text.upper():
            data['MAGNITUD'] = "Menor" [cite: 571]
        
        # Extracción de coordenadas GMS
        lat_gms = re.search(r'Lat\.\s+S=\s*([\d°\'"\.\s,]+)', text)
        lon_gms = re.search(r'Long\.\s+O=\s*([\d°\'"\.\s,]+)', text)
        
        if lat_gms:
            data['Y_COORD'] = gms_to_decimal(lat_gms.group(1)) [cite: 590]
        if lon_gms:
            data['X_COORD'] = gms_to_decimal(lon_gms.group(1)) [cite: 591]
            
        # Volúmenes (PCR suele dar el neto directamente)
        vol_neto = re.search(r'neto de hidrocarburo:\s*(\d+,\d+)', text)
        data['VOL_D_m3'] = float(vol_neto.group(1).replace(',', '.')) if vol_neto else 0.0 [cite: 601]
        
        return data