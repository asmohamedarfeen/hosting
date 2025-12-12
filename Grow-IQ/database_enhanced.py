import os
import logging
from sqlalchemy import create_engine, event, text, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DisconnectionError
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any
from config import settings
import time

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Enhanced database manager with connection pooling and health monitoring"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.metadata = MetaData()
        self.connection_health = {"status": "unknown", "last_check": None, "error_count": 0}
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize database engine with appropriate configuration"""
        try:
            if "sqlite" in settings.DATABASE_URL:
                # SQLite configuration (development)
                self.engine = create_engine(
                    settings.DATABASE_URL,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                    echo=settings.DEBUG,
                    future=True
                )
                logger.info("SQLite engine initialized (development mode)")
            else:
                # PostgreSQL/MySQL configuration (production)
                self.engine = create_engine(
                    settings.DATABASE_URL,
                    poolclass=QueuePool,
                    pool_size=20,
                    max_overflow=30,
                    pool_recycle=300,
                    pool_pre_ping=True,
                    pool_timeout=30,
                    echo=settings.DEBUG,
                    future=True
                )
                logger.info("Production database engine initialized")
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Test connection
            self._test_connection()
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    def _test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                if "sqlite" in settings.DATABASE_URL:
                    result = conn.execute(text("SELECT 1"))
                else:
                    result = conn.execute(text("SELECT 1"))
                result.fetchone()
                
                self.connection_health = {
                    "status": "healthy",
                    "last_check": time.time(),
                    "error_count": 0
                }
                logger.info("Database connection test successful")
                
        except Exception as e:
            self.connection_health = {
                "status": "unhealthy",
                "last_check": time.time(),
                "error_count": self.connection_health["error_count"] + 1
            }
            logger.error(f"Database connection test failed: {e}")
            raise
    
    def get_db(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @contextmanager
    def get_db_context(self) -> Generator[Session, None, None]:
        """Context manager for database sessions with automatic commit/rollback"""
        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise
        finally:
            db.close()
    
    def get_db_sync(self) -> Session:
        """Get a database session for synchronous operations"""
        return self.SessionLocal()
    
    def check_health(self) -> Dict[str, Any]:
        """Check database health status"""
        try:
            with self.engine.connect() as conn:
                if "sqlite" in settings.DATABASE_URL:
                    result = conn.execute(text("PRAGMA database_list"))
                    db_info = {"type": "SQLite", "status": "connected"}
                else:
                    result = conn.execute(text("SELECT version()"))
                    version = result.fetchone()[0]
                    db_info = {"type": "PostgreSQL/MySQL", "status": "connected", "version": version}
                
                                    # Check connection pool status
                if hasattr(self.engine.pool, 'size'):
                    pool_status = {
                        "pool_size": self.engine.pool.size(),
                        "checked_in": self.engine.pool.checkedin(),
                        "checked_out": self.engine.pool.checkedout(),
                        "overflow": self.engine.pool.overflow()
                    }
                else:
                    # SQLite StaticPool doesn't have these methods
                    pool_status = {
                        "pool_size": "N/A (SQLite)",
                        "checked_in": "N/A (SQLite)",
                        "checked_out": "N/A (SQLite)",
                        "overflow": "N/A (SQLite)"
                    }
                
                self.connection_health = {
                    "status": "healthy",
                    "last_check": time.time(),
                    "error_count": 0
                }
                
                return {
                    "overall": "healthy",
                    "database": db_info,
                    "pool": pool_status,
                    "last_check": time.time()
                }
                
        except Exception as e:
            self.connection_health = {
                "status": "unhealthy",
                "last_check": time.time(),
                "error_count": self.connection_health["error_count"] + 1
            }
            
            logger.error(f"Database health check failed: {e}")
            return {
                "overall": "unhealthy",
                "error": str(e),
                "last_check": time.time(),
                "error_count": self.connection_health["error_count"]
            }
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information"""
        if "sqlite" in settings.DATABASE_URL:
            return {
                "type": "SQLite",
                "path": settings.DATABASE_URL.replace("sqlite:///", ""),
                "status": self.connection_health["status"]
            }
        else:
            # Extract connection details from URL
            url_parts = settings.DATABASE_URL.replace("://", "://").split("@")
            if len(url_parts) > 1:
                credentials = url_parts[0].split("://")[1]
                host_port = url_parts[1].split("/")[0]
                database = url_parts[1].split("/")[1].split("?")[0]
                
                return {
                    "type": "PostgreSQL/MySQL",
                    "host": host_port.split(":")[0],
                    "port": host_port.split(":")[1] if ":" in host_port else "default",
                    "database": database,
                    "status": self.connection_health["status"]
                }
            return {
                "type": "Unknown",
                "status": self.connection_health["status"]
            }
    
    def cleanup(self):
        """Cleanup database connections"""
        try:
            if self.engine:
                self.engine.dispose()
                logger.info("Database connections cleaned up")
        except Exception as e:
            logger.error(f"Error during database cleanup: {e}")

# Create global database manager instance
db_manager = DatabaseManager()

# Convenience functions for backward compatibility
def get_db() -> Generator[Session, None, None]:
    """Get database session (backward compatibility)"""
    db = db_manager.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_context() -> Generator[Session, None, None]:
    """Get database context (backward compatibility)"""
    return db_manager.get_db_context()

def get_db_sync() -> Session:
    """Get database session synchronously (backward compatibility)"""
    return db_manager.get_db_sync()

def test_db_connection() -> bool:
    """Test database connection (backward compatibility)"""
    try:
        health = db_manager.check_health()
        return health["overall"] == "healthy"
    except Exception:
        return False

def get_db_info() -> Dict[str, Any]:
    """Get database info (backward compatibility)"""
    return db_manager.get_connection_info()

def check_database_health() -> Dict[str, Any]:
    """Check database health (backward compatibility)"""
    return db_manager.check_health()

def cleanup_database():
    """Cleanup database (backward compatibility)"""
    db_manager.cleanup()

def init_database():
    """Initialize database tables (backward compatibility)"""
    try:
        # Import all model modules to ensure tables are registered with Base metadata
        from models import Base  # core models
        try:
            import message_models  # registers Message model
        except Exception as _:
            # If optional modules fail to import, continue with core models
            pass
        Base.metadata.create_all(bind=db_manager.engine)
        logger.info("Database tables initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        return False
