# SQLAlchemy Setup for CareerConnect

## Overview

CareerConnect is now fully configured with **SQLAlchemy 2.0** as the primary database ORM. The application uses modern SQLAlchemy patterns with proper session management, migrations, and error handling.

## Features

✅ **SQLAlchemy 2.0** with modern syntax and best practices  
✅ **Declarative models** with proper relationships and constraints  
✅ **Session management** with dependency injection and automatic cleanup  
✅ **Database migrations** using Alembic  
✅ **Connection pooling** and optimization  
✅ **Comprehensive error handling** and logging  
✅ **Health monitoring** and diagnostics  

## Database Configuration

### Current Setup
- **Database**: SQLite (default) with PostgreSQL support
- **Location**: `dashboard.db` in the project root
- **Engine**: SQLAlchemy engine with optimized settings
- **Sessions**: FastAPI dependency injection pattern

### Environment Variables
```bash
# Optional: Override database URL
export DATABASE_URL="postgresql://user:password@localhost/careerconnect"
```

## Models Structure

The application includes comprehensive models for:

- **User Management**: Users, profiles, authentication
- **Social Features**: Posts, comments, likes
- **Professional Networking**: Connections, friend requests
- **Career Features**: Jobs, events, notifications
- **Communication**: Messages, conversations

### Key Model Features
- **Relationships**: Proper foreign keys and backrefs
- **Constraints**: Check constraints and validation
- **Indexes**: Optimized database queries
- **Cascading**: Automatic cleanup on deletion

## Database Operations

### Session Management

#### FastAPI Dependency (Recommended)
```python
from fastapi import Depends
from database import get_db
from sqlalchemy.orm import Session

@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

#### Context Manager
```python
from database import get_db_context

with get_db_context() as db:
    user = User(username="john", email="john@example.com")
    db.add(user)
    # Auto-commit and cleanup
```

#### Manual Session (Use with caution)
```python
from database import get_db_sync

db = get_db_sync()
try:
    # Your database operations
    pass
finally:
    db.close()
```

### Query Examples

#### Basic Queries
```python
# Get all users
users = db.query(User).all()

# Filter users
active_users = db.query(User).filter(User.is_active == True).all()

# Get user by ID
user = db.query(User).filter(User.id == 1).first()

# Count records
user_count = db.query(User).count()
```

#### Relationship Queries
```python
# Get user with posts
user = db.query(User).options(selectinload(User.posts)).filter(User.id == 1).first()

# Get posts with author
posts = db.query(Post).options(selectinload(Post.author)).all()
```

#### Complex Queries
```python
from sqlalchemy import and_, or_, desc

# Multiple conditions
users = db.query(User).filter(
    and_(
        User.is_active == True,
        or_(User.user_type == 'premium', User.is_verified == True)
    )
).order_by(desc(User.created_at)).limit(10).all()
```

## Database Migrations

### Using Alembic

#### Initialize Migrations
```bash
python db_manage.py init
```

#### Create New Migration
```bash
python db_manage.py create "Add new user fields"
```

#### Run Migrations
```bash
python db_manage.py migrate
```

#### View Migration History
```bash
python db_manage.py history
```

#### Check Current Revision
```bash
python db_manage.py current
```

### Manual Alembic Commands

#### Initialize
```bash
alembic init migrations
```

#### Create Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

#### Apply Migrations
```bash
alembic upgrade head
```

#### Rollback
```bash
alembic downgrade -1
```

## Database Health Monitoring

### Health Check Endpoint
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-01-11T17:30:00Z"
}
```

### Programmatic Health Check
```python
from database import check_database_health

health = check_database_health()
print(f"Database health: {health['overall']}")
```

## Performance Optimization

### SQLite Optimizations
- **WAL Mode**: Better concurrency and performance
- **Foreign Keys**: Proper constraint enforcement
- **Memory Cache**: Optimized for read-heavy workloads
- **Connection Pooling**: Efficient session management

### Query Optimization
- **Lazy Loading**: Default behavior for relationships
- **Eager Loading**: Use `selectinload()` for specific queries
- **Indexes**: Automatic on primary keys and unique fields
- **Batch Operations**: Efficient bulk operations

## Error Handling

### SQLAlchemy Errors
```python
from sqlalchemy.exc import SQLAlchemyError

try:
    # Database operations
    pass
except SQLAlchemyError as e:
    logger.error(f"Database error: {e}")
    # Handle database-specific errors
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle other errors
```

### Session Management
- **Automatic Rollback**: On errors
- **Connection Cleanup**: Proper resource management
- **Transaction Safety**: ACID compliance

## Development Workflow

### 1. Model Changes
1. Update models in `models.py`
2. Create migration: `python db_manage.py create "Description"`
3. Review generated migration file
4. Apply migration: `python db_manage.py migrate`

### 2. Database Reset (Development)
```bash
python db_manage.py reset
```

### 3. Testing
```bash
# Test database connection
python -c "from database import test_db_connection; print(test_db_connection())"

# Test health check
python -c "from database import check_database_health; print(check_database_health())"
```

## Production Considerations

### PostgreSQL Setup
```bash
# Install PostgreSQL dependencies
pip install psycopg2-binary

# Set environment variable
export DATABASE_URL="postgresql://user:password@localhost/careerconnect"
```

### Environment Configuration
```bash
# Production database URL
DATABASE_URL=postgresql://user:password@host:port/database

# Enable SQL debugging (development only)
SQLALCHEMY_ECHO=true

# Connection pool settings
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

### Monitoring
- **Connection Pool Status**: Monitor pool usage
- **Query Performance**: Enable SQL logging when needed
- **Health Checks**: Regular database health monitoring
- **Backup Strategy**: Implement proper backup procedures

## Troubleshooting

### Common Issues

#### Migration Errors
```bash
# Check current revision
alembic current

# View migration history
alembic history

# Reset to specific revision
alembic downgrade <revision_id>
```

#### Connection Issues
```python
from database import test_db_connection, get_db_info

# Test connection
if not test_db_connection():
    print("Connection failed")
    
# Get database info
print(get_db_info())
```

#### Session Errors
```python
# Check if session is valid
if db.is_active:
    # Session is valid
    pass
else:
    # Session is closed or invalid
    pass
```

### Debug Mode
```python
# Enable SQL logging
engine.echo = True

# Enable detailed error logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
```

## Best Practices

1. **Always use dependency injection** for database sessions in FastAPI
2. **Handle transactions properly** with try/except/finally blocks
3. **Use migrations** for all database schema changes
4. **Monitor query performance** and optimize slow queries
5. **Implement proper error handling** for database operations
6. **Use connection pooling** for production deployments
7. **Regular health checks** and monitoring
8. **Backup strategies** for production data

## Additional Resources

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Migration Guide](https://alembic.sqlalchemy.org/en/latest/)
- [FastAPI Database Integration](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLAlchemy Performance Tips](https://docs.sqlalchemy.org/en/20/faq/performance.html)
