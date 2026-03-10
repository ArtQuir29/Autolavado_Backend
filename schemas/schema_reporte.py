from datetime import date, time
from pydantic import BaseModel, computed_field
from typing import Optional

class ReporteServicioResponse(BaseModel):
    # IDs
    servicio_id: int
    cajero_id: int
    lavador_id: int
    vehiculo_id: int
    
    # Nombres completos (ya concatenados)
    cajero_nombre_completo: str
    lavador_nombre_completo: str
    
    # Servicio
    servicio_nombre: str
    servicio_descripcion: Optional[str] = None
    servicio_costo: float
    duracion_minutos: int
    
    # Vehículo
    vehiculo_placas: str
    vehiculo_serie: Optional[str] = None
    vehiculo_modelo: str
    vehiculo_color: str
    vehiculo_descripcion: str = ""
    
    # Cita
    fecha: date
    hora: time
    descuento: int
    estatus: str
    
    # Cálculos
    @computed_field
    @property
    def costo_original(self) -> float:
        return self.servicio_costo
    
    @computed_field
    @property
    def precio_final(self) -> float:
        return round(self.servicio_costo * (1 - (self.descuento or 0) / 100), 2)
    
    @computed_field
    @property
    def descuento_formateado(self) -> str:
        return f"{self.descuento or 0}%"
    
    @computed_field
    @property
    def ahorro(self) -> float:
        return round(self.servicio_costo * (self.descuento or 0) / 100, 2)
    
    class Config:
        from_attributes = True

class ReporteResumenResponse(BaseModel):
    fecha: str
    total_servicios: int
    suma_costos_originales: float
    suma_precios_finales: float
    total_ahorrado: float
    promedio_descuento: float
    servicios_con_descuento: int