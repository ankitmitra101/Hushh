#!/bin/bash

echo "==================================================="
echo "  Hushh - AI Shopping Concierge | One-Click Start"
echo "==================================================="

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python
if ! command_exists python3; then
    echo "[ERROR] Python 3 is not installed."
    exit 1
fi

# Check for Node.js
if ! command_exists npm; then
    echo "[ERROR] Node.js/npm is not installed."
    exit 1
fi

echo "[1/4] Setting up Backend..."
if [ ! -f ".env" ]; then
    echo "     Creating .env from .env.example..."
    cp .env.example .env
    echo "     [IMPORTANT] Please edit .env to add your OPENAI_API_KEY"
fi

if [ ! -d ".venv" ]; then
    echo "     Creating Python virtual environment..."
    python3 -m venv .venv
fi

echo "     Installing backend dependencies..."
source .venv/bin/activate
pip install -r requirements.txt >/dev/null 2>&1

echo ""
echo "[2/4] Starting Backend Server..."
# Run backend in background and save PID
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "     Backend started (PID: $BACKEND_PID)"

echo ""
echo "[3/4] Setting up Frontend..."
cd hushh-react-frontend

if [ ! -f ".env" ]; then
    echo "     Creating frontend .env..."
    cp .env.example .env
fi

if [ ! -d "node_modules" ]; then
    echo "     Installing frontend dependencies..."
    npm install >/dev/null 2>&1
fi

echo ""
echo "[4/4] Starting Frontend..."
echo "     Opening http://localhost:5173 ..."

# Trap Ctrl+C to kill backend too
trap "kill $BACKEND_PID; exit" SIGINT SIGTERM

npm run dev
