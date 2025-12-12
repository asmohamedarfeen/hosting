import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError
import logging
from contextlib import contextmanager
from typing import Generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "dashboard.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")

# Create engine with better configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    pool_recycle=300,
    pool_pre_ping=True,
    echo=False,  # Set to True for SQL debugging
    future=True,
    # Connection pool settings (only for non-SQLite databases)
    **({"pool_size": 20, "max_overflow": 30} if "sqlite" not in DATABASE_URL else {})
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error in database session: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error in database session: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_db_sync() -> Session:
    """Get a database session for synchronous operations (use with caution)"""
    return SessionLocal()

# Function to test database connection
def test_db_connection() -> bool:
    """Test database connection and return True if successful"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()  # Consume the result
            return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error testing database connection: {e}")
        return False

# Function to get database info
def get_db_info() -> dict:
    """Get database information and status"""
    try:
        with engine.connect() as conn:
            if "sqlite" in DATABASE_URL:
                result = conn.execute(text("PRAGMA database_list"))
                return {"type": "SQLite", "status": "connected", "path": DATABASE_PATH}
            else:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                return {"type": "PostgreSQL", "status": "connected", "version": version}
    except SQLAlchemyError as e:
        return {"type": "Unknown", "status": f"error: {e}"}
    except Exception as e:
        return {"type": "Unknown", "status": f"unexpected error: {e}"}

def check_database_health() -> dict:
    """Comprehensive database health check"""
    health_status = {
        "connection": False,
        "tables": False,
        "overall": "unhealthy"
    }
    
    try:
        # Test connection
        if test_db_connection():
            health_status["connection"] = True
            
            # Test basic table operations
            with engine.connect() as conn:
                # Try to access a table (users table should exist)
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
                if result.fetchone():
                    health_status["tables"] = True
                    health_status["overall"] = "healthy"
                else:
                    health_status["overall"] = "partially_healthy"
                    
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["overall"] = "unhealthy"
    
    return health_status

def close_database_connections():
    """Close all database connections (useful for cleanup)"""
    try:
        engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

# Event listeners for better SQLAlchemy integration
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance and foreign key support"""
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log SQL statements when echo is enabled"""
    if engine.echo:
        logger.debug(f"Executing SQL: {statement}")

# Database initialization function
def init_database():
    """Initialize database tables"""
    try:
        from models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        return False

# Cleanup function for application shutdown
def cleanup_database():
    """Cleanup database resources"""
    try:
        close_database_connections()
        logger.info("Database cleanup completed")
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")
