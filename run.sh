#!/bin/bash
# run.sh

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting YouTube to Flashcards Application...${NC}"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please update .env with your OpenAI API key"
fi

# Install dependencies if needed
echo -e "${GREEN}Checking dependencies...${NC}"
pip install -q -r requirements.txt

# Start the FastAPI backend
echo -e "${GREEN}Starting FastAPI backend on port 8000...${NC}"
uvicorn main:app --reload --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Open browser
echo -e "${GREEN}Opening application in browser...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:8000
fi

echo -e "${BLUE}Application is running!${NC}"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"

# Wait for Ctrl+C
trap "kill $BACKEND_PID; exit" INT
wait