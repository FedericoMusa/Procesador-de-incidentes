"""
Procesador de Incidentes Ambientales — Oil & Gas Mendoza
Ejecutor principal: extrae PDFs, transforma coordenadas y carga en SQLite.
Exporta automáticamente a Excel al finalizar.
"""

import os
import logging
import sqlite3
import fitz       # PyMuPDF
import pandas as pd

from src.extractors.ypf import YPFExtractor
from src.extractors.pluspetrol import PluspetrolExtractor
from src.extractors.petsud import PetSudExtractor
from src.extractors.aconcagua import AconcaguaExtractor
from src.extractors.pcr import PCRExtractor
from src.transformation.coordinates import transform_to_cartesian

# ── Configuración de logging ────────────────────────────────────────────────
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s — %(message)s',
    handlers=[
        logging.FileHandler('logs/processor.log', encoding='utf-8'),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# ── Esquema final de columnas ────────────────────────────────────────────────
COLUMNAS_FINALES = [
    'NUM_INC',
    'OPERADOR',
    'AREA_CONCESION',
    'YACIMIENTO',
    'MAGNITUD',
    'TIPO_INSTALACION',
    'SUBTIPO',
    'FECHA',
    'DESC_ABREV',
    'LAT',
    'LON',
    'VOL_M3',
    'AGUA_PCT',
    'AREA_AFECT_m2',
    'RECURSOS_AFECTADOS',
]

def normalizar(data: dict) -> dict:
    lat = data.get('Y_COORD')
    lon = data.get('X_COORD')
    coord_texto = f"{lat}, {lon}" if lat is not None and lon is not None else None

    desc = data.get('DESCRIPCION') or data.get('DETALLE') or None
    desc_abrev = (desc[:120] + '...') if desc and len(desc) > 120 else desc

    return {
        'NUM_INC':            data.get('NUM_INC'),
        'OPERADOR':           data.get('OPERADOR'),
        'AREA_CONCESION':     data.get('AREA_CONCE'),
        'YACIMIENTO':         data.get('YACIMIENTO'),
        'MAGNITUD':           data.get('MAGNITUD'),
        'TIPO_INSTALACION':   data.get('TIPO_INST'),
        'SUBTIPO':            data.get('SUBTIPO_INC'),
        'FECHA':              data.get('FECHA_INC'),
        'DESC_ABREV':         desc_abrev,
        'LAT':                data.get('Y_COORD'),
        'LON':                data.get('X_COORD'),
        'VOL_M3':             data.get('VOL_D_m3'),
        'AGUA_PCT':           data.get('AGUA_PCT'),
        'AREA_AFECT_m2':      data.get('AREA_AFECT_m2'),
        'RECURSOS_AFECTADOS': data.get('RECURSOS'),
    }

EXTRACTOR_REGISTRY: list[tuple[str, type]] = [
    ("YPF S.A.",                YPFExtractor),
    ("PLUSPETROL",              PluspetrolExtractor),
    ("PETROLEOS SUDAMERICANOS", PetSudExtractor),
    ("ACONCAGUA ENERGIA",       AconcaguaExtractor),
    ("PCR",                     PCRExtractor),
    ("COMODORO RIVADAVIA",      PCRExtractor),
]

def identify_extractor(text: str):
    text_upper = text.upper()
    for keyword, extractor_cls in EXTRACTOR_REGISTRY:
        if keyword in text_upper:
            return extractor_cls()
    return None

def init_database(db_path: str) -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS incidentes (
                NUM_INC           TEXT PRIMARY KEY,
                OPERADOR          TEXT,
                AREA_CONCESION    TEXT,
                YACIMIENTO        TEXT,
                MAGNITUD          TEXT,
                TIPO_INSTALACION  TEXT,
                SUBTIPO           TEXT,
                FECHA             TEXT,
                DESC_ABREV        TEXT,
                LAT               REAL,
                LON               REAL,
                VOL_M3            REAL,
                AGUA_PCT          REAL,
                AREA_AFECT_m2     REAL,
                RECURSOS_AFECTADOS TEXT
            )
        ''')
        conn.commit()
    logger.info(f"Base de datos lista: {db_path}")

def process_pdf(path: str) -> dict | None:
    filename = os.path.basename(path)
    try:
        with fitz.open(path) as doc:
            text = chr(12).join(page.get_text() for page in doc)
    except Exception as e:
        logger.error(f"[{filename}] Error abriendo PDF: {e}")
        return None

    extractor = identify_extractor(text)
    if not extractor:
        logger.warning(f"[{filename}] Formato no reconocido, se omite.")
        return None

    logger.info(f"[{filename}] Extractor: {type(extractor).__name__}")

    try:
        raw = extractor.extract(text)
    except (KeyError, AttributeError, ValueError) as e:
        logger.error(f"[{filename}] Error de extracción: {e}")
        return None

    try:
        if raw.get('Y_COORD') and raw.get('X_COORD'):
            raw['COORD_EAST_M'], raw['COORD_NORTH_M'] = transform_to_cartesian(
                raw['Y_COORD'], raw['X_COORD']
            )
    except Exception as e:
        logger.error(f"[{filename}] Error en transformación UTM: {e}")

    return normalizar(raw)

def insert_incident(conn: sqlite3.Connection, data: dict) -> bool:
    try:
        columns = ', '.join(data.keys())
        placeholders = ':' + ', :'.join(data.keys())
        cursor = conn.execute(
            f"INSERT OR IGNORE INTO incidentes ({columns}) VALUES ({placeholders})",
            data
        )
        if cursor.rowcount == 0:
            logger.info(f"Duplicado ignorado: {data.get('NUM_INC')}")
            return False
        return True
    except sqlite3.IntegrityError as e:
        logger.error(f"Error de integridad para {data.get('NUM_INC')}: {e}")
        return False
    except sqlite3.OperationalError as e:
        logger.error(f"Error de base de datos para {data.get('NUM_INC')}: {e}")
        return False

def exportar_excel(db_path: str) -> None:
    xlsx_path = os.path.join('data', 'incidentes.xlsx')
    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql("SELECT * FROM incidentes ORDER BY FECHA", conn)
        with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Incidentes')
            ws = writer.sheets['Incidentes']
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 60)
        logger.info(f"Excel exportado: {xlsx_path}")
    except Exception as e:
        logger.error(f"Error exportando Excel: {e}")

def main():
    raw_dir = os.path.join('data', 'raw')
    db_path  = os.path.join('data', 'database', 'incidentes.db')

    if not os.path.isdir(raw_dir):
        logger.error(f"Directorio no encontrado: {raw_dir}")
        return

    init_database(db_path)

    pdfs = sorted(f for f in os.listdir(raw_dir) if f.lower().endswith('.pdf'))
    if not pdfs:
        logger.warning(f"No se encontraron PDFs en {raw_dir}")
        return

    logger.info(f"Iniciando proceso. PDFs encontrados: {len(pdfs)}")
    insertados = omitidos = errores = 0

    with sqlite3.connect(db_path) as conn:
        for filename in pdfs:
            logger.info(f"Procesando: {filename}")
            data = process_pdf(os.path.join(raw_dir, filename))
            if data is None:
                omitidos += 1
                continue
            if insert_incident(conn, data):
                insertados += 1
            else:
                errores += 1
        conn.commit()

    logger.info(
        f"Proceso finalizado — "
        f"Insertados: {insertados} | Omitidos: {omitidos} | Errores: {errores}"
    )
    exportar_excel(db_path)

if __name__ == "__main__":
    main()