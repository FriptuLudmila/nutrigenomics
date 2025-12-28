@echo off
echo ============================================================
echo   NUTRIGENOMICS PLATFORM LAUNCHER
echo ============================================================
echo.

echo [1/3] Checking MongoDB...
tasklist | findstr mongod >nul
if errorlevel 1 (
    echo [WARNING] MongoDB is not running!
    echo Please start MongoDB first.
    pause
    exit /b 1
) else (
    echo [OK] MongoDB is running
)

echo.
echo [2/3] Starting Flask Backend...
start cmd /k "title Flask Backend && python run.py"
timeout /t 3 >nul

echo.
echo [3/3] Starting Next.js Frontend...
start cmd /k "title Next.js Frontend && cd frontend && npm run dev"

echo.
echo ============================================================
echo   SERVERS STARTING...
echo ============================================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to stop all servers...
pause >nul

echo.
echo Stopping servers...
taskkill /FI "WindowTitle eq Flask Backend*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Next.js Frontend*" /F >nul 2>&1
echo Done!
