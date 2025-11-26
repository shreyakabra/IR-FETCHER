@echo off
echo Stopping existing server...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *run.py*" 2>nul
timeout /t 2 /nobreak >nul
echo Starting server with auto-reload...
cd /d "%~dp0"
python run.py
pause

