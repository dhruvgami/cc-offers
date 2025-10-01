#!/bin/bash

# Travel Discount Comparison Tool - Frontend Startup Script

set -e  # Exit on error

echo "🚀 Starting Travel Discount Comparison Frontend..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Dependencies not found. Installing..."
    npm install
    echo "✅ Dependencies installed"
    echo ""
fi

# Start the development server
echo "✨ Starting Vite development server..."
echo "📍 Frontend: http://localhost:5173"
echo "📍 Backend API: http://localhost:8000"
echo ""
echo "Press CTRL+C to stop"
echo ""

npm run dev
