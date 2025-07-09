#!/bin/bash

# Jnana Web Interface Startup Script

set -e

echo "�� Starting Jnana Web Interface"
echo "================================"

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Error: Please run this script from the jnana-web directory"
    exit 1
fi

# Create virtual environment for backend if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "�� Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

# Create necessary directories
mkdir -p backend/instance
mkdir -p ../sessions

echo "✅ Setup complete!"
echo ""
echo "🌐 Starting services..."
echo "Backend will run on: http://localhost:5001"
echo "Frontend will run on: http://localhost:3000"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend
echo "🔧 Starting Flask backend..."
cd backend
source venv/bin/activate
python run.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "⚛️  Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Jnana Web Interface is starting up!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for background processes
wait
