import sqlite3
import os

def create_database():
    # Definimos la ruta relativa para que funcione en cualquier PC
    db_path = os.path.join('data', 'database', 'incidentes.db')
    
    # Aseguramos que el directorio exista
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Eliminamos la tabla si existe para aplicar los nuevos cambios de columnas
    # Nota: Solo usar esto durante el desarrollo inicial
    cursor.execute('DROP TABLE IF EXISTS incidentes')

    # Creación de la tabla con validaciones técnicas (CHECKs)
    cursor.execute('''
        CREATE TABLE incidentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            NUM_INC TEXT UNIQUE NOT NULL,       -- [cite: 4, 28, 432]
            AREA_CONCE TEXT NOT NULL,           -- [cite: 6, 35, 434]
            OPERADOR TEXT,                      -- [cite: 5, 34, 434]
            FECHA_MAIL TEXT,                    -- Formato dd-mm-yy sugerido
            
            -- Datos de Magnitud e Infraestructura
            MAGNITUD TEXT,                      -- [cite: 9, 43, 434]
            INSTALACION TEXT,                   -- [cite: 7, 40, 434]
            
            -- Datos del Evento
            TIPO_EVENTO TEXT,                   -- [cite: 9, 41, 434]
            CAUSA_EVENT TEXT,                   -- [cite: 14, 42, 434]
            RECURSO_AFECTADO TEXT,              -- [cite: 16, 56, 440]
            
            -- Datos Cuantitativos
            VOL_D_m3 REAL,                      -- [cite: 15, 49, 438]
            AGUA REAL,                          -- [cite: 15, 50, 438]
            SUELO_m2 REAL,                      -- [cite: 16, 52, 440]
            
            -- Georreferenciación (WGS84 Decimal)
            X_COORD REAL,                       -- Longitud (W) 
            Y_COORD REAL,                       -- Latitud (S) 
            
            -- Coordenadas Cartesianas (Métricas UTM/GK)
            COORD_EAST_M REAL,                  -- Proyección Este (X metros)
            COORD_NORTH_M REAL,                 -- Proyección Norte (Y metros)
            SRID_ORIGEN TEXT,                   -- Sistema original del PDF
            
            -- Metadatos Administrativos
            OBSERV TEXT,                        -- [cite: 14, 45, 434]
            MES TEXT,                           -- Para agrupamiento rápido
            EXPTE_ASOC TEXT,                    -- Referencia administrativa
            FECHA_INF TEXT,                     -- Fecha del informe [cite: 2, 30, 434]
            
            -- REGLAS DE INTEGRIDAD GEOGRÁFICA (Bounding Box Mendoza)
            CONSTRAINT coord_valida_lat CHECK (Y_COORD BETWEEN -38.0 AND -32.0),
            CONSTRAINT coord_valida_lon CHECK (X_COORD BETWEEN -70.0 AND -67.0),
            CONSTRAINT magnitud_valida CHECK (MAGNITUD IN ('Menor', 'Intermedio', 'Mayor'))
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Base de datos verificada e inicializada exitosamente en: {db_path}")

if __name__ == "__main__":
    create_database()