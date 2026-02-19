import os
import fitz  # PyMuPDF
import sqlite3
from src.extractors.ypf import YPFExtractor
from src.extractors.pluspetrol import PluspetrolExtractor
from src.extractors.petsud import PetSudExtractor
from src.extractors.aconcagua import AconcaguaExtractor
from src.extractors.pcr import PCRExtractor
from src.transformation.coordinates import transform_to_cartesian

def identify_extractor(text):
    """Identifica la operadora según palabras clave en el texto."""
    text_upper = text.upper()
    if "YPF S.A." in text_upper:
        return YPFExtractor()
    elif "PLUSPETROL" in text_upper:
        return PluspetrolExtractor()
    elif "PETROLEOS SUDAMERICANOS" in text_upper:
        return PetSudExtractor()
    elif "ACONCAGUA ENERGIA" in text_upper:
        return AconcaguaExtractor()
    elif "PCR" in text_upper or "COMODORO RIVADAVIA" in text_upper:
        return PCRExtractor()
    return None

def main():
    raw_dir = os.path.join('data', 'raw')
    db_path = os.path.join('data', 'database', 'incidentes.db')
    
    conn = sqlite3.connect(db_path)
    
    for filename in os.listdir(raw_dir):
        if filename.endswith('.pdf'):
            print(f"Procesando: {filename}...")
            path = os.path.join(raw_dir, filename)
            
            # 1. Extracción de texto
            with fitz.open(path) as doc:
                text = chr(12).join([page.get_text() for page in doc])
            
            # 2. Selección de extractor
            extractor = identify_extractor(text)
            if not extractor:
                print(f"No se reconoció el formato para {filename}")
                continue
                
            # 3. Mapeo de datos crudos
            try:
                data = extractor.extract(text)
                
                # 4. Transformación Cartesiana (Metros UTM)
                east, north = transform_to_cartesian(data['Y_COORD'], data['X_COORD'])
                data['COORD_EAST_M'] = east
                data['COORD_NORTH_M'] = north
                data['SRID_ORIGEN'] = "Determinado por Extractor"
                
                # 5. Carga en SQLite (Evitando duplicados por NUM_INC)
                columns = ', '.join(data.keys())
                placeholders = ':' + ', :'.join(data.keys())
                query = f"INSERT OR IGNORE INTO incidentes ({columns}) VALUES ({placeholders})"
                
                conn.execute(query, data)
                conn.commit()
                
            except Exception as e:
                print(f"Error procesando {filename}: {e}")

    conn.close()
    print("Proceso finalizado.")

if __name__ == "__main__":
    main()