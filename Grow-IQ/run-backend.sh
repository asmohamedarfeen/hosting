#!/bin/bash

# Glow-IQ Backend Only Startup Script
# This script runs only the Python FastAPI backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo -e "${BLUE}[GLOW-IQ BACKEND]${NC} $1"
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

# Setup Python environment
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

# Start backend server
start_backend() {
    print_header "Starting Backend Server..."
    
    # Set environment variables
    export DEBUG=true
    export ENVIRONMENT=development
    export DATABASE_URL="sqlite:///./dashboard.db"
    export SECRET_KEY="dev-secret-key-change-in-production"
    export HOST="0.0.0.0"
    export PORT="8000"
    
    print_status "Backend configuration:"
    print_status "  - Host: $HOST"
    print_status "  - Port: $PORT"
    print_status "  - Debug: $DEBUG"
    print_status "  - Database: $DATABASE_URL"
    
    # Start the backend
    python3 start.py
}

# Cleanup function
cleanup() {
    print_header "Shutting down backend server..."
    print_status "Backend server stopped. Goodbye! 👋"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    print_header "🚀 Starting Glow-IQ Backend Server"
    echo "=========================================="
    
    # Pre-flight checks
    check_python
    
    # Setup environment
    setup_python_env
    
    # Start backend
    start_backend
}

# Run main function
main "$@"
