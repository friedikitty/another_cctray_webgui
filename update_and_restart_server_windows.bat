@echo off
REM Windows batch script to update and restart the CCTray Build Status Monitor service
REM This script stops the service, updates from SVN, and restarts the service

set SERVICE_NAME=cctray_python
set ERROR_OCCURRED=0

echo ========================================
echo Updating and Restarting CCTray Service
echo ========================================
echo.

REM Check if running from correct directory
if not exist "wsgi.py" (
    echo ERROR: wsgi.py not found. Please run this script from the project directory.
    exit /b 1
)

REM Stop the service
echo [1/3] Stopping service: %SERVICE_NAME%
net stop %SERVICE_NAME%
if errorlevel 1 (
    echo WARNING: Failed to stop service. It may not be running.
    REM Continue anyway - service might not be running
) else (
    echo Service stopped successfully.
)
echo.

REM Update from SVN
echo [2/3] Updating from SVN...
svn up .
if errorlevel 1 (
    echo ERROR: SVN update failed!
    set ERROR_OCCURRED=1
) else (
    echo SVN update completed successfully.
)
echo.

REM Start the service
if %ERROR_OCCURRED%==0 (
    echo [3/3] Starting service: %SERVICE_NAME%
    net start %SERVICE_NAME%
    if errorlevel 1 (
        echo ERROR: Failed to start service!
        exit /b 1
    ) else (
        echo Service started successfully.
    )
) else (
    echo ERROR: Skipping service start due to previous errors.
    echo Please fix the SVN update issue and restart the service manually.
    exit /b 1
)

echo.
echo ========================================
echo Update and restart completed successfully!
echo ========================================