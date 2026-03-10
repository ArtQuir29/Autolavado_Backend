from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import config.db
from crud import crud_movimientos_inventario, crud_productos
from schemas import schema_movimientos_inventario
from config.security import get_current_user

movimiento_router = APIRouter(prefix="/movimientos-inventario", tags=["Movimientos de Inventario"])

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@movimiento_router.get("/", response_model=List[schema_movimientos_inventario.MovimientoInventario])
async def get_movimientos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Obtiene todos los movimientos'''
    return crud_movimientos_inventario.get_movimientos(db, skip, limit)

@movimiento_router.get("/producto/{producto_id}", response_model=List[schema_movimientos_inventario.MovimientoInventario])
async def get_movimientos_by_producto(
    producto_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Obtiene movimientos de un producto específico'''
    producto = crud_productos.get_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return crud_movimientos_inventario.get_movimientos_by_producto(db, producto_id, skip, limit)

@movimiento_router.get("/fecha/{fecha}", response_model=List[schema_movimientos_inventario.MovimientoInventario])
async def get_movimientos_by_fecha(
    fecha: date,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Obtiene movimientos de una fecha específica'''
    # Nota: Esto filtra por fecha_registro (día)
    return db.query(MovimientoInventario).filter(
        db.func.date(MovimientoInventario.fecha_registro) == fecha
    ).all()

@movimiento_router.post("/", response_model=schema_movimientos_inventario.MovimientoInventario, status_code=status.HTTP_201_CREATED)
async def create_movimiento(
    movimiento: schema_movimientos_inventario.MovimientoInventarioCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''
    Crea un movimiento (entrada/salida) y actualiza el stock del producto automáticamente
    '''
    return crud_movimientos_inventario.create_movimiento(db, movimiento)

@movimiento_router.get("/resumen/diario")
async def get_resumen_diario(
    fecha: Optional[date] = Query(None, description="Fecha para resumen"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Obtiene resumen de movimientos del día'''
    fecha_consulta = fecha or date.today()
    movimientos = db.query(MovimientoInventario).filter(
        db.func.date(MovimientoInventario.fecha_registro) == fecha_consulta
    ).all()
    
    entradas = sum(m.cantidad for m in movimientos if m.tipo == "Entrada")
    salidas = sum(m.cantidad for m in movimientos if m.tipo == "Salida")
    
    return {
        "fecha": fecha_consulta.isoformat(),
        "total_movimientos": len(movimientos),
        "total_entradas": entradas,
        "total_salidas": salidas,
        "balance": entradas - salidas
    }