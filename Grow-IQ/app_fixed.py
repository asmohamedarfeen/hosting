import os
import time
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from config import settings
from database_enhanced import (
    test_db_connection, 
    get_db_info, 
    get_db, 
    init_database, 
    check_database_health, 
    cleanup_database
)
from security import SecurityMiddleware
from logging_config import app_logger, security_logger, performance_logger

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
    logger.info("Starting CareerConnect application...")
    
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
    
    logger.info("CareerConnect application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CareerConnect application...")
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

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Add trusted host middleware for production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
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
            "uptime": time.time() - app.start_time if hasattr(app, 'start_time') else 0
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e)
        }

# Performance monitoring middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log performance
    try:
        performance_logger.log_request_time(
            endpoint=str(request.url.path),
            method=request.method,
            duration=duration,
            status_code=response.status_code
        )
    except Exception as e:
        logger.warning(f"Performance logging failed: {e}")
    
    # Add performance header
    response.headers["X-Response-Time"] = str(duration)
    
    return response

# Templates with absolute path
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Import all route modules
from home_routes import router as home_router
from auth_routes import router as auth_router
from dashboard_routes import router as dashboard_router
from job_routes import router as job_router
from social_routes import router as social_router
from connection_routes import router as connection_router
from interview_routes import router as interview_router
from mockinterview_routes import router as mockinterview_router
from resume_tester_routes import router as resume_tester_router
from hr_routes import router as hr_router
from oauth_routes import router as oauth_router

# Include all routers
app.include_router(home_router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(job_router)
app.include_router(social_router)
app.include_router(connection_router)
app.include_router(interview_router)
app.include_router(mockinterview_router)
app.include_router(resume_tester_router)
app.include_router(hr_router)
app.include_router(oauth_router)

logger.info("CareerConnect FastAPI application configured successfully")
