from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session, aliased
from typing import List, Optional
from datetime import date
import config.db
from models.model_usuario_vehiculo_servicio import ServicioVehiculo
from models.modelUser import User
from models.modelServicio import Servicio
from models.modelVehiculos import Vehiculo
from schemas.schema_reporte import ReporteServicioResponse, ReporteResumenResponse
from config.security import get_current_user

reportes_router = APIRouter(prefix="/reportes", tags=["Reportes"])

def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@reportes_router.get("/servicios/", response_model=List[ReporteServicioResponse])
async def get_reporte_servicios(
    fecha: Optional[date] = Query(None, description="Filtrar por fecha (opcional)"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Obtiene todos los servicios con detalles completos
    """
    try:
        # Crear alias para las relaciones
        Cajero = aliased(User)
        Lavador = aliased(User)
        
        # Construir la consulta
        query = db.query(
            ServicioVehiculo,
            Cajero,
            Lavador,
            Servicio,
            Vehiculo
        ).join(
            Cajero, Cajero.Id == ServicioVehiculo.cajero_Id
        ).join(
            Lavador, Lavador.Id == ServicioVehiculo.lavador_Id
        ).join(
            Servicio, Servicio.Id == ServicioVehiculo.servicio_Id
        ).join(
            Vehiculo, Vehiculo.Id == ServicioVehiculo.vehiculo_Id
        )
        
        # Aplicar filtro por fecha si se proporciona
        if fecha:
            query = query.filter(ServicioVehiculo.fecha == fecha)
        
        # Ordenar
        query = query.order_by(ServicioVehiculo.fecha.desc(), ServicioVehiculo.hora)
        
        # Ejecutar
        resultados = query.all()
        
        # Transformar resultados
        response = []
        for uvs, cajero, lavador, servicio, vehiculo in resultados:
            # Construir nombres completos
            cajero_completo = f"{cajero.nombre or ''} {cajero.papellido or ''}".strip()
            if cajero.sapellido:
                cajero_completo += f" {cajero.sapellido}"
                
            lavador_completo = f"{lavador.nombre or ''} {lavador.papellido or ''}".strip()
            if lavador.sapellido:
                lavador_completo += f" {lavador.sapellido}"
            
            # Descripción del vehículo
            partes_vehiculo = []
            if vehiculo.modelo:
                partes_vehiculo.append(vehiculo.modelo)
            if vehiculo.color:
                partes_vehiculo.append(vehiculo.color)
            if hasattr(vehiculo, 'tipo') and vehiculo.tipo:
                partes_vehiculo.insert(0, vehiculo.tipo)
            
            vehiculo_descripcion = " ".join(partes_vehiculo) if partes_vehiculo else "Sin descripción"
            
            response.append(ReporteServicioResponse(
                # IDs
                servicio_id=uvs.Id,
                cajero_id=uvs.cajero_Id,
                lavador_id=uvs.lavador_Id,
                vehiculo_id=uvs.vehiculo_Id,
                
                # Nombres completos (solo esto)
                cajero_nombre_completo=cajero_completo,
                lavador_nombre_completo=lavador_completo,
                
                # Servicio
                servicio_nombre=servicio.nombre or '',
                servicio_descripcion=servicio.descripcion,
                servicio_costo=float(servicio.costo) if servicio.costo else 0,
                duracion_minutos=servicio.duracion_minutos or 0,
                
                # Vehículo
                vehiculo_placas=vehiculo.placa or '',
                vehiculo_serie=vehiculo.serie or '',
                vehiculo_modelo=vehiculo.modelo or '',
                vehiculo_color=vehiculo.color or '',
                vehiculo_descripcion=vehiculo_descripcion,
                
                # Cita
                fecha=uvs.fecha,
                hora=uvs.hora,
                descuento=uvs.descuento or 0,
                estatus=uvs.estatus or ''
            ))
        
        return response
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener reporte: {str(e)}")