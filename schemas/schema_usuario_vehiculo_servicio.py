from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from models.model_usuario_vehiculo_servicio import Solicitud

class UsuarioVehiculoServicioBase(BaseModel):
    '''Esquema base para servicios de vehículos'''
    cajero_Id: int
    lavador_Id: int
    servicio_Id: int
    vehiculo_Id: int
    fecha: date
    hora: time
    descuento: Optional[int] = Field(0, ge=0, le=100)  # 👈 NUEVO CAMPO
    estatus: Solicitud = Solicitud.Programa
    estado: bool = True

    @field_validator("hora", mode="before")
    @classmethod
    def limpiar_zona_horaria(cls, value):
        if isinstance(value, str):
            if value.endswith("Z"):
                value = value.replace("Z", "")
            if "+" in value:
                value = value.split("+")[0]
        return value

class UsuarioVehiculoServicioCreate(UsuarioVehiculoServicioBase):
    '''Esquema para crear servicio de vehículo'''
    pass

class UsuarioVehiculoServicioUpdate(BaseModel):
    '''Esquema para actualizar servicio de vehículo'''
    cajero_Id: Optional[int] = None
    lavador_Id: Optional[int] = None
    servicio_Id: Optional[int] = None
    vehiculo_Id: Optional[int] = None
    fecha: Optional[date] = None
    hora: Optional[time] = None
    descuento: Optional[int] = Field(None, ge=0, le=100)  # 👈 NUEVO CAMPO
    estatus: Optional[Solicitud] = None
    estado: Optional[bool] = None

class UsuarioVehiculoServicio(UsuarioVehiculoServicioBase):
    '''Esquema para respuesta de servicio de vehículo'''
    Id: int
    fecha_registro: datetime
    fecha_actualizacion: Optional[datetime] = None
    
    @property
    def precio_final(self) -> float:
        """Calcula el precio final con descuento"""
        # Este valor se llenará desde la relación en la BD
        return 0.0

    class Config:
        from_attributes = True