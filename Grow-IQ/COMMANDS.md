# Glow-IQ Application Commands

This document provides all the commands needed to run your Glow-IQ web application in different environments.

## Quick Start Commands

### 🚀 **One-Command Startup (Recommended)**
```bash
# Run both frontend and backend in development mode
./run-dev.sh
```

### 🔧 **Backend Only**
```bash
# Run only the Python FastAPI backend
./run-backend.sh
```

### 🎨 **Frontend Only**
```bash
# Run only the React frontend development server
./run-frontend.sh
```

### 🏭 **Production Mode**
```bash
# Run in production mode with Gunicorn
./run-production.sh
```

### 🐳 **Docker Mode**
```bash
# Run with Docker
./run-docker.sh

# Run with Docker Compose
./run-docker.sh compose
```

## Manual Commands

### **Development Setup**

#### 1. **Python Backend Setup**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run backend
python start.py
```

#### 2. **React Frontend Setup**
```bash
# Navigate to frontend directory
cd fronted

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### **Production Commands**

#### 1. **Backend Production**
```bash
# Install production dependencies
pip install -r requirements-azure.txt

# Set production environment variables
export DEBUG=false
export ENVIRONMENT=production
export DATABASE_URL="your-production-database-url"
export SECRET_KEY="your-secret-key"

# Run with Gunicorn
gunicorn app:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

#### 2. **Frontend Production**
```bash
cd fronted

# Build for production
npm run build

# Serve static files (if needed)
npx serve dist/public
```

### **Docker Commands**

#### 1. **Build Docker Image**
```bash
# Build the image
docker build -t glow-iq:latest .

# Run the container
docker run -d \
  --name glow-iq-app \
  -p 8000:8000 \
  -e DATABASE_URL="sqlite:///./dashboard.db" \
  -e SECRET_KEY="your-secret-key" \
  glow-iq:latest
```

#### 2. **Docker Compose**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Environment Variables

### **Required Variables**
```bash
# Database
export DATABASE_URL="sqlite:///./dashboard.db"  # or PostgreSQL URL

# Security
export SECRET_KEY="your-secret-key-here"

# Server
export HOST="0.0.0.0"
export PORT="8000"
```

### **Optional Variables**
```bash
# Environment
export ENVIRONMENT="development"  # or "production"
export DEBUG="true"  # or "false"

# Workers (production)
export WORKERS="4"

# Additional settings
export UPLOAD_FOLDER="./uploads"
export MAX_FILE_SIZE="16777216"  # 16MB
```

## Database Commands

### **SQLite (Development)**
```bash
# Database file will be created automatically
# Location: ./dashboard.db
```

### **PostgreSQL (Production)**
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Set database URL
export DATABASE_URL="postgresql://user:password@localhost:5432/glow_iq"

# Run migrations (if using Alembic)
alembic upgrade head
```

## Testing Commands

### **Backend Tests**
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### **Frontend Tests**
```bash
cd fronted

# Run tests (if configured)
npm test

# Run linting
npm run lint
```

## Monitoring Commands

### **Health Checks**
```bash
# Backend health
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs

# Frontend
curl http://localhost:5173
```

### **Logs**
```bash
# Backend logs (if using systemd)
journalctl -u glow-iq -f

# Docker logs
docker logs -f glow-iq-app

# Application logs
tail -f logs/app.log
```

## Troubleshooting Commands

### **Common Issues**

#### 1. **Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
export PORT="8001"
python start.py
```

#### 2. **Dependencies Issues**
```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

#### 3. **Node.js Issues**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 4. **Database Issues**
```bash
# Delete SQLite database
rm dashboard.db

# Recreate database
python -c "from database_enhanced import init_database; init_database()"
```

## Development Workflow

### **Daily Development**
```bash
# 1. Start development environment
./run-dev.sh

# 2. Make changes to code
# 3. Test in browser
# 4. Stop with Ctrl+C
```

### **Testing Changes**
```bash
# 1. Run backend only
./run-backend.sh

# 2. In another terminal, run frontend
./run-frontend.sh

# 3. Test API endpoints
curl http://localhost:8000/health
```

### **Production Deployment**
```bash
# 1. Build frontend
cd fronted && npm run build && cd ..

# 2. Install production dependencies
pip install -r requirements-azure.txt

# 3. Set production environment variables
export ENVIRONMENT=production
export DEBUG=false

# 4. Run production server
./run-production.sh
```

## Performance Commands

### **Backend Performance**
```bash
# Run with multiple workers
gunicorn app:app --bind 0.0.0.0:8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Profile performance
python -m cProfile -o profile.stats start.py
```

### **Frontend Performance**
```bash
# Build with optimizations
cd fronted
npm run build -- --mode production

# Analyze bundle size
npm run build -- --analyze
```

## Security Commands

### **Generate Secret Key**
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Or using OpenSSL
openssl rand -hex 32
```

### **Check Dependencies**
```bash
# Check for security vulnerabilities
pip install safety
safety check

# Check for outdated packages
pip list --outdated
```

## Backup Commands

### **Database Backup**
```bash
# SQLite backup
cp dashboard.db dashboard.db.backup.$(date +%Y%m%d_%H%M%S)

# PostgreSQL backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

### **Application Backup**
```bash
# Create backup archive
tar -czf glow-iq-backup-$(date +%Y%m%d_%H%M%S).tar.gz \
  --exclude=venv \
  --exclude=node_modules \
  --exclude=__pycache__ \
  --exclude=.git \
  .
```

## Quick Reference

| Command | Purpose | Environment |
|---------|---------|-------------|
| `./run-dev.sh` | Start both frontend and backend | Development |
| `./run-backend.sh` | Start backend only | Development |
| `./run-frontend.sh` | Start frontend only | Development |
| `./run-production.sh` | Start in production mode | Production |
| `./run-docker.sh` | Start with Docker | Any |
| `python start.py` | Manual backend start | Any |
| `npm run dev` | Manual frontend start | Development |
| `npm run build` | Build frontend | Production |

---

For more detailed information, see the individual script files or the main documentation.
