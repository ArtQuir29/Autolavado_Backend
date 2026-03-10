from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.db import Base
import enum

class TipoMovimiento(str, enum.Enum):
    ENTRADA = "Entrada"
    SALIDA = "Salida"

class MovimientoInventario(Base):
    '''Modelo para la tabla de movimientos de inventario'''
    __tablename__ = "tbd_movimientos_inventario"
    
    Id = Column(Integer, primary_key=True, index=True)
    producto_Id = Column(Integer, ForeignKey("tbc_productos.Id"), nullable=False)
    tipo = Column(Enum(TipoMovimiento), nullable=False)  # Entrada o Salida
    cantidad = Column(Integer, nullable=False)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, onupdate=func.now())  # Cambiado a fecha_actualizacion
    
    # Relación
    producto = relationship("Producto", back_populates="movimientos")