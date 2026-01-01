#!/bin/bash

# A2UI Meeting Assistant Startup Script

echo "Starting A2UI Meeting Assistant..."

# Check if Python environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Please activate your Python virtual environment first"
    exit 1
fi

# Set environment variables
export $(cat .env.a2ui | xargs)

# Start the FastAPI backend
echo "Starting FastAPI backend..."
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start the A2UI client (if built)
if [ -d "a2ui_integration/client/dist" ]; then
    echo "Starting A2UI client..."
    cd a2ui_integration/client/dist
    python -m http.server 3001 &
    CLIENT_PID=$!
    cd ../../..
else
    echo "A2UI client not built. Run 'python a2ui_integration/setup.py --build-client' to build it."
fi

echo "A2UI Meeting Assistant started!"
echo "Backend: http://localhost:8005"
echo "A2UI Client: http://localhost:3001"
echo "WebSocket: ws://localhost:8005/ws/a2ui"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    if [ ! -z "$CLIENT_PID" ]; then
        kill $CLIENT_PID 2>/dev/null
    fi
    exit 0
}

trap cleanup EXIT

# Wait for processes
wait
