from abc import ABC, abstractmethod
from datetime import datetime
from src.transformation.coordinates import transform_to_cartesian

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, text):
        pass

    def normalize_date(self, date_str):
        # Maneja formatos d/m/y o d-m-y y devuelve dd-mm-yy
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"):
            try:
                return datetime.strptime(date_str.strip(), fmt).strftime('%d-%m-%y')
            except ValueError:
                continue
        return date_str

    def calculate_net_hydrocarbon(self, total_vol, water_pct):
        # Asegura que siempre tengamos el dato neto si valoras la integridad
        return round(float(total_vol) * (1 - (float(water_pct) / 100)), 4)