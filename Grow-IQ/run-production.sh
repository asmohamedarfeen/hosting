#!/bin/bash

# Glow-IQ Production Server Startup Script
# This script runs the application in production mode

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
    echo -e "${BLUE}[GLOW-IQ PRODUCTION]${NC} $1"
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
    
    print_status "Installing production dependencies..."
    pip install --upgrade pip
    pip install -r requirements-azure.txt
}

# Build frontend
build_frontend() {
    print_status "Building frontend for production..."
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    cd fronted
    
    # Install dependencies
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Build frontend
    print_status "Building React application..."
    npm run build
    
    cd ..
    
    print_status "Frontend built successfully"
}

# Start production server
start_production() {
    print_header "Starting Production Server..."
    
    # Set production environment variables
    export DEBUG=false
    export ENVIRONMENT=production
    export DATABASE_URL="${DATABASE_URL:-sqlite:///./dashboard.db}"
    export SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"
    export HOST="${HOST:-0.0.0.0}"
    export PORT="${PORT:-8000}"
    export WORKERS="${WORKERS:-4}"
    
    print_status "Production configuration:"
    print_status "  - Host: $HOST"
    print_status "  - Port: $PORT"
    print_status "  - Workers: $WORKERS"
    print_status "  - Debug: $DEBUG"
    print_status "  - Environment: $ENVIRONMENT"
    
    # Start with Gunicorn for production
    print_status "Starting with Gunicorn..."
    gunicorn app:app \
        --bind $HOST:$PORT \
        --workers $WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        --access-logfile - \
        --error-logfile - \
        --log-level info
}

# Cleanup function
cleanup() {
    print_header "Shutting down production server..."
    print_status "Production server stopped. Goodbye! 👋"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    print_header "🚀 Starting Glow-IQ Production Server"
    echo "============================================="
    
    # Pre-flight checks
    check_python
    
    # Setup environment
    setup_python_env
    
    # Build frontend
    build_frontend
    
    # Start production server
    start_production
}

# Run main function
main "$@"
