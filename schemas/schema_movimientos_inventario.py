from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from models.modelMovimientosInventario import TipoMovimiento

class MovimientoInventarioBase(BaseModel):
    '''Esquema base para movimientos'''
    producto_Id: int
    tipo: TipoMovimiento
    cantidad: int = Field(..., gt=0)

class MovimientoInventarioCreate(MovimientoInventarioBase):
    '''Esquema para crear movimiento'''
    pass

class MovimientoInventario(MovimientoInventarioBase):
    '''Esquema para respuesta de movimiento'''
    Id: int
    fecha_registro: datetime
    fecha_actualizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True