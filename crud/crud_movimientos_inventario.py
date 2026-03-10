from sqlalchemy.orm import Session
from models.modelMovimientosInventario import MovimientoInventario
from schemas import schema_movimientos_inventario
from crud.crud_productos import actualizar_stock, get_producto
from fastapi import HTTPException

def get_movimientos(db: Session, skip: int = 0, limit: int = 100):
    '''Obtener todos los movimientos'''
    return db.query(MovimientoInventario).order_by(
        MovimientoInventario.fecha_registro.desc()
    ).offset(skip).limit(limit).all()

def get_movimiento(db: Session, movimiento_id: int):
    '''Obtener un movimiento por ID'''
    return db.query(MovimientoInventario).filter(
        MovimientoInventario.Id == movimiento_id
    ).first()

def get_movimientos_by_producto(db: Session, producto_id: int, skip: int = 0, limit: int = 100):
    '''Obtener movimientos de un producto específico'''
    return db.query(MovimientoInventario).filter(
        MovimientoInventario.producto_Id == producto_id
    ).order_by(
        MovimientoInventario.fecha_registro.desc()
    ).offset(skip).limit(limit).all()

def create_movimiento(db: Session, movimiento: schema_movimientos_inventario.MovimientoInventarioCreate):
    '''
    Crear un nuevo movimiento y actualizar el stock del producto
    '''
    # Verificar que el producto existe
    producto = get_producto(db, movimiento.producto_Id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Para salidas, verificar stock suficiente
    if movimiento.tipo == "Salida" and producto.stock_actual < movimiento.cantidad:
        raise HTTPException(
            status_code=400, 
            detail=f"Stock insuficiente. Disponible: {producto.stock_actual}"
        )
    
    # 1. Crear el movimiento
    db_movimiento = MovimientoInventario(**movimiento.model_dump())
    db.add(db_movimiento)
    db.flush()  # Para obtener el ID sin commit aún
    
    # 2. Actualizar el stock del producto
    stock_actualizado = actualizar_stock(
        db, 
        movimiento.producto_Id, 
        movimiento.cantidad, 
        movimiento.tipo
    )
    
    if not stock_actualizado and movimiento.tipo == "Salida":
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al actualizar stock")
    
    # 3. Commit de ambas operaciones
    db.commit()
    db.refresh(db_movimiento)
    
    return db_movimiento

def delete_movimiento(db: Session, movimiento_id: int):
    '''Eliminar un movimiento (NO RECOMENDADO)'''
    db_movimiento = get_movimiento(db, movimiento_id)
    if db_movimiento:
        db.delete(db_movimiento)
        db.commit()
    return db_movimiento