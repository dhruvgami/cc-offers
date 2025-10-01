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

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo "✅ Dependencies installed"
    echo ""
fi

# Check if Playwright browser is installed
if ! python -c "from playwright.sync_api import sync_playwright; sync_playwright().start().chromium.executable_path" 2>/dev/null; then
    echo "🌐 Installing Playwright browser..."
    playwright install chromium
    echo "✅ Playwright browser installed"
    echo ""
fi

# Initialize database if needed
if [ ! -f "../data/travel_discounts.db" ]; then
    echo "🗄️  Initializing database..."
    python -c "import sys; sys.path.insert(0, '.'); from shared.init_db import *; init_db(); seed_initial_data()"
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

python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
