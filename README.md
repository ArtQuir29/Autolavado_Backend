# autolavadoBackend

# Esto crea una carpeta llamada venv con el entorno virtual
python -m venv venv

# Iniciar la API (modo desarrollo con recarga automática)
uvicorn main:app --reload

# Iniciar en un puerto específico
uvicorn main:app --reload --port 8000

# Iniciar con más detalles (debug)
uvicorn main:app --reload --log-level debug

# Probar en navegador
http://localhost:8000/docs

# Detener la API (cuando está corriendo)
Ctrl + C

# Windows - Activar
venv\Scripts\activate
.venv\Scripts\activate

# Windows - Desactivar
deactivate

# Instalar todo desde requirements.txt
pip install -r requirements.txt

# Instalar un paquete específico
pip install fastapi
pip install pymysql

# Ver paquetes instalados
pip list

# Analizar un archivo específico
pylint routes/routes_productos.py

# Analizar una carpeta completa
pylint routes/
pylint crud/
pylint models/

# Analizar todo el proyecto
pylint routes/ crud/ models/ schemas/ config/

# Con formato detallado
pylint routes/ -ry

# Solo errores (sin warnings)
pylint routes/ --errors-only

# Generar reporte HTML
pylint routes/ --output-format=html > pylint_report.html

# Usar archivo de configuración
pylint --rcfile=.pylintrc routes/

# Ver estado
git status

# Agregar archivos
git add .
git add archivo.py

# Hacer commit
git commit -m "mensaje"

# Subir cambios
git push

# Bajar cambios
git pull

# Ver historial
git log --oneline