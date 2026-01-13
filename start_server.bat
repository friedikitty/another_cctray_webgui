@echo off
REM Windows batch script to start the CCTray Build Status Monitor
REM This script starts the Waitress WSGI server

echo Starting CCTray Build Status Monitor...
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Start the WSGI server
py -3 wsgi.py

pause
