@echo off
echo ===================================================
echo   Hushh - AI Shopping Concierge | One-Click Start
echo ===================================================

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.10+
    pause
    exit /b
)

REM Check for Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH. Please install Node.js (LTS recommended)
    pause
    exit /b
)

echo [1/4] Setting up Backend...
if not exist ".env" (
    echo      Creating .env from .env.example...
    copy .env.example .env >nul
    echo      [IMPORTANT] You may need to edit .env to add your OPENAI_API_KEY (Groq key)
)

if not exist ".venv" (
    echo      Creating Python virtual environment...
    python -m venv .venv
)

echo      Installing/Updating backend dependencies...
call .venv\Scripts\activate
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo      [WARNING] Pip install failed or partially failed. Retrying with verbose...
    pip install -r requirements.txt
)

echo.
echo [2/4] Starting Backend Server...
start "Hushh Backend" cmd /k "call .venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo [3/4] Setting up Frontend...
cd hushh-react-frontend
if not exist ".env" (
    echo      Creating frontend .env...
    copy .env.example .env >nul
)

if not exist "node_modules" (
    echo      Installing frontend dependencies (this may take a minute)...
    call npm install >nul 2>&1
)

echo.
echo [4/4] Starting Frontend...
echo      The application will open in your browser shortly...
echo      Frontend: http://localhost:5173
echo      Backend:  http://localhost:8000
echo.
echo Press any key to stop the frontend (Backend runs in separate window)...
call npm run dev

cd ..
