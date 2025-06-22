@echo off
REM VyralFlow AI Quick Start Script for Windows

echo.
echo 🚀 Starting VyralFlow AI...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo 📦 Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

REM Start backend in new window
echo 🔧 Starting backend server...
start "VyralFlow Backend" cmd /k "venv\Scripts\activate 2>nul || vyralflow-env\Scripts\activate 2>nul && python start.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo 🎨 Starting frontend server...
start "VyralFlow Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ✅ VyralFlow AI is starting up!
echo.
echo 🔗 Frontend: http://localhost:5173
echo 🔗 Backend API: http://localhost:8080/docs
echo.
echo Close this window to keep services running
echo Or press Ctrl+C to stop all services
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

pause
