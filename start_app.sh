#!/bin/bash
echo "🚀 Starting Cash Tracker Application..."

# Start backend in background
echo "🐍 Starting Python backend..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=

# Wait for backend to start
sleep 3

# Start frontend
echo "⚛️ Starting React frontend..."
cd ../frontend
npm start &
FRONTEND_PID=

echo "✅ Application started!"
echo "Backend: http://localhost:5001"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'kill  ; exit' INT
wait
