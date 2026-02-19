"""
Procesador de Incidentes Ambientales — Oil & Gas Mendoza
Ejecutor principal: extrae PDFs, transforma coordenadas y carga en SQLite.
"""

import os
import logging
import sqlite3
import fitz  # PyMuPDF

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

# ── Registro de extractores (patrón registro — extensible sin tocar main) ───
# Para agregar una nueva operadora: añadir una tupla aquí, sin más cambios.
EXTRACTOR_REGISTRY: list[tuple[str, type]] = [
    ("YPF S.A.",               YPFExtractor),
    ("PLUSPETROL",             PluspetrolExtractor),
    ("PETROLEOS SUDAMERICANOS", PetSudExtractor),
    ("ACONCAGUA ENERGIA",      AconcaguaExtractor),
    ("PCR",                    PCRExtractor),
    ("COMODORO RIVADAVIA",     PCRExtractor),  # alias de PCR
]


def identify_extractor(text: str):
    """
    Identifica la operadora según palabras clave en el texto
    y retorna una instancia del extractor correspondiente.
    Retorna None si el formato no es reconocido.
    """
    text_upper = text.upper()
    for keyword, extractor_cls in EXTRACTOR_REGISTRY:
        if keyword in text_upper:
            return extractor_cls()
    return None


def init_database(db_path: str) -> None:
    """
    Crea la base de datos y la tabla incidentes si no existen.
    Se ejecuta siempre al inicio — si ya existe, no hace nada.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS incidentes (
                NUM_INC         TEXT PRIMARY KEY,
                OPERADOR        TEXT,
                AREA_CONCE      TEXT,
                YACIMIENTO      TEXT,
                CUENCA          TEXT,
                AREA_OPERATIVA  TEXT,
                INSTALACION     TEXT,
                TIPO_INST       TEXT,
                SUBTIPO_INC     TEXT,
                CAUSA           TEXT,
                MAGNITUD        TEXT,
                DESCRIPCION     TEXT,
                FECHA_INC       TEXT,
                HORA_INC        TEXT,
                HORA_ESTIMADA   TEXT,
                Y_COORD         REAL,
                X_COORD         REAL,
                COORD_EAST_M    REAL,
                COORD_NORTH_M   REAL,
                SRID_ORIGEN     TEXT,
                VOL_D_m3        REAL,
                VOL_R_m3        REAL,
                VOL_GAS_m3      REAL,
                AGUA_PCT        REAL,
                AREA_AFECT_m2   REAL,
                PPM_HC          TEXT,
                RECURSOS        TEXT,
                MEDIDAS         TEXT,
                RESPONSABLE     TEXT,
                UBICACION       TEXT,
                GK_X_M          REAL,
                GK_Y_M          REAL,
                SRID_GK         TEXT,
                CODIGO          TEXT
            )
        ''')
        conn.commit()
    logger.info(f"Base de datos lista: {db_path}")


def process_pdf(path: str) -> dict | None:
    """
    Abre un PDF, identifica la operadora y extrae los datos del incidente.
    Retorna el dict de datos o None si el formato no es reconocido
    o si ocurre un error de extracción.
    """
    filename = os.path.basename(path)

    # 1. Extracción de texto
    try:
        with fitz.open(path) as doc:
            text = chr(12).join(page.get_text() for page in doc)
    except Exception as e:
        logger.error(f"[{filename}] Error abriendo PDF: {e}")
        return None

    # 2. Identificación de extractor
    extractor = identify_extractor(text)
    if not extractor:
        logger.warning(f"[{filename}] Formato no reconocido, se omite.")
        return None

    logger.info(f"[{filename}] Extractor: {type(extractor).__name__}")

    # 3. Extracción de datos
    try:
        data = extractor.extract(text)
    except (KeyError, AttributeError, ValueError) as e:
        logger.error(f"[{filename}] Error de extracción: {e}")
        return None

    # 4. Transformación de coordenadas a UTM (metros cartesianos)
    try:
        if data.get('Y_COORD') and data.get('X_COORD'):
            east, north = transform_to_cartesian(
                data['Y_COORD'], data['X_COORD']
            )
            data['COORD_EAST_M'] = east
            data['COORD_NORTH_M'] = north
        else:
            logger.warning(f"[{filename}] Sin coordenadas válidas, se omite transformación UTM.")
            data['COORD_EAST_M'] = None
            data['COORD_NORTH_M'] = None
    except Exception as e:
        logger.error(f"[{filename}] Error en transformación de coordenadas: {e}")
        data['COORD_EAST_M'] = None
        data['COORD_NORTH_M'] = None

    return data


def insert_incident(conn: sqlite3.Connection, data: dict) -> bool:
    """
    Inserta un incidente en la base de datos.
    Usa INSERT OR IGNORE para respetar la unicidad de NUM_INC.
    Retorna True si se insertó, False si era duplicado u ocurrió un error.
    """
    try:
        columns = ', '.join(data.keys())
        placeholders = ':' + ', :'.join(data.keys())
        query = f"INSERT OR IGNORE INTO incidentes ({columns}) VALUES ({placeholders})"
        cursor = conn.execute(query, data)
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


def main():
    raw_dir = os.path.join('data', 'raw')
    db_path = os.path.join('data', 'database', 'incidentes.db')

    # Verificar que los directorios requeridos existan
    if not os.path.isdir(raw_dir):
        logger.error(f"Directorio no encontrado: {raw_dir}")
        return

    # Inicializar base de datos (crea tabla si no existe)
    init_database(db_path)

    pdfs = sorted(f for f in os.listdir(raw_dir) if f.lower().endswith('.pdf'))
    if not pdfs:
        logger.warning(f"No se encontraron PDFs en {raw_dir}")
        return

    logger.info(f"Iniciando proceso. PDFs encontrados: {len(pdfs)}")

    insertados = 0
    omitidos = 0
    errores = 0

    # Context manager garantiza cierre de conexión incluso ante excepciones
    with sqlite3.connect(db_path) as conn:
        for filename in pdfs:
            path = os.path.join(raw_dir, filename)
            logger.info(f"Procesando: {filename}")

            data = process_pdf(path)
            if data is None:
                omitidos += 1
                continue

            if insert_incident(conn, data):
                insertados += 1
            else:
                errores += 1

        # Un único commit al finalizar todos los inserts (más eficiente)
        conn.commit()

    logger.info(
        f"Proceso finalizado — "
        f"Insertados: {insertados} | Omitidos: {omitidos} | Errores: {errores}"
    )


if __name__ == "__main__":
    main()