import os
import time
import logging
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from config import settings
from database_enhanced import (
    test_db_connection, 
    get_db_info, 
    init_database, 
    check_database_health,
    cleanup_database,
    get_db
)
from sqlalchemy.orm import Session
from models import User, ResumeTestResult, ResumeathonParticipant
from auth_utils import get_current_user
from security import SecurityMiddleware
from logging_config import app_logger, security_logger, performance_logger
from pydantic import BaseModel
import speech_recognition as sr
import base64
import tempfile
import traceback
import wave
import audioop
import re
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional, Dict, Set

# Configure logging
logger = app_logger

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload configuration
UPLOAD_FOLDER = os.path.join(BASE_DIR, settings.UPLOAD_FOLDER.lstrip('./'))
MAX_CONTENT_LENGTH = settings.MAX_FILE_SIZE

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Qrow IQ application...")
    
    # Test database connection
    if test_db_connection():
        logger.info("Database connection successful")
        db_info = get_db_info()
        logger.info(f"Database: {db_info}")
        
        # Check database health
        health_status = check_database_health()
        logger.info(f"Database health: {health_status}")
        
        if health_status["overall"] == "unhealthy":
            logger.warning("Database health check failed, attempting to initialize...")
            if not init_database():
                logger.error("Failed to initialize database tables")
                raise RuntimeError("Cannot initialize database tables")
    else:
        logger.error("Database connection failed!")
        raise RuntimeError("Cannot connect to database")
    
    # Create database tables if they don't exist
    try:
        if not init_database():
            logger.warning("Database tables may not be properly initialized")
        else:
            logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    logger.info("Qrow IQ application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Qrow IQ application...")
    cleanup_database()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Qrow IQ - Professional career development platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Add trusted host middleware for production
# Note: Disabled for Render deployment - Render uses dynamic hostnames
# If you need this, add your Render domain to ALLOWED_HOSTS environment variable
# Example: ALLOWED_HOSTS=hosting-ujm7.onrender.com,your-domain.com
if settings.ENVIRONMENT == "production" and settings.ALLOWED_HOSTS:
    # Only enable if ALLOWED_HOSTS is explicitly set and not just defaults
    allowed_hosts = [h.strip() for h in settings.ALLOWED_HOSTS if h.strip() and h.strip() not in ["localhost", "127.0.0.1", "0.0.0.0"]]
    if allowed_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts
        )
        logger.info(f"TrustedHostMiddleware enabled with hosts: {allowed_hosts}")
    else:
        logger.info("TrustedHostMiddleware disabled - no production hosts configured")
else:
    logger.info("TrustedHostMiddleware disabled - not in production or ALLOWED_HOSTS not set")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend (Vite) build directory - matches fronted/vite.config.ts outDir (dist/public)
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, "fronted", "dist", "public")
FRONTEND_ASSETS_DIR = os.path.join(FRONTEND_DIST_DIR, "assets")

# Mount Vite assets if build exists
if os.path.isdir(FRONTEND_ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS_DIR), name="frontend_assets")
    logger.info(f"Mounted frontend assets from {FRONTEND_ASSETS_DIR} at /assets")

# Mount static files with absolute path
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Mount landing page assets
app.mount("/landing", StaticFiles(directory=os.path.join(BASE_DIR, "static", "landing")), name="landing")

# Mount resume tester static files (if directory exists)
_RESUME_TESTER_STATIC_DIR = os.path.join(BASE_DIR, "resume_tester", "static")
if os.path.isdir(_RESUME_TESTER_STATIC_DIR):
    app.mount("/resume-tester/static", StaticFiles(directory=_RESUME_TESTER_STATIC_DIR), name="resume_tester_static")
    logger.info(f"Mounted resume tester static files from {_RESUME_TESTER_STATIC_DIR} at /resume-tester/static")
else:
    logger.warning(f"Resume tester static directory not found: {_RESUME_TESTER_STATIC_DIR}")

# MOCK INTERVIEW MODULE - DISCONNECTED (can be reconnected in future)
# Mount mock interview static files (if directory exists)
# MOCK_INTERVIEW_STATIC_DIR = os.path.join(BASE_DIR, "mockinterviwe", "static")
# if os.path.isdir(MOCK_INTERVIEW_STATIC_DIR):
#     app.mount("/mock-interview/static", StaticFiles(directory=MOCK_INTERVIEW_STATIC_DIR), name="mock_interview_static")
#     logger.info(f"Mounted mock interview static files from {MOCK_INTERVIEW_STATIC_DIR} at /mock-interview/static")
# else:
#     logger.warning(f"Mock interview static directory not found: {MOCK_INTERVIEW_STATIC_DIR}")

# Mount uploaded message UI static directory (if present)
try:
    MESSAGE_UI_DIR = os.path.join(BASE_DIR, "message", "message", "message")
    if os.path.isdir(MESSAGE_UI_DIR):
        app.mount("/message/static", StaticFiles(directory=MESSAGE_UI_DIR), name="message_static")
        logger.info("Message UI static directory mounted at /message/static")
except Exception as e:
    logger.warning(f"Could not mount message UI static directory: {e}")

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

# Redirect old default avatar path to correct location
@app.get("/default-avatar.svg")
async def redirect_default_avatar():
    """Redirect old default avatar path to correct location"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/uploads/default-avatar.svg", status_code=301)

# Performance monitoring middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log performance
    performance_logger.log_request_time(
        endpoint=str(request.url.path),
        method=request.method,
        duration=duration,
        status_code=response.status_code
    )
    
    # Add performance header
    response.headers["X-Response-Time"] = str(duration)
    
    return response

# Templates with absolute path
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Store templates in app state for global access
app.state.templates = templates

# Global template access function
def get_templates():
    """Get templates from app state"""
    return app.state.templates

# Make templates globally accessible
app.templates = templates

# Import routes after app creation to avoid circular imports
from auth_routes import router as auth_router
from dashboard_routes import router as dashboard_router
from home_routes import router as home_router
from api_routes import router as api_router

from connection_routes import router as connection_router
from social_routes import router as social_router
from job_routes import router as job_router
from interview_routes import router as interview_router
from hr_routes import router as hr_router
from resume_tester_routes import router as resume_tester_router
# MOCK INTERVIEW MODULE - DISCONNECTED (can be reconnected in future)
# from mockinterview_routes import router as mockinterview_router
from test_results_routes import router as test_results_router
from oauth_routes import router as oauth_router
from profile_api_routes import router as profile_api_router
from message_routes import router as message_router
from message_api_routes import router as message_api_router, router_compat as message_api_router_compat
from message_routes import router as new_message_router
from workshop_routes import router as workshop_router
from admin_routes import router as admin_router

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(home_router, tags=["Home"])
app.include_router(api_router, tags=["API"])

app.include_router(connection_router, tags=["Connections"])
app.include_router(social_router, tags=["Social"])
app.include_router(job_router, prefix="/api", tags=["Jobs"])
app.include_router(interview_router, tags=["Interview"])
app.include_router(hr_router, tags=["HR Management"])
app.include_router(resume_tester_router, tags=["Resume Tester"])
# MOCK INTERVIEW MODULE - DISCONNECTED (can be reconnected in future)
# app.include_router(mockinterview_router, tags=["Mock Interview"])

# Catch-all route to handle /mock-interview requests when module is disabled
@app.get("/mock-interview")
@app.get("/mock-interview/")
@app.get("/mock-interview/{path:path}")
async def mock_interview_disabled():
    """Mock Interview module is currently disabled"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=503,
        content={
            "error": "Mock Interview module is currently disabled",
            "message": "This feature is temporarily unavailable. Please check back later."
        }
    )
