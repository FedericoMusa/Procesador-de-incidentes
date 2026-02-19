import re
from src.extractors.base_extractor import BaseExtractor
from src.transformation.coordinates import gms_to_decimal

class PetSudExtractor(BaseExtractor):
    def extract(self, text):
        data = {}
        [cite_start]data['OPERADOR'] = "Petróleos Sudamericanos" [cite: 37, 81, 127]
        
        # [cite_start]Mapeo de Área y Número [cite: 28, 29, 35, 38]
        num = re.search(r'N° DE COMUNICADO\s+(\d+)', text)
        [cite_start]data['NUM_INC'] = num.group(1) if num else None [cite: 29, 78, 124]
        
        area = re.search(r'Área operativa / concesión\s+([\w\s]+)', text)
        [cite_start]data['AREA_CONCE'] = area.group(1).strip() if area else "La Ventana" [cite: 38, 82, 128]
        
        # [cite_start]Magnitud e Instalación [cite: 40, 43, 74, 86, 89]
        [cite_start]data['MAGNITUD'] = "Menor" if "Menor" in text else "Mayor" [cite: 43, 89, 137]
        inst = re.search(r'Instalación asociada\s+([\w\s\-\d]+)', text)
        [cite_start]data['INSTALACION'] = inst.group(1).strip() if inst else None [cite: 40, 86, 133]
        
        # [cite_start]Coordenadas GMS [cite: 47, 91, 92, 139, 140]
        lat_gms = re.search(r'latitud - S\)\s*([\d°\'"\.\s,]+)', text)
        lon_gms = re.search(r'Longitud - O\)\s*([\d°\'"\.\s,]+)', text)
        
        if lat_gms:
            data['Y_COORD'] = gms_to_decimal(lat_gms.group(1))
        if lon_gms:
            data['X_COORD'] = gms_to_decimal(lon_gms.group(1))
            
        # [cite_start]Volúmenes y Agua [cite: 49, 50, 94, 95]
        vol = re.search(r'Volumen m³ derramado\s+([\d,]+)', text)
        agua = re.search(r'% AGUA DERRAMADO\s+(\d+)', text)
        [cite_start]data['VOL_D_m3'] = float(vol.group(1).replace(',', '.')) if vol else 0.0 [cite: 49, 94, 142]
        [cite_start]data['AGUA'] = float(agua.group(1)) if agua else 0.0 [cite: 50, 95, 143]
        
        return data