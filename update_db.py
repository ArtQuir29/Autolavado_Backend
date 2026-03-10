from config.db import engine, Base
from models.modelProductos import Producto
from models.modelMovimientosInventario import MovimientoInventario
from models.modelUser import User
from models.modelRols import Rols
from models.modelServicio import Servicio
from models.modelVehiculos import Vehiculo
from models.model_usuario_vehiculo_servicio import ServicioVehiculo
from sqlalchemy import inspect, text
import time

def verificar_tablas_existentes():
    """Verifica qué tablas ya existen"""
    inspector = inspect(engine)
    return set(inspector.get_table_names())

def crear_tablas():
    print("="*60)
    print("🔄 ACTUALIZANDO BASE DE DATOS")
    print("="*60)
    
    # Verificar tablas antes
    tablas_antes = verificar_tablas_existentes()
    print(f"\n📊 Tablas existentes: {len(tablas_antes)}")
    for tabla in sorted(tablas_antes):
        print(f"   ✅ {tabla}")
    
    # Tablas que se crearán
    tablas_modelo = {table.name for table in Base.metadata.sorted_tables}
    tablas_nuevas = tablas_modelo - tablas_antes
    
    print(f"\n🆕 Tablas nuevas a crear: {len(tablas_nuevas)}")
    for tabla in sorted(tablas_nuevas):
        print(f"   ➕ {tabla}")
    
    if not tablas_nuevas:
        print("\n✨ No hay tablas nuevas que crear")
        print("✅ Base de datos ya está actualizada")
        return
    
    # Preguntar antes de crear
    respuesta = input("\n¿Deseas crear las nuevas tablas? (s/n): ")
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        return
    
    # Crear tablas
    print("\n⚙️ Creando nuevas tablas...")
    inicio = time.time()
    
    try:
        Base.metadata.create_all(bind=engine)
        tiempo = time.time() - inicio
        
        # Verificar después
        tablas_despues = verificar_tablas_existentes()
        creadas = tablas_despues - tablas_antes
        
        print(f"✅ {len(creadas)} tablas creadas en {tiempo:.2f} segundos")
        for tabla in sorted(creadas):
            print(f"   ✅ {tabla}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return
    
    print("\n" + "="*60)
    print("✅ BASE DE DATOS ACTUALIZADA EXITOSAMENTE")
    print("="*60)

def ver_estructura_tabla(tabla_nombre):
    """Ver estructura de una tabla específica"""
    inspector = inspect(engine)
    if tabla_nombre in inspector.get_table_names():
        print(f"\n📋 Estructura de {tabla_nombre}:")
        for columna in inspector.get_columns(tabla_nombre):
            print(f"   - {columna['name']}: {columna['type']}")
    else:
        print(f"❌ La tabla {tabla_nombre} no existe")

if __name__ == "__main__":
    crear_tablas()
    
    # Opcional: ver estructura de tablas nuevas
    print("\n" + "="*60)
    respuesta = input("¿Ver estructura de tablas? (s/n): ")
    if respuesta.lower() == 's':
        ver_estructura_tabla("tbc_productos")
        ver_estructura_tabla("tbd_movimientos_inventario")