app.include_router(test_results_router, tags=["Test Results"])
app.include_router(oauth_router, tags=["OAuth"])
app.include_router(profile_api_router, tags=["Profile API"])
app.include_router(message_router, tags=["Messages"])
app.include_router(message_api_router, tags=["Message API Adapter"])
app.include_router(message_api_router_compat, tags=["Message API Compat"])
app.include_router(new_message_router, tags=["New Messages"])
app.include_router(workshop_router, tags=["Workshops"])
app.include_router(admin_router, tags=["Admin"])

# -------- Cultural Events minimal API (in-memory) --------
class CulturalEventIn(BaseModel):
    title: str
    description: Optional[str] = None
    date: str
    time: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None

_CULTURAL_EVENTS: List[dict] = []
_CULTURAL_REGISTRATIONS: Dict[int, List[int]] = {}

@app.post("/api/cultural-events")
async def create_cultural_event(
    payload: CulturalEventIn,
    current_user: User = Depends(get_current_user)
):
    user_type = (getattr(current_user, 'user_type', '') or '').lower()
    role = (getattr(current_user, 'role', '') or '').lower()
    is_hr = getattr(current_user, 'is_hr', False) or user_type in ['hr','admin'] or role in ['hr','admin']
    if not is_hr:
        raise HTTPException(status_code=403, detail="Only HR can create cultural events")

    event_id = len(_CULTURAL_EVENTS) + 1
    organizer_name = getattr(current_user, 'full_name', None) or getattr(current_user, 'username', f"user-{current_user.id}")
    event = {
        'id': event_id,
        'title': payload.title.strip(),
        'description': (payload.description or '').strip(),
        'date': payload.date.strip(),
        'time': (payload.time or '').strip(),
        'location': (payload.location or '').strip(),
        'category': (payload.category or 'festival').strip(),
        'organizer': organizer_name,
        'organizer_id': current_user.id,
        'attendees': 0,
        'maxAttendees': 0,
        'isUpcoming': True,
        'isFeatured': False,
        'image': '/figmaAssets/cultural-fest.jpg',
        'tags': []
    }
    _CULTURAL_EVENTS.append(event)
    _CULTURAL_REGISTRATIONS[event_id] = []
    return { 'success': True, 'event': event }

@app.get("/api/cultural-events/{event_id}/participants")
async def get_cultural_event_participants(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = next((e for e in _CULTURAL_EVENTS if e['id'] == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    is_admin = (getattr(current_user, 'user_type', '') == 'admin')
    if event.get('organizer_id') != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view participants")

    ids = _CULTURAL_REGISTRATIONS.get(event_id, [])
    users = []
    if ids:
        users = db.query(User).filter(User.id.in_(ids)).all()

    return {
        'participants': [
            {
                'id': u.id,
                'full_name': getattr(u, 'full_name', None),
                'email': getattr(u, 'email', None),
                'username': getattr(u, 'username', None)
            } for u in users
        ],
        'count': len(ids)
    }

# Global exception handler for authentication errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions, especially authentication errors"""
    
    # Check if this is an API request
    is_api_request = (
        request.url.path.startswith("/api/") or
        "application/json" in request.headers.get("accept", "") or
        "application/json" in request.headers.get("content-type", "")
    )
    
    if exc.status_code == 401:  # Unauthorized
        if is_api_request:
            # Return JSON response for API requests
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "Authentication required", "code": "AUTH_REQUIRED"}
            )
        else:
            # Redirect to login page for browser requests
            return RedirectResponse(url="/login", status_code=303)
            
    elif exc.status_code == 403:  # Forbidden
        if is_api_request:
            # Return JSON response for API requests
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": "Access forbidden", "code": "ACCESS_FORBIDDEN"}
            )
        else:
            # Redirect to login page for browser requests
            return RedirectResponse(url="/login", status_code=303)
    
    # For other HTTP errors
    if is_api_request:
        # Return JSON response for API requests
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.detail, "code": f"HTTP_{exc.status_code}"}
        )
    else:
        # Return HTML error page for browser requests
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Error {exc.status_code}</title></head>
                <body>
                    <h1>Error {exc.status_code}</h1>
                    <p>{exc.detail}</p>
                    <a href="/login">Go to Login</a>
                </body>
            </html>
            """,
            status_code=exc.status_code
        )

# Root route - serve public landing page first
@app.get("/")
async def root():
    """Serve the landing page for everyone."""
    try:
        landing_index_path = os.path.join(BASE_DIR, "static", "landing", "index.html")
        if os.path.exists(landing_index_path):
            return FileResponse(landing_index_path, media_type="text/html")
        # Fallback to SPA index
        index_path = os.path.join(FRONTEND_DIST_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path, media_type="text/html")
    except Exception as e:
        logger.warning(f"Could not serve landing page: {e}")
    
    # Fallback: Return a simple JSON response instead of redirecting to localhost
    return JSONResponse(
        content={
            "message": "Grow-IQ API is running!",
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "docs": "/docs",
            "health": "/health"
        },
        status_code=200
    )

# Resume analyzer endpoint (optional authentication)
@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    request: Request = None
):
    """Resume analyzer endpoint - works with or without authentication"""
    try:
        if file.content_type != 'application/pdf':
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
        # Read file content
        file_content = await file.read()
        
        # Save uploaded file to a temp location for analysis
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name
        
        # Record start time for analysis duration
        from datetime import datetime
        start_time = datetime.now()
        
        # Import and use the ATS scorer
        from resume_tester.ats_resume_scorer import ATSResumeScorer
        scorer = ATSResumeScorer(api_key="AIzaSyA3f8izcUDNQTik3utegfZ5bKvxeG0vwq8")
        result = scorer.score_resume(tmp_path)
        
        # Calculate analysis duration
        end_time = datetime.now()
        analysis_duration = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
        
        # Clean up temp file
        try:
            import os
            os.unlink(tmp_path)
        except OSError:
            pass  # File already deleted or doesn't exist
        
        # Check if result is a string (error) or dictionary (success)
        if isinstance(result, str):
            # If it's an error string, return it as an error response
            raise HTTPException(status_code=500, detail=result)
        
        # Add analysis metadata to dictionary result
        result['analysis_duration_ms'] = analysis_duration
        result['timestamp'] = datetime.now().isoformat()
        
        # Try to save results to database if user is authenticated
        try:
            user_id = None
            
            # Get database session for user lookup
            db = next(get_db())
            
            # Try to get user from session token (cookie-based auth)
            session_token = request.cookies.get("session_token") if request else None
            if session_token:
                try:
                    from auth_utils import get_user_from_session
                    session_data = get_user_from_session(session_token, db)
                    if isinstance(session_data, dict):
                        user_id = session_data.get('user_id')
                        logger.info(f"Found user_id {user_id} from session token")
                except Exception as session_error:
                    logger.warning(f"Failed to get user from session: {session_error}")
                    user_id = None
            
            # If no user from session, try to get from Authorization header (API token)
            if not user_id and request:
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    try:
                        from auth_utils import get_current_user_from_token
                        token = auth_header.replace("Bearer ", "")
                        # This would require implementing token-based auth if needed
                    except Exception:
                        pass

            if user_id:
                logger.info(f"Saving resume test result for user {user_id}")
                # Persist the uploaded file to a durable location
                import os as _os
                import time as _time
                base_dir = _os.path.dirname(_os.path.abspath(__file__))
                resume_dir = _os.path.join(base_dir, "resume_data")
                _os.makedirs(resume_dir, exist_ok=True)
                safe_name = (file.filename or "unknown.pdf").replace("/", "_").replace("\\", "_")
                stored_filename = f"{int(_time.time())}_{safe_name}"
                stored_path = _os.path.join(resume_dir, stored_filename)
                try:
                    with open(stored_path, 'wb') as f_out:
                        f_out.write(file_content)
                except Exception as write_err:
                    logger.error(f"Failed to persist resume file: {write_err}")
                    stored_path = safe_name  # fallback

                # Create ResumeTestResult record
                from datetime import datetime as dt
                resume_result = ResumeTestResult(
                    user_id=user_id,
                    filename=file.filename or "unknown.pdf",
                    filepath=stored_path,
                    content_quality_score=result['content_quality']['score'],
                    content_quality_explanation=result['content_quality']['explanation'],
                    skills_match_score=result['skills_match']['score'],
                    skills_match_explanation=result['skills_match']['explanation'],
                    experience_achievements_score=result['experience_achievements']['score'],
                    experience_achievements_explanation=result['experience_achievements']['explanation'],
                    format_structure_score=result['format_structure']['score'],
                    format_structure_explanation=result['format_structure']['explanation'],
                    education_certifications_score=result['education_certifications']['score'],
                    education_certifications_explanation=result['education_certifications']['explanation'],
                    total_score=result['total_score'],
                    analysis_duration_ms=int(analysis_duration),
                    file_size=len(file_content),
                    file_type='PDF',
                    analysis_timestamp=dt.now()  # Explicitly set timestamp
                )

                # Add overall grade based on score
                if result['total_score'] >= 90:
                    resume_result.overall_grade = 'A+'
                elif result['total_score'] >= 80:
                    resume_result.overall_grade = 'A'
                elif result['total_score'] >= 70:
                    resume_result.overall_grade = 'B+'
                elif result['total_score'] >= 60:
                    resume_result.overall_grade = 'B'
                elif result['total_score'] >= 50:
                    resume_result.overall_grade = 'C+'
                elif result['total_score'] >= 40:
                    resume_result.overall_grade = 'C'
                else:
                    resume_result.overall_grade = 'D'

                # Save to database (using the same db session)
                db.add(resume_result)
                db.commit()
                db.refresh(resume_result)

                logger.info(f"Resume analysis saved to database for user {user_id}, result ID: {resume_result.id}")
                
                # Update ResumeathonParticipant if user has joined the leaderboard
                try:
                    participant = db.query(ResumeathonParticipant).filter(
                        ResumeathonParticipant.user_id == user_id,
                        ResumeathonParticipant.is_active == True
                    ).first()
                    
                    if participant:
                        # Update to use the latest resume test result
                        participant.resume_test_result_id = resume_result.id
                        db.commit()
                        logger.info(f"Updated ResumeathonParticipant for user {user_id} to use latest score: {result['total_score']}")
                except Exception as update_error:
                    logger.warning(f"Failed to update ResumeathonParticipant: {update_error}")
                    # Don't fail the whole operation if participant update fails
            else:
                logger.info("User not authenticated, skipping database save")

        except Exception as db_error:
            logger.error(f"Error saving resume results to database: {str(db_error)}")
            # Do not fail the request if database save fails
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

# Get user's resume scores
@app.get("/api/resume-scores")
async def get_resume_scores(
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Get user's resume test scores"""
    try:
        # Check if user is authenticated
        user_id = None
        if request:
            session_token = request.cookies.get("session_token")
            if session_token:
                try:
                    from auth_utils import get_user_from_session
                    session_data = get_user_from_session(session_token)
                    if session_data:
                        user_id = session_data.get('user_id')
                except:
                    user_id = None
        
        if not user_id:
            # Return empty results for unauthenticated users
            return JSONResponse(content={
                'resume_scores': [],
                'summary': {
                    'total_tests': 0,
                    'average_score': 0,
                    'best_score': 0,
                    'latest_score': 0
                }
            })
        
        # Get all resume test results for the user, ordered by most recent first
        resume_results = db.query(ResumeTestResult).filter(
            ResumeTestResult.user_id == user_id
        ).order_by(ResumeTestResult.analysis_timestamp.desc()).all()
        
        # Calculate average score
        if resume_results:
            total_scores = [result.total_score for result in resume_results]
            average_score = sum(total_scores) / len(total_scores)
            best_score = max(total_scores)
            latest_score = resume_results[0].total_score
        else:
            average_score = 0
            best_score = 0
            latest_score = 0
        
        # Format results for frontend
        formatted_results = []
        for result in resume_results:
            formatted_results.append({
                'id': result.id,
                'filename': result.filename,
                'total_score': result.total_score,
                'overall_grade': result.overall_grade,
                'analysis_timestamp': result.analysis_timestamp.isoformat(),
                'analysis_duration_ms': result.analysis_duration_ms
            })
        
        return JSONResponse(content={
            'resume_scores': formatted_results,
            'summary': {
                'total_tests': len(resume_results),
                'average_score': round(average_score, 1),
                'best_score': best_score,
                'latest_score': latest_score
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching resume scores: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching resume scores: {str(e)}")

# MOCK INTERVIEW MODULE - DISCONNECTED (can be reconnected in future)
# Mock Interview scores summary for current user
# @app.get("/api/mock-scores")
# async def get_mock_scores(
#     request: Request,
#     db: Session = Depends(get_db)
# ):
#     """Return mock interview score summary and recent sessions for current user."""
#     try:
#         # Identify user via session cookie
#         session_token = request.cookies.get("session_token")
#         if not session_token:
#             return JSONResponse(content={
#                 'sessions': [],
#                 'summary': {
#                     'total_sessions': 0,
#                     'average_score': 0,
#                     'best_score': 0,
#                     'latest_score': 0
#                 }
#             })
#         from auth_utils import get_user_from_session as _get_user_from_session
#         session_data = _get_user_from_session(session_token, db)
#         if not session_data:
#             return JSONResponse(content={
#                 'sessions': [],
#                 'summary': {
#                     'total_sessions': 0,
#                     'average_score': 0,
#                     'best_score': 0,
#                     'latest_score': 0
#                 }
#             })
#
#         user_id = session_data.get('user_id')
#         # Import model locally to avoid circular imports at module import time
#         from models import MockInterviewSession
#
#         # Fetch user's sessions ordered by most recent
#         sessions = db.query(MockInterviewSession) \
#             .filter(MockInterviewSession.user_id == user_id) \
#             .order_by((MockInterviewSession.ended_at.is_(None)).asc(), MockInterviewSession.ended_at.desc()) \
#             .limit(20).all()
#
#         # Compute summary
#         scores = [int(getattr(s, 'score_overall', 0) or 0) for s in sessions if getattr(s, 'score_overall', None) is not None]
#         total = len(scores)
#         average = int(sum(scores)/total) if total > 0 else 0
#         best = max(scores) if scores else 0
#         latest = int(scores[0]) if scores else 0
#
#         # Serialize minimal session info
#         serialized = [
#             {
#                 'id': getattr(s, 'id', None),
#                 'session_uuid': getattr(s, 'session_uuid', None),
#                 'job_role': getattr(s, 'job_role', ''),
#                 'ended_at': getattr(s, 'ended_at', None).isoformat() if getattr(s, 'ended_at', None) else None,
#                 'overall': int(getattr(s, 'score_overall', 0) or 0),
#                 'accuracy': int(getattr(s, 'score_accuracy', 0) or 0),
#                 'clarity': int(getattr(s, 'score_clarity', 0) or 0),
#                 'relevance': int(getattr(s, 'score_relevance', 0) or 0)
#             }
#             for s in sessions
#         ]
#
#         return JSONResponse(content={
#             'sessions': serialized,
#             'summary': {
#                 'total_sessions': total,
#                 'average_score': average,
#                 'best_score': best,
#                 'latest_score': latest
#             }
#         })
#     except Exception as e:
#         logger.error(f"Error fetching mock interview scores: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error fetching mock scores: {str(e)}")

# Auto-login for testing
@app.get("/auto-login")
async def auto_login():
    """Auto login with first user for testing"""
    from models import User
    from database_enhanced import get_db
    from auth_utils import create_session_token
    
    db = next(get_db())
    user = db.query(User).first()
    
    if not user:
        return HTMLResponse("No users found. Please create a user first.")
    
    token = create_session_token(user.id, db)
    
    response = RedirectResponse(url="/test_profile_update.html", status_code=303)
    response.set_cookie("session_token", token, path="/")
    return response

# Test profile update page
@app.get("/test_profile_update.html")
async def test_profile_page():
    """Serve the profile test page"""
    with open("test_profile_update.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

# Root endpoint - let home routes handle this
# The home routes will check authentication and redirect if needed

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db_status = test_db_connection()
        return {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "timestamp": "2025-08-11T17:30:00Z"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2025-08-11T17:30:00Z"
        }

# Debug page endpoint
@app.get("/debug")
async def debug_page():
    """Debug page for testing login functionality"""
    with open("debug_login.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

# Test posting page endpoint
@app.get("/test-posting")
async def test_posting_page():
    """Test page for testing posting functionality"""
    with open("test_posting.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

# Test image posting page endpoint
@app.get("/test-image-posting")
async def test_image_posting_page():
    """Test page for testing image posting functionality"""
    with open("test_image_posting.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

# Test interview interface page endpoint
@app.get("/test-interview")
async def test_interview_interface_page():
    """Test page for testing interview interface functionality"""
    with open("test_interview_interface.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

# Test API status page endpoint
@app.get("/test-api-status")
async def test_api_status_page():
    """Test page for testing API status and fallback functionality"""
    with open("test_api_status.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

# Debug HR access endpoint
@app.get("/debug-hr-access")
async def debug_hr_access():
    """Debug endpoint to test HR access without authentication"""
    try:
        from models import User
        
        db = next(get_db())
        users = db.query(User).filter(User.user_type == 'domain').limit(5).all()
        
        debug_info = []
        for user in users:
            try:
                debug_info.append({
                    "username": user.username,
                    "email": user.email,
                    "user_type": user.user_type,
                    "is_verified": user.is_verified,
                    "domain_id": user.domain_id,
                    "hr_id": user.hr_id,
                    "is_hr_user": user.is_hr_user(),
                    "access_type": user.get_access_type(),
                    "has_domain_access": user.has_domain_access()
                })
            except Exception as e:
                debug_info.append({
                    "username": user.username,
                    "error": str(e)
                })
        
        db.close()
        
        return {
            "status": "success",
            "message": "HR access debug information",
            "users": debug_info
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }

# Test resume upload fix page endpoint
@app.get("/test-resume-upload")
async def test_resume_upload_page():
    """Test page for verifying resume upload fix"""
    with open("test_resume_upload.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

# Test mock interview integration page endpoint
@app.get("/test-mock-interview")
async def test_mock_interview_page():
    """Test page for verifying mock interview integration"""
    with open("test_mock_interview.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

# Profile Management API Routes
@app.post("/api/update-profile")
async def update_profile(request: Request):
    """Update user profile information"""
    try:
        # Get current user from session
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Get user from session
        from auth_utils import get_user_from_session
        session_data = get_user_from_session(session_token)
        if not session_data:
            raise HTTPException(status_code=401, detail="Session expired")
        
        user_id = session_data['user_id']
        
        # Get profile data from request
        profile_data = await request.json()
        
        # Update user profile in database
        from models import User
        
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user fields
        if 'first_name' in profile_data and 'last_name' in profile_data:
            user.set_names(profile_data['first_name'], profile_data['last_name'])
        if 'title' in profile_data:
            user.title = profile_data['title']
        if 'company' in profile_data:
            user.company = profile_data['company']
        if 'industry' in profile_data:
            user.industry = profile_data['industry']
        if 'experience' in profile_data:
            user.experience = profile_data['experience']
        if 'experience_years' in profile_data:
            user.experience_years = profile_data['experience_years']
        if 'bio' in profile_data:
            user.bio = profile_data['bio']
        if 'skills' in profile_data:
            user.skills = profile_data['skills']
        if 'interests' in profile_data:
            user.interests = profile_data['interests']
        if 'education' in profile_data:
            user.education = profile_data['education']
        if 'certifications' in profile_data:
            user.certifications = profile_data['certifications']
        if 'phone' in profile_data:
            user.phone = profile_data['phone']
        if 'location' in profile_data:
            user.location = profile_data['location']
        if 'website' in profile_data:
            user.website = profile_data['website']
        if 'linkedin_url' in profile_data:
            user.linkedin_url = profile_data['linkedin_url']
        if 'github_url' in profile_data:
            user.github_url = profile_data['github_url']
        if 'twitter_url' in profile_data:
            user.twitter_url = profile_data['twitter_url']
        if 'portfolio_url' in profile_data:
            user.portfolio_url = profile_data['portfolio_url']
        if 'profile_visibility' in profile_data:
            user.profile_visibility = profile_data['profile_visibility']
        if 'show_email' in profile_data:
            user.show_email = profile_data['show_email']
        if 'show_phone' in profile_data:
            user.show_phone = profile_data['show_phone']
        
        # Save changes
        db.commit()
        
        return {"success": True, "message": "Profile updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        return {"success": False, "message": str(e)}

@app.post("/api/upload-profile-picture")
async def upload_profile_picture(request: Request):
    """
    Production-ready profile picture upload endpoint
    
    Features:
    - Secure file validation
    - File size limits (2MB)
    - MIME type validation
    - Filename sanitization
    - Cloud storage ready
    - Comprehensive error handling
    """
    try:
        # Authentication check
        session_token = request.cookies.get("session_token")
        if not session_token:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": "Authentication required", "code": "AUTH_REQUIRED"}
            )
        
        # Get database session
        db = next(get_db())
        try:
            from auth_utils import get_user_from_session
            session_data = get_user_from_session(session_token, db)
            if not session_data:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "message": "Session expired", "code": "SESSION_EXPIRED"}
                )
            
            user_id = session_data['user_id']
        finally:
            db.close()
        
        # Get form data
        form = await request.form()
        file = form.get("profile_picture")
        
        if not file:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "No file uploaded", "code": "NO_FILE"}
            )
        
        # Handle UploadFile properly - read content to get size
        file_content = await file.read()
        file_size = len(file_content)
        
        # File validation
        validation_result = await validate_profile_picture(file, file_size, file_content)
        if not validation_result["valid"]:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": validation_result["message"], "code": validation_result["code"]}
            )
        
        # Generate secure filename
        filename = generate_secure_filename(file.filename)
        
        # Save file to storage (pass content directly)
        storage_result = await save_profile_picture(file_content, filename)
        if not storage_result["success"]:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": storage_result["message"], "code": "STORAGE_ERROR"}
            )
        
        # Update database
        db_result = await update_user_profile_picture(user_id, storage_result["file_url"])
        if not db_result["success"]:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": db_result["message"], "code": "DB_ERROR"}
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Profile picture uploaded successfully",
                "file_url": storage_result["file_url"],
                "filename": filename
            }
        )
        
    except Exception as e:
        logger.error(f"Error uploading profile picture: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Internal server error", "code": "INTERNAL_ERROR"}
        )

async def validate_profile_picture(file, file_size: int, file_content: bytes) -> dict:
    """Validate uploaded profile picture file"""
    try:
        # Check file size (2MB limit)
        if file_size > 2 * 1024 * 1024:
            return {"valid": False, "message": "File size must be less than 2MB", "code": "FILE_TOO_LARGE"}
        
        if file_size == 0:
            return {"valid": False, "message": "File is empty", "code": "EMPTY_FILE"}
        
        # Check MIME type
        allowed_mimes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        content_type = file.content_type or ''
        if content_type and content_type not in allowed_mimes:
            return {"valid": False, "message": "Only JPG, PNG, and WebP images are allowed", "code": "INVALID_TYPE"}
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        file_extension = os.path.splitext(file.filename or '')[1].lower()
        if file_extension not in allowed_extensions:
            return {"valid": False, "message": "Invalid file extension", "code": "INVALID_EXTENSION"}
        
        # Validate actual image content using magic bytes
        if file_content:
            # Check JPEG
            if file_content[:3] == b'\xff\xd8\xff':
                pass  # Valid JPEG
            # Check PNG
            elif file_content[:8] == b'\x89PNG\r\n\x1a\n':
                pass  # Valid PNG
            # Check WebP
            elif file_content[:4] == b'RIFF' and file_content[8:12] == b'WEBP':
                pass  # Valid WebP
            else:
                return {"valid": False, "message": "File is not a valid image", "code": "INVALID_IMAGE"}
        
        return {"valid": True, "message": "File validation passed", "code": "VALID"}
        
    except Exception as e:
        logger.error(f"File validation error: {e}")
        import traceback
        traceback.print_exc()
        return {"valid": False, "message": "File validation failed", "code": "VALIDATION_ERROR"}

def generate_secure_filename(original_filename: str) -> str:
    """Generate a secure, unique filename"""
    import uuid
    import re
    
    # Remove any path components and get just the filename
    filename = os.path.basename(original_filename)
    
    # Remove any non-alphanumeric characters except dots and hyphens
    filename = re.sub(r'[^a-zA-Z0-9.-]', '', filename)
    
    # Generate unique identifier
    unique_id = str(uuid.uuid4())
    
    # Get file extension
    file_extension = os.path.splitext(filename)[1].lower()
    
    # Create secure filename: timestamp_uuid.extension
    timestamp = int(time.time())
    secure_filename = f"{timestamp}_{unique_id}{file_extension}"
    
    return secure_filename

async def save_profile_picture(file_content: bytes, filename: str) -> dict:
    """Save profile picture to storage (local or cloud)"""
    try:
        # For now, save to local storage
        # In production, you can easily switch to S3 or other cloud storage
        
        upload_dir = os.path.join(BASE_DIR, "static", "uploads", "profile_pictures")
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        
        # Save file - write content directly to disk
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Generate file URL
        file_url = f"/static/uploads/profile_pictures/{filename}"
        
        logger.info(f"Profile picture saved successfully: {file_url}")
        return {"success": True, "file_url": file_url, "message": "File saved successfully"}
        
    except Exception as e:
        logger.error(f"Error saving profile picture: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"Failed to save file: {str(e)}"}

async def update_user_profile_picture(user_id: int, file_url: str) -> dict:
    """Update user's profile picture in database"""
    try:
        from models import User
        
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return {"success": False, "message": "User not found"}
        
        # Update profile picture
        user.update_profile_pic(file_url)
        db.commit()
        db.close()
        
        logger.info(f"Profile picture updated for user {user_id}: {file_url}")
        return {"success": True, "message": "Profile picture updated in database"}
        
    except Exception as e:
        logger.error(f"Error updating database: {e}")
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.rollback()
            db.close()
        return {"success": False, "message": f"Database update failed: {str(e)}"}

@app.post("/api/test-upload-profile-image")
async def test_upload_profile_image(request: Request):
    """Test endpoint for profile image upload (no authentication required)"""
    try:
        # Get form data
        form = await request.form()
        file = form.get("profile_image")
        
        if not file:
            return {"success": False, "message": "No file uploaded"}
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            return {"success": False, "message": "File must be an image (JPG, PNG, GIF)"}
        
        # Validate file size (5MB limit)
        if file.size > 5 * 1024 * 1024:
            return {"success": False, "message": "File size must be less than 5MB"}
        
        # Generate unique filename
        import uuid
        import os
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"test_{uuid.uuid4()}{file_extension}"
        
        # Save file to uploads directory
        upload_dir = os.path.join(BASE_DIR, "static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {"success": True, "message": "Test image uploaded successfully", "filename": filename}
        
    except Exception as e:
        logger.error(f"Error in test upload: {e}")
        return {"success": False, "message": f"Server error: {str(e)}"}

# Import and include streak routes
try:
    from streak_routes import router as streak_router
    app.include_router(streak_router, prefix="/api", tags=["Streaks"])
    logger.info("Streak routes included successfully")
except Exception as e:
    logger.warning(f"Could not include streak routes: {e}")

# Import and include job recommendation routes
try:
    from job_recommendation_routes import router as job_recommendation_router
    app.include_router(job_recommendation_router, tags=["Job Recommendations"])
    logger.info("Job recommendation routes included successfully")
except Exception as e:
    logger.warning(f"Could not include job recommendation routes: {e}")

# Import and include test auth routes for debugging
try:
    from test_auth_route import router as test_auth_router
    app.include_router(test_auth_router, tags=["Test Auth"])
    logger.info("Test auth routes included successfully")
except Exception as e:
    logger.warning(f"Could not include test auth routes: {e}")

logger.info("Qrow IQ FastAPI application configured successfully")

# Handle Chrome DevTools well-known probe to avoid noisy 404s
@app.get("/.well-known/appspecific/com.chrome.devtools.json")
async def chrome_devtools_probe():
    from fastapi import Response
    return Response(status_code=204)

# Serve uploaded message dashboard (if available)
@app.get("/message/dashboard")
async def message_dashboard_page():
    """Serve the uploaded message dashboard UI."""
    try:
        file_path = os.path.join(BASE_DIR, "message", "message", "message", "dashboard.html")
        if not os.path.exists(file_path):
            return HTMLResponse("Message dashboard not found.")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Rewrite API base URL to use this server
        content = content.replace(
            "const API_BASE_URL = 'http://localhost:9000/api/v1';",
            "const API_BASE_URL = '/api/v1';"
        )
        # Disable login redirect inside uploaded message UI
        content = content.replace(
            "window.location.href = '/login';",
            "/* login bypass: disabled redirect */"
        )
        # Fix websocket URL to this host and our WS endpoint
        content = content.replace(
            "const wsUrl = `${protocol}//localhost:9000/api/v1/messages/ws/${userId}?token=${currentToken}`;",
            "const wsUrl = `${protocol}//${window.location.host}/messages/ws/${userId}`;"
        )
        return HTMLResponse(content=content)
    except Exception as e:
        logger.error(f"Error serving message dashboard: {e}")
        return HTMLResponse("Failed to load message dashboard.")

# Redirect legacy paths to the new message dashboard
@app.get("/messages")
async def redirect_messages_no_slash():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/message/dashboard", status_code=307)

@app.get("/messages/")
async def redirect_messages_with_slash():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/message/dashboard", status_code=307)

# ---------------- Speech-to-Text (runs in same server) ----------------

# Initialize speech recognizer with safer defaults
_stt_recognizer = sr.Recognizer()
_stt_recognizer.dynamic_energy_threshold = False
_stt_recognizer.energy_threshold = 200
_stt_recognizer.pause_threshold = 0.6

def _stt_decode_base64_audio(data_str: str) -> bytes:
    if not data_str:
        raise ValueError("Empty audio_data")
    if "," in data_str and data_str.strip().startswith("data:"):
        data_str = data_str.split(",", 1)[1]
    padding = len(data_str) % 4
    if padding:
        data_str += "=" * (4 - padding)
    return base64.b64decode(data_str)

def _stt_trim_silence_wav(in_wav_path: str,
                          rms_threshold: int = 700,
                          trailing_silence_ms: int = 800,
                          chunk_ms: int = 30) -> str:
    """Trim trailing silence from a 16-bit PCM mono/stereo WAV by RMS threshold.
    Returns a path to a trimmed temp wav file; falls back to original on error.
    """
    try:
        with wave.open(in_wav_path, 'rb') as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()

            if sampwidth != 2:
                # Convert later by re-saving as 16-bit if needed; for now, just keep original
                return in_wav_path

            frames = wf.readframes(n_frames)

        # Compute RMS per chunk
        chunk_size = max(1, int(framerate * (chunk_ms / 1000.0)))
        total_samples = n_frames
        # For multi-channel, audioop works on interleaved frames with width*samples
        # Iterate over bytes in steps of chunk_size frames
        rms_values = []
        pos = 0
        bytes_per_frame = sampwidth * n_channels
        total_bytes = len(frames)
        bytes_per_chunk = chunk_size * bytes_per_frame
        while pos < total_bytes:
            chunk = frames[pos:pos + bytes_per_chunk]
            if not chunk:
                break
            rms = audioop.rms(chunk, sampwidth)  # 0..32767 for 16-bit
            rms_values.append(rms)
            pos += bytes_per_chunk

        if not rms_values:
            return in_wav_path

        # Find last chunk above threshold
        last_idx = -1
        for i in range(len(rms_values) - 1, -1, -1):
            if rms_values[i] > rms_threshold:
                last_idx = i
                break

        if last_idx == -1:
            # No speech detected; keep short segment
            keep_bytes = min(total_bytes, bytes_per_chunk * max(1, int((trailing_silence_ms / chunk_ms))))
        else:
            # Keep chunks up to last speech plus trailing_silence_ms
            extra_chunks = int(trailing_silence_ms / chunk_ms)
            end_chunk_inclusive = min(len(rms_values) - 1, last_idx + extra_chunks)
            keep_bytes = min(total_bytes, (end_chunk_inclusive + 1) * bytes_per_chunk)

        trimmed_frames = frames[:keep_bytes]

        # Write trimmed file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as out_f:
            out_path = out_f.name
        with wave.open(out_path, 'wb') as wout:
            wout.setnchannels(n_channels)
            wout.setsampwidth(sampwidth)
            wout.setframerate(framerate)
            wout.writeframes(trimmed_frames)
        return out_path
    except Exception:
        # On any error, just use original
        return in_wav_path

class _SpeechRecognitionRequest(BaseModel):
    audio_data: str
    language: str = "en-US"

class _SpeechRecognitionResponse(BaseModel):
    text: str
    confidence: Optional[float] = None
    success: bool
    error: Optional[str] = None

@app.post("/api/stt/speech-to-text")
async def stt_speech_to_text(request: _SpeechRecognitionRequest):
    try:
        audio_bytes = _stt_decode_base64_audio(request.audio_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        try:
            # Trim trailing silence before recognition
            trimmed_path = _stt_trim_silence_wav(temp_file_path)
            with sr.AudioFile(trimmed_path) as source:
                try:
                    _stt_recognizer.adjust_for_ambient_noise(source, duration=0.2)
                except Exception:
                    pass
                audio = _stt_recognizer.record(source)
            text = _stt_recognizer.recognize_google(audio, language=request.language)
            return {
                "text": text,
                "confidence": 0.8,
                "success": True
            }
        finally:
            try:
                import os as _os
                if _os.path.exists(temp_file_path):
                    _os.unlink(temp_file_path)
                # Also clean trimmed temp if different
                try:
                    if 'trimmed_path' in locals() and trimmed_path != temp_file_path and _os.path.exists(trimmed_path):
                        _os.unlink(trimmed_path)
                except Exception:
                    pass
            except Exception:
                pass
    except sr.UnknownValueError:
        return {"text": "", "success": False, "error": "Could not understand the audio"}
    except sr.RequestError as e:
        return {"text": "", "success": False, "error": f"Speech recognition service error: {str(e)}"}
    except Exception as e:
        logger.error("[stt] Unexpected error:\n" + traceback.format_exc())
        return {"text": "", "success": False, "error": f"Unexpected error: {str(e)}"}

@app.post("/api/stt/speech-to-text-file")
async def stt_speech_to_text_file(audio_file: UploadFile = File(...), language: str = "en-US"):
    try:
        audio_data = await audio_file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        try:
            trimmed_path = _stt_trim_silence_wav(temp_file_path)
            with sr.AudioFile(trimmed_path) as source:
                try:
                    _stt_recognizer.adjust_for_ambient_noise(source, duration=0.2)
                except Exception:
                    pass
                audio = _stt_recognizer.record(source)
            text = _stt_recognizer.recognize_google(audio, language=language)
            return {
                "text": text,
                "confidence": 0.8,
                "success": True
            }
        finally:
            try:
                import os as _os
                if _os.path.exists(temp_file_path):
                    _os.unlink(temp_file_path)
                try:
                    if 'trimmed_path' in locals() and trimmed_path != temp_file_path and _os.path.exists(trimmed_path):
                        _os.unlink(trimmed_path)
                except Exception:
                    pass
            except Exception:
                pass
    except sr.UnknownValueError:
        return {"text": "", "success": False, "error": "Could not understand the audio"}
    except sr.RequestError as e:
        return {"text": "", "success": False, "error": f"Speech recognition service error: {str(e)}"}
    except Exception as e:
        logger.error("[stt-file] Unexpected error:\n" + traceback.format_exc())
        return {"text": "", "success": False, "error": f"Unexpected error: {str(e)}"}

class _VoiceActivityRequest(BaseModel):
    audio_data: str  # Base64 encoded audio data
    threshold: float = 0.005  # RMS threshold for voice detection
    min_duration: float = 0.5  # Minimum duration in seconds

class _VoiceActivityResponse(BaseModel):
    has_voice: bool
    confidence: float
    duration: float
    success: bool
    error: Optional[str] = None

@app.post("/api/stt/voice-activity-detection", response_model=_VoiceActivityResponse)
async def voice_activity_detection(request: _VoiceActivityRequest):
    """
    Detect if audio contains voice activity using RMS analysis
    """
    try:
        audio_bytes = _stt_decode_base64_audio(request.audio_data)
        
        # Load audio file to analyze
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            with sr.AudioFile(temp_file_path) as source:
                # Get audio data
                audio = _stt_recognizer.record(source)
                audio_data = audio.get_raw_data()
                
                # Convert to float32 array for analysis
                import numpy as np
                audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Calculate RMS (Root Mean Square) for voice activity detection
                rms = np.sqrt(np.mean(audio_array ** 2))
                
                # Calculate duration
                duration = len(audio_array) / source.SAMPLE_RATE
                
                # Determine if voice is present
                has_voice = rms > request.threshold and duration >= request.min_duration
                
                # Calculate confidence based on RMS value
                confidence = min(1.0, rms / (request.threshold * 10))  # Scale confidence
                
                return _VoiceActivityResponse(
                    has_voice=has_voice,
                    confidence=confidence,
                    duration=duration,
                    success=True
                )
                
        finally:
            try:
                import os as _os
                if _os.path.exists(temp_file_path):
                    _os.unlink(temp_file_path)
            except Exception:
                pass
                
    except Exception as e:
        logger.error("[voice-activity] Unexpected error:\n" + traceback.format_exc())
        return _VoiceActivityResponse(
            has_voice=False,
            confidence=0.0,
            duration=0.0,
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

# Auto Speech Processing Endpoints
class AutoSpeechRequest(BaseModel):
    audio_data: str  # Base64 encoded audio data
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    language: str = "en-US"
    auto_submit: bool = True

class AutoSpeechResponse(BaseModel):
    success: bool
    text: str
    confidence: float
    submitted: bool
    message_id: Optional[str] = None
    error: Optional[str] = None

@app.post("/api/auto-speech/process", response_model=AutoSpeechResponse)
async def process_auto_speech(
    request: AutoSpeechRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process speech automatically and submit to interview session
    """
    try:
        # Decode audio data
        audio_bytes = _stt_decode_base64_audio(request.audio_data)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            # Process audio for speech recognition
            with sr.AudioFile(temp_file_path) as source:
                # Adjust for ambient noise
                try:
                    _stt_recognizer.adjust_for_ambient_noise(source, duration=0.2)
                except Exception:
                    pass
                
                # Record audio
                audio = _stt_recognizer.record(source)
            
            # Perform speech recognition
            try:
                text = _stt_recognizer.recognize_google(audio, language=request.language)
                confidence = 0.8  # Google doesn't provide confidence scores
            except sr.UnknownValueError:
                return AutoSpeechResponse(
                    success=False,
                    text="",
                    confidence=0.0,
                    submitted=False,
                    error="Could not understand the audio"
                )
            except sr.RequestError as e:
                return AutoSpeechResponse(
                    success=False,
                    text="",
                    confidence=0.0,
                    submitted=False,
                    error=f"Speech recognition service error: {str(e)}"
                )
            
            # If auto_submit is enabled and we have a session_id, submit the message
            submitted = False
            message_id = None
            
            if request.auto_submit and request.session_id and text.strip():
                try:
                    # MOCK INTERVIEW MODULE - DISCONNECTED (can be reconnected in future)
                    # Import here to avoid circular imports
                    # from mockinterview_routes import send_message
                    
                    # Create message request
                    # message_request = {
                    #     "session_id": request.session_id,
                    #     "message": text,
                    #     "user_id": request.user_id or current_user.id
                    # }
                    
                    # Submit message to interview
                    # result = await send_message(message_request, db)
                    
                    # if isinstance(result, dict) and result.get("success"):
                    #     submitted = True
                    #     message_id = result.get("message_id")
                    # else:
                    #     logger.warning(f"Failed to submit message to interview: {result}")
                    pass  # Mock interview integration disabled
                        
                except Exception as e:
                    logger.error(f"Failed to submit to interview: {str(e)}")
                    # Still return the text even if submission failed
            
            return AutoSpeechResponse(
                success=True,
                text=text,
                confidence=confidence,
                submitted=submitted,
                message_id=message_id
            )
            
        finally:
            # Clean up temporary file
            try:
                import os
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            except Exception:
                pass
                
    except Exception as e:
        logger.error(f"Auto speech processing error: {str(e)}")
        logger.error(traceback.format_exc())
        return AutoSpeechResponse(
            success=False,
            text="",
            confidence=0.0,
            submitted=False,
            error=f"Processing error: {str(e)}"
        )

# Redirect top-level auth paths to prefixed routes
@app.get("/login")
async def redirect_login():
    # Serve SPA index so client router renders LoginPage at /login
    index_path = os.path.join(FRONTEND_DIST_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/auth/login", status_code=307)

@app.get("/signup")
async def redirect_signup():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/auth/signup", status_code=307)

# ---------------- Job Recommendations ----------------

def _normalize_tokens(text: str) -> Set[str]:
    if not text:
        return set()
    # Keep alphanumerics and spaces, lowercase, split
    cleaned = re.sub(r"[^a-zA-Z0-9+.# ]+", " ", text.lower())
    tokens = {t for t in (tok.strip() for tok in cleaned.replace("/", " ").replace(",", " ").split()) if t}
    # Common stopwords to reduce noise
    stop = {"and","or","the","a","an","to","of","in","for","with","on","at","by","from","as","is","are","be","this","that"}
    return {t for t in tokens if t not in stop and len(t) > 1}

def _parse_user_skills(skills_field: Optional[str]) -> Set[str]:
    if not skills_field:
        return set()
    try:
        import json
        data = json.loads(skills_field)
        if isinstance(data, list):
            return {s.strip().lower() for s in data if isinstance(s, str)}
        if isinstance(data, dict):
            return {str(k).strip().lower() for k, v in data.items() if v}
    except Exception:
        pass
    # Fallback: comma/semicolon separated
    parts = re.split(r"[,;\n]+", skills_field)
    return {p.strip().lower() for p in parts if p.strip()}

def _job_tokens(job) -> Set[str]:
    fields = [getattr(job, 'title', ''), getattr(job, 'requirements', ''), getattr(job, 'description', ''), getattr(job, 'location', ''), getattr(job, 'job_type', '')]
    joined = " \n ".join([f for f in fields if f])
    return _normalize_tokens(joined)

def _score_job(user_skill_tokens: Set[str], job_tokens: Set[str]) -> float:
    if not user_skill_tokens or not job_tokens:
        return 0.0
    inter = user_skill_tokens & job_tokens
    if not inter:
        return 0.0
    # Jaccard-like with a small boost for exact skill matches
    jacc = len(inter) / len(user_skill_tokens | job_tokens)
    boost = min(0.5, len(inter) * 0.05)
    return round(jacc + boost, 4)

@app.get("/api/jobs/recommendations")
async def get_job_recommendations(
    request: Request,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Return top-N active job recommendations for the current user based on profile skills."""
    try:
        from models import User, Job
        # Identify user from session cookie (mirrors other endpoints' pattern)
        session_token = request.cookies.get("session_token")
        user: Optional[User] = None
        if session_token:
            try:
                from auth_utils import get_user_from_session
                session_data = get_user_from_session(session_token)
                if isinstance(session_data, dict):
                    user = db.query(User).filter(User.id == session_data.get('user_id')).first()
            except Exception:
                user = None

        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")

        user_skills = _parse_user_skills(getattr(user, 'skills', None))
        # Include inferred tokens from title/industry to improve recall
        user_skills |= _normalize_tokens((user.title or "") + " " + (user.industry or ""))

        # Fetch active jobs
        jobs: List[Job] = db.query(Job).filter(Job.is_active == True).all()
        scored: List[Tuple[float, Job]] = []
        for job in jobs:
            jt = _job_tokens(job)
            score = _score_job(user_skills, jt)
            if score > 0:
                scored.append((score, job))

        # Sort by score desc, then recency
        scored.sort(key=lambda x: (x[0], getattr(x[1], 'posted_at', None) or 0), reverse=True)
        top = scored[: max(1, min(50, limit))]
        results = []
        for score, job in top:
            jd = job.to_dict()
            jd['match_score'] = score
            results.append(jd)

        return {"success": True, "count": len(results), "recommendations": results}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job recommendations error: {e}")
        return {"success": False, "message": str(e), "recommendations": []}

# SPA fallback: require auth and serve index.html for non-API, non-static paths
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str, request: Request):
    blocked_prefixes = (
        "api/", "static/", "assets/", "resume-tester/", "mock-interview/", "message/",
        "docs", "redoc", "openapi.json", "health", "auth/", "dashboard/"
    )
    if full_path.startswith(blocked_prefixes) or full_path in {"favicon.ico"}:
        from fastapi import HTTPException as _HTTPException
        raise _HTTPException(status_code=404, detail="Not Found")
    # Enforce authentication for SPA routes
    session_token = request.cookies.get("session_token")
    is_authenticated = False
    if session_token:
        try:
            from auth_utils import get_user_from_session as _get_user_from_session
            # Get database session
            db = next(get_db())
            try:
                session_data = _get_user_from_session(session_token, db)
                is_authenticated = bool(session_data and session_data.get("user_id"))
            finally:
                db.close()
        except Exception:
            is_authenticated = False
    if not is_authenticated:
        return RedirectResponse(url="/login", status_code=303)
    index_path = os.path.join(FRONTEND_DIST_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    # Use relative redirect instead of hardcoded localhost
    from config import get_base_url
    base_url = get_base_url(request)
    return RedirectResponse(url=f"{base_url}/", status_code=307)
