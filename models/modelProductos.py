from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.db import Base

class Producto(Base):
    '''Modelo para la tabla de productos'''
    __tablename__ = "tbc_productos"
    
    Id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(200))
    categoria = Column(String(50))
    unidad_medida = Column(String(20), nullable=False, default="Pieza")
    stock_actual = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=0)
    precio_compra = Column(Float, nullable=False)
    estado = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, onupdate=func.now())  # Cambiado a fecha_actualizacion
    
    # Relación con movimientos
    movimientos = relationship("MovimientoInventario", back_populates="producto")