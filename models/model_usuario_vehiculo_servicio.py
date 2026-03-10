from sqlalchemy import Column, Integer, Boolean, DateTime, Date, Time, ForeignKey, Enum
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.db import Base

class Solicitud(str, PyEnum):
    '''Estatus de solicitud'''
    Programa = "Programa"
    Proceso = "Proceso"
    Realizada = "Realizada"
    Cancelada = "Cancelada"

class ServicioVehiculo(Base):
    '''Modelo para la tabla de servicios por vehículo'''
    __tablename__ = "tbd_usuario_vehiculo_servicio"

    Id = Column(Integer, primary_key=True, index=True)
    cajero_Id = Column(Integer, ForeignKey("tbb_users.Id"))
    lavador_Id = Column(Integer, ForeignKey("tbb_users.Id"))
    servicio_Id = Column(Integer, ForeignKey("tbc_servicio.Id"))
    vehiculo_Id = Column(Integer, ForeignKey("tbb_vehiculo.Id"))

    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    descuento = Column(Integer, default=0)  # 👈 NUEVO CAMPO (porcentaje)
    estatus = Column(Enum(Solicitud), default=Solicitud.Programa)
    estado = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, onupdate=func.now())

    # Relaciones
    cajero_rel = relationship("User", foreign_keys=[cajero_Id], back_populates="cajero")
    lavador_rel = relationship("User", foreign_keys=[lavador_Id], back_populates="lavador")
    servicio = relationship("Servicio", back_populates="vehiculos_servicios")
    vehiculo = relationship("Vehiculo", back_populates="servicios")
    
    @property
    def precio_final(self):
        """Calcula el precio final después del descuento"""
        if self.servicio:
            descuento_aplicado = self.descuento or 0
            return self.servicio.costo * (1 - descuento_aplicado / 100)
        return 0