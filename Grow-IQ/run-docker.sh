#!/bin/bash

# Glow-IQ Docker Startup Script
# This script runs the application using Docker

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
    echo -e "${BLUE}[GLOW-IQ DOCKER]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    DOCKER_VERSION=$(docker --version)
    print_status "Docker version: $DOCKER_VERSION"
    
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose not found. Using 'docker compose' instead."
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
}

# Build Docker image
build_image() {
    print_status "Building Docker image..."
    docker build -t glow-iq:latest .
    print_status "Docker image built successfully"
}

# Run with Docker
run_docker() {
    print_header "Starting Glow-IQ with Docker..."
    
    # Set environment variables
    export DATABASE_URL="${DATABASE_URL:-sqlite:///./dashboard.db}"
    export SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"
    export HOST="0.0.0.0"
    export PORT="8000"
    export DEBUG="false"
    export ENVIRONMENT="production"
    
    print_status "Docker configuration:"
    print_status "  - Image: glow-iq:latest"
    print_status "  - Host: $HOST"
    print_status "  - Port: $PORT"
    print_status "  - Environment: $ENVIRONMENT"
    
    # Run the container
    docker run -d \
        --name glow-iq-app \
        -p $PORT:8000 \
        -e DATABASE_URL="$DATABASE_URL" \
        -e SECRET_KEY="$SECRET_KEY" \
        -e HOST="$HOST" \
        -e PORT="8000" \
        -e DEBUG="$DEBUG" \
        -e ENVIRONMENT="$ENVIRONMENT" \
        glow-iq:latest
    
    print_status "Container started successfully"
    print_status "Application URL: http://localhost:$PORT"
    print_status "API Documentation: http://localhost:$PORT/docs"
    print_status "Health Check: http://localhost:$PORT/health"
}

# Run with Docker Compose
run_compose() {
    print_header "Starting Glow-IQ with Docker Compose..."
    
    if [ -f "docker-compose.yml" ]; then
        $COMPOSE_CMD up -d
        print_status "Services started with Docker Compose"
    else
        print_warning "docker-compose.yml not found. Creating a basic one..."
        create_compose_file
        $COMPOSE_CMD up -d
    fi
}

# Create basic docker-compose.yml
create_compose_file() {
    cat > docker-compose.yml << EOF
version: '3.8'

services:
  glow-iq:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./dashboard.db
      - SECRET_KEY=your-secret-key-here
      - HOST=0.0.0.0
      - PORT=8000
      - DEBUG=false
      - ENVIRONMENT=production
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=glow_iq
      - POSTGRES_USER=glow_iq
      - POSTGRES_PASSWORD=glow_iq_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
EOF
    
    print_status "Created docker-compose.yml"
}

# Show logs
show_logs() {
    print_status "Showing container logs..."
    docker logs -f glow-iq-app
}

# Stop containers
stop_containers() {
    print_header "Stopping containers..."
    
    if [ -f "docker-compose.yml" ]; then
        $COMPOSE_CMD down
    else
        docker stop glow-iq-app 2>/dev/null || true
        docker rm glow-iq-app 2>/dev/null || true
    fi
    
    print_status "Containers stopped"
}

# Cleanup function
cleanup() {
    print_header "Shutting down Docker containers..."
    stop_containers
    print_status "Docker containers stopped. Goodbye! 👋"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    print_header "🚀 Starting Glow-IQ with Docker"
    echo "======================================"
    
    # Pre-flight checks
    check_docker
    
    # Build image
    build_image
    
    # Choose run method
    if [ "$1" = "compose" ]; then
        run_compose
    else
        run_docker
    fi
    
    echo ""
    print_header "🎉 Glow-IQ is running in Docker!"
    echo "======================================"
    echo "🌐 Application: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo "🏥 Health Check: http://localhost:8000/health"
    echo ""
    echo "To view logs: docker logs -f glow-iq-app"
    echo "To stop: docker stop glow-iq-app"
    echo "Press Ctrl+C to stop and cleanup"
    echo "======================================"
    
    # Keep script running and show logs
    show_logs
}

# Run main function
main "$@"
