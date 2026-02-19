## Procesador de Incidentes Ambientales - Oil & Gas Mendoza
Este proyecto automatiza la extracción de datos desde planillas de incidentes (PDF) de operadoras como YPF, Pluspetrol y Petróleos Sudamericanos. El objetivo es consolidar la información en una base de datos local SQLite, validando técnicamente las coordenadas y volúmenes para su posterior análisis.
+4

# 🛠 Requisitos y Entorno
  .   Python 3.10+

  . No requiere conexión a internet para su funcionamiento (local-first).

  . No requiere Docker (optimizado para PCs de bajos recursos).
# 📂 Estructura del Proyecto
```
incidents_processor/
├── data/
│   ├── raw/                # PDFs a procesar (ej. Comunicado N° 06/26)
│   └── database/           # Base de datos local (incidentes.db)
├── src/
│   ├── extractors/         # Lógica por operadora (ypf.py, pluspetrol.py, petsud.py)
│   ├── transformation/     # Conversión de coordenadas y normalización de fechas
│   └── main.py             # Ejecutor principal
├── requirements.txt        # Librerías (PyMuPDF, Pandas, PyProj)
└── README.md               
```
# 📊 Mapeo de Datos y Validación

El sistema normaliza los datos de entrada a un esquema unificado:
  . Área Concesionada: Se extrae el nombre del área operativa (ej. "JCP", "La Ventana" o "CHIHUIDO DE LA SIERRA NEGRA") como identificador principal.
  . Fechas: Formato estandarizado dd-mm-yy (Argentina).
  . Georreferenciación: Conversión automática a grados decimales (WGS84).
  . Validación: Se bloquean registros con Latitud fuera de [-38.0, -32.0] o Longitud fuera de [-70.0, -67.0] para asegurar que el incidente esté dentro de Mendoza.
# 🚀 Uso Rápido

1.  Instalación de dependencias:

  pip install -r requirements.txt

2. Carga de datos:
   
   Colocar los PDFs en data/raw/ y ejecutar:
   python src/main.py
# ⚠️ Reglas de Integridad
  1. Cero Duplicados: El campo NUM-INC es único. Si un informe ya fue procesado, el sistema lo ignorará.


  2. Consistencia de Volúmenes: Se verifica que el volumen recuperado no sea superior al derramado.
    
  4. Check de Coordenadas: Un número mal puesto que traslade el pozo fuera de la cuenca será detectado y rechazado por la base de datos.
