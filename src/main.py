import fitz  # PyMuPDF
from src.extractors.aconcagua import AconcaguaExtractor
from src.extractors.pcr import PCRExtractor
from src.transformation.coordinates import transform_to_cartesian
import sqlite3

def process_all_pdfs():
    # Conexión a la DB local que creamos
    conn = sqlite3.connect('data/database/incidentes.db')
    
    # Lista de archivos en data/raw/
    # (Aquí iría la lógica para iterar archivos)
    
    # Ejemplo de lógica de decisión:
    text = "Texto extraído del PDF..." 
    
    if "ACONCAGUA ENERGIA" in text:
        extractor = AconcaguaExtractor()
    elif "PCR" in text or "Petroquimica Comodoro" in text:
        extractor = PCRExtractor()
    # ... agregar los demás
    
    clean_data = extractor.extract(text)
    
    # Paso final de integridad: Conversión Cartesiana antes de guardar
    east, north = transform_to_cartesian(clean_data['Y_COORD'], clean_data['X_COORD'])
    clean_data['COORD_EAST_M'] = east
    clean_data['COORD_NORTH_M'] = north
    
    # Insertar en SQLite (usando pandas o SQL directo)
    # ...