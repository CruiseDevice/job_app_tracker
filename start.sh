#!/bin/bash

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting Job Application Tracker...${NC}\n"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    kill 0
    exit
}

trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${BLUE}[Backend]${NC} Starting FastAPI server on port 8000..."
cd backend && python main.py &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 2

# Start frontend
echo -e "${GREEN}[Frontend]${NC} Starting Vite dev server on port 5173..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo -e "\n${YELLOW}✅ Both servers are running!${NC}"
echo -e "${BLUE}Backend:${NC}  http://localhost:8000"
echo -e "${GREEN}Frontend:${NC} http://localhost:5173"
echo -e "\n${YELLOW}Press Ctrl+C to stop both servers${NC}\n"

# Wait for both processes
wait

