@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "ADMIN_DIR=%ROOT%frontend_admin"
set "PORT=5000"
set "ADMIN_PORT=8083"

echo.
echo ========================================
echo   PowerNest Battery SaaS Startup
echo ========================================
echo.

if not exist "%BACKEND_DIR%" (
  echo [ERROR] backend directory not found: %BACKEND_DIR%
  pause
  exit /b 1
)

if not exist "%ADMIN_DIR%" (
  echo [ERROR] frontend_admin directory not found: %ADMIN_DIR%
  pause
  exit /b 1
)

rem Start admin frontend in a new window.
where npm >nul 2>&1
if errorlevel 1 (
  echo [WARN] npm not found. Admin frontend will not be started.
  echo [WARN] Please install Node.js if you need the admin frontend.
) else (
  echo [INFO] Starting admin frontend in a new window...
  start "PowerNest Admin Frontend" /D "%ADMIN_DIR%" cmd /k "if not exist node_modules npm install & set PORT=%ADMIN_PORT% & npm run serve"
  echo [INFO] Admin frontend: http://localhost:%ADMIN_PORT%
)

rem Start backend in current window.
cd /d "%BACKEND_DIR%"
set "PY=%BACKEND_DIR%\venv\Scripts\python.exe"

if not exist "%PY%" (
  echo [INFO] Backend venv not found. Creating venv...
  python --version >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ and add it to PATH.
    pause
    exit /b 1
  )
  python -m venv venv
  if not exist "%PY%" (
    echo [ERROR] Failed to create backend venv.
    pause
    exit /b 1
  )
)

echo [INFO] Installing backend dependencies...
"%PY%" -m pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Failed to install backend dependencies.
  pause
  exit /b 1
)

echo.
echo ========================================
echo   Backend API:      http://127.0.0.1:%PORT%
echo   Health Check:     http://127.0.0.1:%PORT%/api/v1/health
echo   Admin Frontend:   http://localhost:%ADMIN_PORT%
echo   Stop backend:     Ctrl+C
echo ========================================
echo.

"%PY%" run.py
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if not "%EXIT_CODE%"=="0" (
  echo [ERROR] Backend exited with code %EXIT_CODE%.
  pause
)
exit /b %EXIT_CODE%
