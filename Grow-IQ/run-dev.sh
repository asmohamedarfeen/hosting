#!/bin/bash

# Glow-IQ Development Server Startup Script
# This script runs both frontend and backend in development mode

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[GLOW-IQ]${NC} $1"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_status "Python version: $PYTHON_VERSION"
}

# Check if Node.js is installed
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    print_status "Node.js version: $NODE_VERSION"
}

# Create virtual environment if it doesn't exist
setup_python_env() {
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    print_status "Activating Python virtual environment..."
    source venv/bin/activate
    
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
}

# Install frontend dependencies
setup_frontend() {
    if [ ! -d "fronted/node_modules" ]; then
        print_status "Installing frontend dependencies..."
        cd fronted
        npm install
        cd ..
    fi
}

# Start backend server
start_backend() {
    print_header "Starting Backend Server..."
    
    # Set environment variables for development
    export DEBUG=true
    export ENVIRONMENT=development
    export DATABASE_URL="sqlite:///./dashboard.db"
    export SECRET_KEY="dev-secret-key-change-in-production"
    
    # Start the backend
    python3 start.py &
    BACKEND_PID=$!
    
    print_status "Backend server started with PID: $BACKEND_PID"
    print_status "Backend URL: http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
    print_status "Health Check: http://localhost:8000/health"
}

# Start frontend server
start_frontend() {
    print_header "Starting Frontend Server..."
    
    cd fronted
    
    # Start the frontend development server
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
    
    print_status "Frontend server started with PID: $FRONTEND_PID"
    print_status "Frontend URL: http://localhost:5173"
}

# Wait for servers to start
wait_for_servers() {
    print_status "Waiting for servers to start..."
    sleep 5
    
    # Check if backend is running
    if curl -s http://localhost:8000/health > /dev/null; then
        print_status "✅ Backend server is running"
    else
        print_warning "⚠️  Backend server may not be ready yet"
    fi
    
    # Check if frontend is running
    if curl -s http://localhost:5173 > /dev/null; then
        print_status "✅ Frontend server is running"
    else
        print_warning "⚠️  Frontend server may not be ready yet"
    fi
}

# Cleanup function
cleanup() {
    print_header "Shutting down servers..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_status "Backend server stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_status "Frontend server stopped"
    fi
    
    print_status "All servers stopped. Goodbye! 👋"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    print_header "🚀 Starting Glow-IQ Development Environment"
    echo "=================================================="
    
    # Pre-flight checks
    check_python
    check_node
    
    # Setup environments
    setup_python_env
    setup_frontend
    
    # Start servers
    start_backend
    start_frontend
    
    # Wait and verify
    wait_for_servers
    
    echo ""
    print_header "🎉 Glow-IQ is now running!"
    echo "=================================================="
    echo "🌐 Frontend: http://localhost:5173"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo "🏥 Health Check: http://localhost:8000/health"
    echo ""
    echo "Press Ctrl+C to stop all servers"
    echo "=================================================="
    
    # Keep script running
    wait
}

# Run main function
main "$@"
