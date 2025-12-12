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
        # Simple database test
        if test_db_connection():
            logger.info("Database connection successful")
            # Initialize database tables
            init_database()
            logger.info("Database tables initialized")
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
    description="A professional career development platform dashboard",
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

logger.info("Qrow IQ FastAPI application configured successfully")
