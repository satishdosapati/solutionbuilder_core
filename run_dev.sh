#!/bin/bash
echo "Starting AWS Solution Architect Tool Development Environment..."

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Start backend in background
echo "Starting backend server..."
cd backend
./setup.sh
source venv/bin/activate || source venv/Scripts/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Start frontend
echo "Starting frontend server..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Development servers started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
