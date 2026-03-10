from sqlalchemy.orm import Session
from models.modelProductos import Producto
from schemas import schema_productos

def get_productos(db: Session, skip: int = 0, limit: int = 100):
    '''Obtener todos los productos'''
    return db.query(Producto).offset(skip).limit(limit).all()

def get_producto(db: Session, producto_id: int):
    '''Obtener un producto por ID'''
    return db.query(Producto).filter(Producto.Id == producto_id).first()

def get_producto_by_nombre(db: Session, nombre: str):
    '''Obtener producto por nombre'''
    return db.query(Producto).filter(Producto.nombre == nombre).first()

def get_productos_bajo_stock(db: Session):
    '''Obtener productos con stock por debajo del mínimo'''
    return db.query(Producto).filter(Producto.stock_actual < Producto.stock_minimo).all()

def create_producto(db: Session, producto: schema_productos.ProductoCreate):
    '''Crear un nuevo producto'''
    db_producto = Producto(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

def update_producto(db: Session, producto_id: int, producto: schema_productos.ProductoUpdate):
    '''Actualizar un producto existente'''
    db_producto = get_producto(db, producto_id)
    if db_producto:
        update_data = producto.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_producto, key, value)
        db.commit()
        db.refresh(db_producto)
    return db_producto

def actualizar_stock(db: Session, producto_id: int, cantidad: int, tipo: str):
    '''
    Actualizar stock del producto
    tipo: "Entrada" (suma) o "Salida" (resta)
    '''
    db_producto = get_producto(db, producto_id)
    if not db_producto:
        return None
    
    if tipo == "Entrada":
        db_producto.stock_actual += cantidad
    elif tipo == "Salida":
        # Verificar stock suficiente
        if db_producto.stock_actual < cantidad:
            return None  # Stock insuficiente
        db_producto.stock_actual -= cantidad
    
    db.commit()
    db.refresh(db_producto)
    return db_producto

def delete_producto(db: Session, producto_id: int):
    '''Eliminar un producto por ID'''
    db_producto = get_producto(db, producto_id)
    if db_producto:
        db.delete(db_producto)
        db.commit()
    return db_producto