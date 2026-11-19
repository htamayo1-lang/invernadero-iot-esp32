@echo off
REM Abre la interfaz del invernadero (se ejecuta en el PC, no se sube al ESP32).
chcp 65001 >nul
set PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
cd /d "%~dp0"

"%PY%" -c "import flet, paho.mqtt" 2>nul || (
    echo Instalando librerias de la app...
    "%PY%" -m pip install -r requirements.txt
)
"%PY%" app_simple.py
