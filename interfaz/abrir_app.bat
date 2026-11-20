@echo off
chcp 65001 >nul
set PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
cd /d "%~dp0"

"%PY%" -c "import paho.mqtt" 2>nul || (
    echo Instalando paho-mqtt para el modo ESP32 por MQTT...
    "%PY%" -m pip install -r requirements.txt
)
"%PY%" app.py
