#!/bin/bash

# Travel Discount Comparison Tool - Backend Startup Script

set -e  # Exit on error

echo "🚀 Starting Travel Discount Comparison API..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Define Python paths (use venv if activated, otherwise use venv's python directly)
PYTHON="./venv/bin/python3"
PIP="./venv/bin/pip"

# Check if dependencies are installed
if ! $PYTHON -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    $PIP install --upgrade pip -q
    $PIP install -r requirements.txt -q
    echo "✅ Dependencies installed"
    echo ""
fi

# Check if Playwright browser is installed
if ! $PYTHON -c "from playwright.sync_api import sync_playwright; sync_playwright().start().chromium.executable_path" 2>/dev/null; then
    echo "🌐 Installing Playwright browser..."
    $PYTHON -m playwright install chromium
    echo "✅ Playwright browser installed"
    echo ""
fi

# Initialize database if needed
if [ ! -f "../data/travel_discounts.db" ]; then
    echo "🗄️  Initializing database..."
    $PYTHON -c "import sys; sys.path.insert(0, '.'); from shared.init_db import *; init_db(); seed_initial_data()"
    echo ""
fi

# Start the server
echo "✨ Starting FastAPI server..."
echo "📍 API: http://localhost:8000"
echo "📖 Docs: http://localhost:8000/docs"
echo "🏥 Health: http://localhost:8000/health"
echo ""
echo "Press CTRL+C to stop"
echo ""

$PYTHON -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
