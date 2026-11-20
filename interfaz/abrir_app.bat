@echo off
cd /d "%~dp0"
set PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe

"%PY%" -c "import paho.mqtt" 2>nul || "%PY%" -m pip install -r requirements.txt
"%PY%" app.py
