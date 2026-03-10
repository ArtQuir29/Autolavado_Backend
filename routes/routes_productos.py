from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
import config.db
from crud import crud_productos
from schemas import schema_productos
from config.security import get_current_user

producto_router = APIRouter(prefix="/productos", tags=["Productos"])

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@producto_router.get("/", response_model=List[schema_productos.Producto])
async def get_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Obtiene todos los productos'''
    return crud_productos.get_productos(db, skip, limit)

@producto_router.get("/bajo-stock/", response_model=List[schema_productos.Producto])
async def get_productos_bajo_stock(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Obtiene productos con stock por debajo del mínimo'''
    return crud_productos.get_productos_bajo_stock(db)

@producto_router.get("/{producto_id}", response_model=schema_productos.Producto)
async def get_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Obtiene un producto por ID'''
    db_producto = crud_productos.get_producto(db, producto_id)
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto

@producto_router.post("/", response_model=schema_productos.Producto, status_code=status.HTTP_201_CREATED)
async def create_producto(
    producto: schema_productos.ProductoCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Crea un nuevo producto'''
    existe = crud_productos.get_producto_by_nombre(db, producto.nombre)
    if existe:
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese nombre")
    
    return crud_productos.create_producto(db, producto)

@producto_router.put("/{producto_id}", response_model=schema_productos.Producto)
async def update_producto(
    producto_id: int,
    producto: schema_productos.ProductoUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Actualiza un producto existente'''
    db_producto = crud_productos.update_producto(db, producto_id, producto)
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return db_producto