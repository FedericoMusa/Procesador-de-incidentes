from pyproj import Transformer, CRS
import re

def gms_to_decimal(gms_str):
    """Convierte formatos como 33°11'24" a decimal negativo para Argentina."""
    parts = re.findall(r'\d+', gms_str)
    if len(parts) >= 3:
        # Grados + (Minutos/60) + (Segundos/3600)
        dec = float(parts[0]) + float(parts[1])/60 + float(parts[2])/3600
        return -dec
    return None

def transform_to_cartesian(lat, lon, zone=19):
    """
    Convierte WGS84 (Lat/Lon) a coordenadas planas UTM (Metros).
    Mendoza mayormente cae en la Zona 19S.
    """
    # Definimos la proyección de origen (WGS84) y destino (UTM 19S)
    crs_wgs84 = CRS.from_epsg(4326)
    crs_utm19s = CRS.from_epsg(32719)
    
    transformer = Transformer.from_crs(crs_wgs84, crs_utm19s, always_xy=True)
    easting, northing = transformer.transform(lon, lat)
    
    return easting, northing