#!/bin/bash

# Glow-IQ Frontend Only Startup Script
# This script runs only the React frontend development server

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
    echo -e "${BLUE}[GLOW-IQ FRONTEND]${NC} $1"
}

# Check if Node.js is installed
check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    print_status "Node.js version: $NODE_VERSION"
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    NPM_VERSION=$(npm --version)
    print_status "npm version: $NPM_VERSION"
}

# Install frontend dependencies
setup_frontend() {
    print_status "Installing frontend dependencies..."
    cd fronted
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing npm packages..."
        npm install
    else
        print_status "Dependencies already installed"
    fi
    
    print_status "Frontend dependencies ready"
}

# Start frontend server
start_frontend() {
    print_header "Starting Frontend Development Server..."
    
    cd fronted
    
    print_status "Frontend configuration:"
    print_status "  - Environment: development"
    print_status "  - Build tool: Vite"
    print_status "  - Framework: React + TypeScript"
    
    # Start the frontend development server
    npm run dev
}

# Cleanup function
cleanup() {
    print_header "Shutting down frontend server..."
    print_status "Frontend server stopped. Goodbye! 👋"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    print_header "🚀 Starting Glow-IQ Frontend Server"
    echo "==========================================="
    
    # Pre-flight checks
    check_node
    
    # Setup frontend
    setup_frontend
    
    # Start frontend
    start_frontend
}

# Run main function
main "$@"
