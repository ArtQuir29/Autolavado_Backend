from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Optional
from datetime import date
import config.db
from crud import crud_usuario_vehiculo_servicio
from schemas import schema_usuario_vehiculo_servicio
from config.security import get_current_user
from models.modelUser import User
from models.modelServicio import Servicio
from models.modelVehiculos import Vehiculo
from models.model_usuario_vehiculo_servicio import ServicioVehiculo

servicio_vehiculo_router = APIRouter(prefix="/servicios-vehiculo", tags=["Servicios por Vehículo"])

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Esquema para la respuesta personalizada
class ServicioVehiculoDetalle(schema_usuario_vehiculo_servicio.UsuarioVehiculoServicio):
    cajero_nombre_completo: Optional[str] = None
    lavador_nombre_completo: Optional[str] = None
    servicio_nombre: Optional[str] = None
    servicio_costo: Optional[float] = None
    servicio_descripcion: Optional[str] = None
    vehiculo_placas: Optional[str] = None
    vehiculo_marca: Optional[str] = None
    vehiculo_modelo: Optional[str] = None
    vehiculo_color: Optional[str] = None
    motivo: Optional[str] = None
    color_atendido: Optional[str] = None

# NUEVO ENDPOINT: GET por fecha con todos los detalles
@servicio_vehiculo_router.get("/por-fecha/", response_model=List[ServicioVehiculoDetalle])
async def get_servicios_por_fecha(
    fecha: date = Query(..., description="Fecha a consultar (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''
    Obtiene todos los servicios para una fecha específica con detalles completos:
    - Cajero: nombre completo
    - Lavador: nombre completo
    - Servicio: nombre, costo, descripción
    - Vehículo: placas, marca, modelo, color
    - Motivo y color
    '''
    
    # Consulta con joins para obtener todos los datos relacionados
    resultados = db.query(
        ServicioVehiculo,
        User.Id.label('cajero_id'),
        User.nombre.label('cajero_nombre'),
        User.papellido.label('cajero_papellido'),
        User.sapellido.label('cajero_sapellido'),
        User2.nombre.label('lavador_nombre'),
        User2.papellido.label('lavador_papellido'),
        User2.sapellido.label('lavador_sapellido'),
        Servicio.nombre.label('servicio_nombre'),
        Servicio.costo.label('servicio_costo'),
        Servicio.descripcion.label('servicio_descripcion'),
        Vehiculo.placa.label('vehiculo_placa'),
        Vehiculo.marca.label('vehiculo_marca'),
        Vehiculo.modelo.label('vehiculo_modelo'),
        Vehiculo.color.label('vehiculo_color')
    ).join(
        User, User.Id == ServicioVehiculo.cajero_Id
    ).join(
        User2, User2.Id == ServicioVehiculo.lavador_Id
    ).join(
        Servicio, Servicio.Id == ServicioVehiculo.servicio_Id
    ).join(
        Vehiculo, Vehiculo.Id == ServicioVehiculo.vehiculo_Id
    ).filter(
        ServicioVehiculo.fecha == fecha
    ).all()
    
    # Transformar resultados al formato deseado
    response = []
    for r in resultados:
        item = {
            # Datos básicos del servicio
            "Id": r[0].Id,
            "cajero_Id": r[0].cajero_Id,
            "lavador_Id": r[0].lavador_Id,
            "servicio_Id": r[0].servicio_Id,
            "vehiculo_Id": r[0].vehiculo_Id,
            "fecha": r[0].fecha,
            "hora": r[0].hora,
            "estatus": r[0].estatus,
            "estado": r[0].estado,
            "fecha_registro": r[0].fecha_registro,
            "fecha_actualizacion": r[0].fecha_actualizacion,
            "motivo": r[0].motivo,
            "color_atendido": r[0].color_vehiculo,
            
            # Campos calculados/enriquecidos
            "cajero_nombre_completo": f"{r.cajero_nombre} {r.cajero_papellido} {r.cajero_sapellido or ''}".strip(),
            "lavador_nombre_completo": f"{r.lavador_nombre} {r.lavador_papellido} {r.lavador_sapellido or ''}".strip(),
            "servicio_nombre": r.servicio_nombre,
            "servicio_costo": r.servicio_costo,
            "servicio_descripcion": r.servicio_descripcion,
            "vehiculo_placas": r.vehiculo_placa,
            "vehiculo_marca": r.vehiculo_marca,
            "vehiculo_modelo": r.vehiculo_modelo,
            "vehiculo_color": r.vehiculo_color
        }
        response.append(item)
    
    return response

# Mantener los endpoints existentes
@servicio_vehiculo_router.get("/", response_model=List[schema_usuario_vehiculo_servicio.UsuarioVehiculoServicio])
async def read_servicios_vehiculo(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Obtener todos los servicios de vehículos'''
    servicios = crud_usuario_vehiculo_servicio.get_servicios_vehiculo(db=db, skip=skip, limit=limit)
    return servicios

@servicio_vehiculo_router.get("/{servicio_id}", response_model=schema_usuario_vehiculo_servicio.UsuarioVehiculoServicio)
async def read_servicio_vehiculo(
    servicio_id: int, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Obtener un servicio de vehículo por ID'''
    db_servicio = crud_usuario_vehiculo_servicio.get_servicio_vehiculo(db=db, servicio_id=servicio_id)
    if db_servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return db_servicio

# Endpoints existentes para filtrar...
@servicio_vehiculo_router.get("/vehiculo/{vehiculo_id}", response_model=List[schema_usuario_vehiculo_servicio.UsuarioVehiculoServicio])
async def read_servicios_by_vehiculo(
    vehiculo_id: int, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Obtener servicios por vehículo'''
    servicios = crud_usuario_vehiculo_servicio.get_servicios_by_vehiculo(db=db, vehiculo_id=vehiculo_id)
    return servicios

@servicio_vehiculo_router.get("/lavador/{lavador_id}", response_model=List[schema_usuario_vehiculo_servicio.UsuarioVehiculoServicio])
async def read_servicios_by_lavador(
    lavador_id: int, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Obtener servicios por lavador'''
    servicios = crud_usuario_vehiculo_servicio.get_servicios_by_lavador(db=db, lavador_id=lavador_id)
    return servicios

@servicio_vehiculo_router.get("/cajero/{cajero_id}", response_model=List[schema_usuario_vehiculo_servicio.UsuarioVehiculoServicio])
async def read_servicios_by_cajero(
    cajero_id: int, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Obtener servicios por cajero'''
    servicios = crud_usuario_vehiculo_servicio.get_servicios_by_cajero(db=db, cajero_id=cajero_id)
    return servicios

# Endpoint POST actualizado para incluir motivo y color
@servicio_vehiculo_router.post("/", response_model=schema_usuario_vehiculo_servicio.UsuarioVehiculoServicio, status_code=status.HTTP_201_CREATED)
async def create_servicio_vehiculo(
    servicio: schema_usuario_vehiculo_servicio.UsuarioVehiculoServicioCreate, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Crear un nuevo servicio de vehículo'''
    return crud_usuario_vehiculo_servicio.create_servicio_vehiculo(db=db, servicio=servicio)

@servicio_vehiculo_router.put("/{servicio_id}", response_model=schema_usuario_vehiculo_servicio.UsuarioVehiculoServicio)
async def update_servicio_vehiculo(
    servicio_id: int, 
    servicio: schema_usuario_vehiculo_servicio.UsuarioVehiculoServicioUpdate, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Actualizar un servicio de vehículo existente'''
    db_servicio = crud_usuario_vehiculo_servicio.update_servicio_vehiculo(
        db=db, servicio_id=servicio_id, servicio=servicio
    )
    if db_servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return db_servicio

@servicio_vehiculo_router.delete("/{servicio_id}")
async def delete_servicio_vehiculo(
    servicio_id: int, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    '''Eliminar un servicio de vehículo por ID'''
    db_servicio = crud_usuario_vehiculo_servicio.delete_servicio_vehiculo(db=db, servicio_id=servicio_id)
    if db_servicio is None:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return {"message": "Servicio eliminado exitosamente"}