# Glow-IQ Requirements Documentation

This document explains the different requirements files available for the Glow-IQ application and when to use each one.

## Requirements Files Overview

### 1. `requirements.txt` - **Main Production Requirements**
- **Purpose**: Complete production deployment with all features
- **Use Case**: Full-featured production deployment
- **Includes**: All dependencies for ML, speech recognition, monitoring, etc.

### 2. `requirements-azure.txt` - **Azure App Service Optimized**
- **Purpose**: Optimized for Azure App Service deployment
- **Use Case**: When deploying to Azure App Service
- **Includes**: Azure-specific dependencies and optimizations

### 3. `requirements-minimal.txt` - **Minimal Dependencies**
- **Purpose**: Basic functionality with minimal dependencies
- **Use Case**: Quick deployment, testing, or resource-constrained environments
- **Includes**: Only essential dependencies

### 4. `requirements-dev.txt` - **Development Requirements**
- **Purpose**: Development tools and testing dependencies
- **Use Case**: Local development environment
- **Includes**: Testing frameworks, code quality tools, debugging tools

### 5. `requirements_production.txt` - **Legacy Production**
- **Purpose**: Previous production requirements (legacy)
- **Use Case**: Reference or migration from old setup
- **Status**: Consider migrating to `requirements.txt`

## Installation Instructions

### For Production Deployment

```bash
# Full production setup
pip install -r requirements.txt

# Azure App Service deployment
pip install -r requirements-azure.txt

# Minimal setup
pip install -r requirements-minimal.txt
```

### For Development

```bash
# Development setup (includes production + dev tools)
pip install -r requirements-dev.txt

# Or install production requirements first, then dev tools
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Dependency Categories

### Core Application Dependencies
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation

### Database Dependencies
- **PostgreSQL**: `psycopg2-binary` (production)
- **SQLite**: Built-in with Python (development)
- **Alembic**: Database migrations

### Authentication & Security
- **JWT**: `python-jose[cryptography]`
- **Password Hashing**: `passlib[bcrypt]`
- **Encryption**: `cryptography`
- **CORS**: `fastapi-cors`

### Machine Learning & AI
- **Scikit-learn**: ML algorithms
- **NumPy**: Numerical computing
- **Google Generative AI**: Resume testing
- **Speech Recognition**: Audio processing

### Monitoring & Logging
- **Structlog**: Structured logging
- **Prometheus**: Metrics collection
- **Sentry**: Error tracking
- **OpenTelemetry**: Distributed tracing

### Azure Integration
- **Azure Identity**: Authentication
- **Azure Key Vault**: Secrets management
- **Azure Storage**: File storage
- **Azure Management**: Resource management

## Version Pinning Strategy

### Production Requirements
- **Major versions pinned**: `fastapi>=0.104.1`
- **Security updates**: `cryptography>=41.0.0`
- **Compatibility**: Tested combinations

### Development Requirements
- **Latest compatible**: `pytest>=7.4.0`
- **Development tools**: Latest stable versions
- **Testing frameworks**: Compatible versions

## Environment-Specific Considerations

### Azure App Service
- **Python Version**: 3.11 (recommended)
- **Memory**: Minimum 1GB for full features
- **Storage**: Use Azure Storage for file uploads
- **Database**: Azure Database for PostgreSQL

### Local Development
- **Python Version**: 3.11+
- **Database**: SQLite (default) or PostgreSQL
- **Redis**: Optional for caching
- **File Storage**: Local filesystem

### Docker Deployment
- **Base Image**: `python:3.11-slim`
- **Dependencies**: Use `requirements-azure.txt`
- **Multi-stage**: Separate build and runtime

## Security Considerations

### Production Security
- **Secrets Management**: Azure Key Vault
- **HTTPS Only**: Enforced in production
- **CORS**: Properly configured
- **Rate Limiting**: Implemented

### Development Security
- **Local Secrets**: `.env` files (not committed)
- **Test Data**: No real credentials
- **Dependencies**: Regular security updates

## Performance Optimization

### Production Optimizations
- **Async Support**: `uvicorn[standard]`
- **Connection Pooling**: SQLAlchemy
- **Caching**: Redis
- **CDN**: Azure CDN for static files

### Development Optimizations
- **Hot Reload**: `uvicorn --reload`
- **Debug Mode**: Detailed error messages
- **Profiling**: `py-spy` for performance analysis

## Troubleshooting

### Common Issues

#### 1. Dependency Conflicts
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt
```

#### 2. Azure Deployment Issues
```bash
# Use Azure-specific requirements
pip install -r requirements-azure.txt

# Check Azure CLI
az --version
az login
```

#### 3. Development Setup Issues
```bash
# Install development requirements
pip install -r requirements-dev.txt

# Run tests
pytest
```

### Dependency Resolution

#### 1. Check for Conflicts
```bash
pip check
```

#### 2. Update Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

#### 3. Lock Dependencies
```bash
pip freeze > requirements-lock.txt
```

## Maintenance

### Regular Updates
- **Security Updates**: Monthly
- **Feature Updates**: Quarterly
- **Major Versions**: Annually

### Dependency Monitoring
- **Security Scanning**: `safety check`
- **Vulnerability Scanning**: `bandit`
- **License Compliance**: Check licenses

### Version Management
- **Semantic Versioning**: Follow semver
- **Breaking Changes**: Document and test
- **Compatibility**: Test across environments

## Migration Guide

### From Legacy Requirements
1. **Backup**: Current working environment
2. **Test**: New requirements in staging
3. **Deploy**: Gradual rollout
4. **Monitor**: Performance and errors

### Between Requirements Files
1. **Identify**: Required features
2. **Choose**: Appropriate requirements file
3. **Install**: New requirements
4. **Test**: Application functionality

---

For questions or issues with dependencies, please refer to the troubleshooting section or contact the development team.
