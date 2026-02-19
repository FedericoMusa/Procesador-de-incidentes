import re
from src.extractors.base_extractor import BaseExtractor

class YPFExtractor(BaseExtractor):
    def extract(self, text):
        data = {}
        data['OPERADOR'] = "YPF S.A." # 
        
        # Identificador único (Comunicado Incidente N°)
        num_inc = re.search(r'Incidente N°\s*(\d+)', text)
        data['NUM_INC'] = num_inc.group(1) if num_inc else None # 
        
        # El Área manda en el nombre del registro
        area = re.search(r'Área concesionada:\s*([^\n]+)', text)
        data['AREA_CONCE'] = area.group(1).strip() if area else "DESFILADERO BAYO" # 
        
        # Fecha de ocurrencia
        fecha = re.search(r'Fecha de ocurrencia:\s*(\d{2}/\d{2}/\d{4})', text)
        data['FECHA_MAIL'] = self.normalize_date(fecha.group(1)) if fecha else None # 
        
        # Magnitud e Instalación
        magnitud = re.search(r'Magnitud del Incidente:\s*(\w+)', text)
        data['MAGNITUD'] = magnitud.group(1) if magnitud else "Menor" # 
        
        inst = re.search(r'Nombre de la instalación:\s*([^\n]+)', text)
        data['INSTALACION'] = inst.group(1).strip() if inst else None # 
        
        # Georreferenciación (YPF suele dar decimales directos)
        lat = re.search(r'Latitud \(S\):\s*(-?\d+\.\d+)', text)
        lon = re.search(r'Longitud \(W\):\s*(-?\d+\.\d+)', text)
        data['Y_COORD'] = float(lat.group(1)) if lat else None # 
        data['X_COORD'] = float(lon.group(1)) if lon else None # 
        
        # Volúmenes (manejo de los 4 decimales de YPF)
        vol = re.search(r'Volumen m3 derramado:\s*([\d.]+)', text)
        agua = re.search(r'% Agua contenido:\s*([\d.]+)', text)
        data['VOL_D_m3'] = float(vol.group(1)) if vol else 0.0 # 
        data['AGUA'] = float(agua.group(1)) if agua else 0.0 # 
        
        return data