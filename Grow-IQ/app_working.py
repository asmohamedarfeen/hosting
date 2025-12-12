import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from database_enhanced import (
    test_db_connection, 
    init_database, 
    check_database_health, 
    cleanup_database
)
from logging_config import app_logger

# Configure logging
logger = app_logger

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload configuration
UPLOAD_FOLDER = os.path.join(BASE_DIR, settings.UPLOAD_FOLDER.lstrip('./'))
MAX_CONTENT_LENGTH = settings.MAX_FILE_SIZE

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simple lifespan function that won't fail
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Qrow IQ application...")
    
    try:
        # Simple database test - don't fail if it doesn't work
        if test_db_connection():
            logger.info("Database connection successful")
            # Initialize database tables
            try:
                init_database()
                logger.info("Database tables initialized")
            except Exception as e:
                logger.warning(f"Database initialization warning: {e}")
        else:
            logger.warning("Database connection failed, but continuing...")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
        # Continue anyway - don't fail the app
    
    logger.info("Qrow IQ application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Qrow IQ application...")
    try:
        cleanup_database()
    except Exception as e:
        logger.warning(f"Database cleanup warning: {e}")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A professional networking platform dashboard",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files with absolute path
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Mount resume tester static files
app.mount("/resume-tester/static", StaticFiles(directory=os.path.join(BASE_DIR, "resume_tester", "static")), name="resume_tester_static")

# Mount mock interview static files
app.mount("/mock-interview/static", StaticFiles(directory=os.path.join(BASE_DIR, "mockinterviwe", "static")), name="mock_interview_static")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        db_health = check_database_health()
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "database": db_health,
            "uptime": 0
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e)
        }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Qrow IQ is running!", "status": "healthy"}

# Dashboard endpoint
@app.get("/dashboard")
async def dashboard():
    """Dashboard endpoint"""
    return {"message": "Dashboard is accessible", "status": "healthy"}

# Messaging endpoint
@app.get("/messaging")
async def messaging():
    """Messaging endpoint"""
    return {"message": "Messaging system is accessible", "status": "healthy"}



# Performance monitoring middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Add performance header
    response.headers["X-Response-Time"] = str(duration)
    
    return response

# Templates with absolute path
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# Import and include HR routes
try:
    from hr_routes import router as hr_router
    app.include_router(hr_router, prefix="/hr", tags=["HR"])
    logger.info("HR routes included successfully")
except Exception as e:
    logger.warning(f"Could not include HR routes: {e}")

# Network functionality has been removed
logger.info("Network functionality has been removed from this application")

# Import and include other essential routes
try:
    from home_routes import router as home_router
    app.include_router(home_router, tags=["Home"])
    logger.info("Home routes included successfully")
except Exception as e:
    logger.warning(f"Could not include home routes: {e}")

try:
    from auth_routes import router as auth_router
    app.include_router(auth_router, tags=["Authentication"])
    logger.info("Authentication routes included successfully")
except Exception as e:
    logger.warning(f"Could not include auth routes: {e}")

try:
    from connection_routes import router as connection_router
    app.include_router(connection_router, prefix="/connections", tags=["Connections"])
    logger.info("Connection routes included successfully")
except Exception as e:
    logger.warning(f"Could not include connection routes: {e}")

try:
    from job_routes import router as job_router
    app.include_router(job_router, prefix="/jobs", tags=["Jobs"])
    logger.info("Job routes included successfully")
except Exception as e:
    logger.warning(f"Could not include job routes: {e}")

# Import and include social routes
try:
    from social_routes import router as social_router
    app.include_router(social_router, prefix="/social", tags=["Social"])
    logger.info("Social routes included successfully")
except Exception as e:
    logger.warning(f"Could not include social routes: {e}")

# Import and include API routes
try:
    from api_routes import router as api_router
    app.include_router(api_router, tags=["API"])
    logger.info("API routes included successfully")
except Exception as e:
    logger.warning(f"Could not include API routes: {e}")

# Import and include streak routes
try:
    from streak_routes import router as streak_router
    app.include_router(streak_router, tags=["Streaks"])
    logger.info("Streak routes included successfully")
except Exception as e:
    logger.warning(f"Could not include streak routes: {e}")

# Import and include test routes
try:
    from test_routes import test_router
    app.include_router(test_router, tags=["Test"])
    logger.info("Test routes included successfully")
except Exception as e:
    logger.warning(f"Could not include test routes: {e}")

logger.info("Qrow IQ FastAPI application configured successfully")
