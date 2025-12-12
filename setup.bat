@echo off
echo [INFO] Creando entorno virtual...
python -m venv venv

echo [INFO] Activando entorno...
call venv\Scripts\activate

echo [INFO] Actualizando pip...
python -m pip install --upgrade pip

echo [INFO] Instalando dependencias...
pip install -r requirements.txt

echo [INFO] Setup completo. Para iniciar:
echo call venv\Scripts\activate
echo uvicorn app.main:app --reload
pause
