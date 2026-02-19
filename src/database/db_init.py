import sqlite3
import os

def create_database():
    # Definimos la ruta relativa para que funcione en cualquier PC
    db_path = os.path.join('data', 'database', 'incidentes.db')
    
    # Aseguramos que el directorio exista
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Creación de la tabla con validaciones técnicas (CHECKs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            NUM_INC TEXT UNIQUE NOT NULL,       -- ID del reporte (evita duplicados)
            AREA_CONCE TEXT NOT NULL,           -- El área manda en el nombre
            OPERADOR TEXT,                      -- YPF, Pluspetrol, etc.
            FECHA_MAIL TEXT,                    -- Formato dd-mm-yy
            VOL_D_m3 REAL,                      -- Volumen derramado
            AGUA REAL,                          -- % de agua
            SUELO_m2 REAL,                      -- Superficie afectada
            TIPO_EVENTO TEXT,                   -- Crudo, Agua de prod, etc.
            CAUSA_EVENT TEXT,                   -- Corrosión, falla mat, etc.
            RECURSO_AFECTADO TEXT,              -- Suelo, Cauce, etc.
            OBSERV TEXT,                        -- Descripción o notas
            X_COORD REAL,                       -- Longitud (Oeste)
            Y_COORD REAL,                       -- Latitud (Sur)
            MES TEXT,                           -- Mes para reportes rápidos
            EXPTE_ASOC TEXT,                    -- Expediente asociado
            FECHA_INF TEXT,                     -- Fecha de informe
            
            -- REGLAS DE INTEGRIDAD GEOGRÁFICA (Bounding Box Mendoza)
            CONSTRAINT coord_valida_lat CHECK (Y_COORD BETWEEN -38.0 AND -32.0),
            CONSTRAINT coord_valida_lon CHECK (X_COORD BETWEEN -70.0 AND -67.0)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Base de datos inicializada exitosamente en: {db_path}")

if __name__ == "__main__":
    create_database()