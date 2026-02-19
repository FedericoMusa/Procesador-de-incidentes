"""
Fixtures compartidos para los tests de extractores.
Los textos reproducen exactamente el contenido extraído por PyMuPDF
de los PDFs reales provistos.
"""

import pytest


@pytest.fixture
def ypf_text():
    return """Res. 24-04 / Dec. 437-93 / Res. 177-10
Comunicado Incidente Nº 0000246524
Informe Preliminar Mendoza
INFORME DEL INCIDENTE
Fecha de ocurrencia: 10/10/2025
Hora de ocurrencia: 10:00
Fecha de alta de registro: 10/10/2025
Operador: YPF S.A.
Unidad económica: NEN - NEGOCIO NORTE
Área operativa: PHM - PTO.HER-MOLINA
Yacimiento: DESFILADERO BAYO
Área concesionada: CHIHUIDO DE LA SIERRA NEGRA
Cuenca: NEUQUINA
Provincia: Mendoza
Tipo de permiso: Explotación
Instalación asociada: PLANTA AGUA DB NEUQUEN (TRASVASE DBY)
Nombre de la instalación: YPF.NQ.DB.A-3 (MARGINAL) / POZO INYECTOR
Tipo de instalación: CAÑERIA CONDUCCIÓN
Subtipo de instalación: Cañería conducción Agua
Subtipo de incidente: DERRAME DE AGUA DE PRODUCCIÓN
Tipo de evento causante: FALLA DE MATERIALES
Subtipo de evento causante: CORROSION
Magnitud del Incidente: Menor
Descripción: Se observa perdida en linea conducción pozo sumidero DB.X-3
INFORMACIÓN GEOGRÁFICA
Grados, minutos y decimales: Latitud (S): 37 ° / 20.936 ' Longitud (W): 69 ° / 3.204 '
Grados, minutos, segundos y decimales: Latitud (S): 37 ° / 20 ' / 56.2 '' Longitud (W): 69 ° / 3 ' / 12.2 ''
Grados y decimales: Latitud (S): 37.348933° Longitud (W): 69.053400°
VOLUMEN
Concentración de hidrocarburo (ppm): menor a 50
Volumen m3 derramado: 8.5000
% Agua contenido: 99.8000
Volumen m3 recuperado: 1.0000
ÁREA AFECTADA
Área m2: 1250.00
Recursos afectados: Suelo, Cauce aluvional
"""


@pytest.fixture
def petsud_text():
    return """N° DE COMUNICADO 562
Fecha de ocurrencia 12/2/2026
Hora de ocurrencia 15:00hs
Operador Petróleos Sudamericanos
Área operativa / concesión La Ventana
Yacimiento Punta de las Bardas
Cuenca Cuyana
Provincia Mendoza
Tipo de permiso Explotación
Instalación asociada Acueducto N°5 Pias 2-VM
Tipo de instalación cañería inyeccion PB-191
Subtipo de incidente Crudo
Tipo de evento causante Falla de Materiales - Corrosión
Magnitud del Incidente Menor
Descripción de la rotura y afectación
La perdida se produce en Cañería conduccion PB-191, afecta locacion de pozo con agua de formación y restos de sulfuro.
Coordenadas x (latitud - S) 33°30'57,62"
Coordenadas y (Longitud - O) 68°38'14,82"
Concentración de hidrocarburo (ppm) Menor a 50ppm
Volumen m3 derramado 7
% AGUA DERRAMADO 100
Volumen m3 recuperado 0
Área m2 200
Medidas adoptadas Se aplica el rol, se despresuriza cañería y se repara según procedimiento.
Suelo x
"""


@pytest.fixture
def pluspetrol_text():
    return """FECHA: 10/02/2026 HORA: 19:00 COMUNICADO N°: 06/26
EMPRESA: Pluspetrol S.A. CONCESION: JCP YACIMIENTO: JCP
OTROS: Satélite COHS-S2 CÓDIGO: DC_DR_0008_26
CONTINGENCIA: Interna: X Externa:
UBICACIÓN ESPECÍFICA: Satélite COHS-S2
COORDENADAS: X: 5858159 Y: 2552673 (Gauss-Krüger Faja 2 - Campo Inchauspe 69')
Long.: -68.4049142 Lat.: -37.4246588 (GS 84 Grados)
DESCRIPCIÓN: En recorrida habitual operador observa pitting en válvula reguladora de presión en línea de
control. Sin afectación a cauces permanentes y no permanentes. Vol. derramado: 0,015 m3(97 % agua de
producción). Volumen recuperado: 0 m3. Sup. Afectada: 0,5 m2. Suelo contaminado: A DETERMINAR.
"""


@pytest.fixture
def aconcagua_text():
    return """Informe de Incidente
Operador del Área PETROLERA ACONCAGUA ENERGIA S.A.
Nombre del área en recepción o Chañares Herrados
Nombre del yacimiento Chañares Herrados
Reponsable de la Instalación Singarella Darío
Fecha de Ocurrencia 08/09/2025
Hora de Ocurrencia 18:00
Tipo de Incidente
Detalle del incidente Se produce falla de material en cañería de conducción soterrada, de ERFV, sobre camino secundario
Tipo de instalación involucrada Pozo Productor
Subtipo de instalación involucrada CH-28
Tipo de evento causante
Subtipo del evento causante
Volumen de líquido derramado 1,50 m3
PPM 0,00 mg/lts
% de Agua 48,00 %
Volumen de gas 0,00 m3
Superficie aprox. afectada 50,00 m2
Volumen de fluido recuperado 0,00 m3
Latitud Decimal -33.3465
Longitud Decimal -68.9873
"""


@pytest.fixture
def pcr_text():
    return """Comunicado MDZ-21-2025- Batería 216 Fecha: 18-02-2026
Hora Estimada: 8:00hs
Hora de Detección: 8:30 hs
Empresa: Petroquimica Comodoro Rivadavia S.A (PCR)
Zona: Sector instalación Batería 216.
Concesión: El Sosneado
TIPO MAGNITUD
 BAJO MEDIO GRAVE (>10m3)
2- Derrames de hidrocarburos ■
Ubicación específica: Aproximadamente oleoducto de salida de calentador Batería 216.
Lat. S= 34°57´51,5" S
Long. O= 69°31´59,52" O
Descripción del accidente y su impacto:
Siendo las 8:30 hs aproximadamente, se detecta derrame de hidrocarburo, producto de una pinchadura en el oleoducto.
Superficie Afectada: El derrame afecta suelo dentro de la instalación de la batería. Aproximadamente se afectan unos 11 m2.
Medidas adoptadas: Se detuvo el bombeo del oleoducto, se gestionaron recursos e iniciaron las tareas de reparación y limpieza.
El tiempo estimado para superar la contingencia: 48 hs.
Volumen derramado neto de hidrocarburo: 1,1 m3. Con un 40 % de agua.
Volumen recuperado neto de hidrocarburo: 0 m3.
Responsable del comunicado: Sabrina Estegui
"""
