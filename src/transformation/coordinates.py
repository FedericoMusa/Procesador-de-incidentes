from pyproj import Transformer, CRS
import re

def gms_to_decimal(gms_str):
    """
    Convierte GMS (Grados, Minutos, Segundos) a decimal negativo (Hemisferio Sur/Oeste).
    Ejemplo: "33° 11' 24\"" -> -33.19
    """
    if not gms_str:
        return None
    # Extrae todos los números, incluyendo decimales en los segundos
    parts = re.findall(r"[-+]?\d*\.\d+|\d+", gms_str)
    if len(parts) >= 3:
        degrees = float(parts[0])
        minutes = float(parts[1])
        seconds = float(parts[2])
        decimal = degrees + (minutes / 60) + (seconds / 3600)
        return -abs(decimal) # Fuerza negativo para Argentina
    return None

def gk_to_decimal(x_gk, y_gk, faja=2):
    """
    Convierte coordenadas Gauss-Krüger (Campo Inchauspe 69) a WGS84 Decimal.
    Pluspetrol usa Faja 2.
    """
    # Definición de EPSG para Campo Inchauspe Faja 2 (Argentina)
    epsg_gk2 = f"epsg:2218{faja}" 
    transformer = Transformer.from_crs(epsg_gk2, "epsg:4326", always_xy=True)
    lon, lat = transformer.transform(x_gk, y_gk)
    return lat, lon

def transform_to_cartesian(lat, lon, epsg_destino=32719):
    """
    Convierte WGS84 a UTM (metros). 
    Mendoza usa mayormente UTM Zona 19S (EPSG: 32719).
    """
    if lat is None or lon is None:
        return None, None
        
    transformer = Transformer.from_crs("epsg:4326", f"epsg:{epsg_destino}", always_xy=True)
    easting, northing = transformer.transform(lon, lat)
    
    return round(easting, 2), round(northing, 2)