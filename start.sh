#!/bin/bash

echo "🚀 Starting School Agent Simple..."

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate 2>/dev/null || python -m venv venv && source venv/bin/activate
pip install -r requirements.txt -q
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend..."
cd frontend
npm install --silent
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ School Agent is running!"
echo "Backend: http://localhost:8000 (PID: $BACKEND_PID)"
echo "Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait