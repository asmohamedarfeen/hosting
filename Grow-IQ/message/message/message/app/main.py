"""
Main FastAPI application entry point.
Configures the app, includes routers, and sets up middleware.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import os
import sys

"""
Ensure this standalone messaging UI uses the main application's database.
We import the top-level config and set DATABASE_URL so the message app's
DB layer points at the same database as the main app (shared users table).
"""
# Resolve project root (Glow-IQ) and import global config
PROJECT_TOP = Path(__file__).resolve().parents[4]
if str(PROJECT_TOP) not in sys.path:
    sys.path.insert(0, str(PROJECT_TOP))
try:
    from config import settings  # main app config
    os.environ["DATABASE_URL"] = settings.DATABASE_URL
except Exception:
    # Fallback: leave environment as-is if main config isn't available
    pass

try:
    from .db import create_tables
    from .routers import users, connections, messages
except ImportError:
    # When running the file directly, use absolute imports
    from app.db import create_tables
    from app.routers import users, connections, messages

# Get the project root directory (parent of app directory)
PROJECT_ROOT = Path(__file__).parent.parent

def get_html_file_path(filename: str) -> str:
    """Get the absolute path to an HTML file in the project root."""
    return str(PROJECT_ROOT / filename)

# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    print("🚀 Starting LinkedIn-like Connection + Messaging App...")
    # Create tables against the main app database (no-op if already present)
    try:
        create_tables()
        print("✅ Database tables verified/created successfully")
    except Exception as e:
        print(f"⚠️  Skipped table creation: {e}")
    print("🌐 Application is ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="LinkedIn-like Connection + Messaging App",
    description="A FastAPI-based application for user connections and real-time messaging",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(users.router, prefix="/api/v1")
app.include_router(connections.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions globally."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "LinkedIn-like Connection + Messaging App",
        "version": "1.0.0"
    }


# Root endpoint - redirect to login page
@app.get("/")
async def root():
    """Root endpoint redirects to login page."""
    return FileResponse(get_html_file_path("login_page.html"))


# Serve login page
@app.get("/login")
async def login_page():
    """Serve the login page."""
    return FileResponse(get_html_file_path("login_page.html"))


# Redirect old login_page.html to login
@app.get("/login_page.html")
async def login_html_redirect():
    """Redirect old login_page.html to login route."""
    return RedirectResponse(url="/login", status_code=301)


# Serve dashboard page
@app.get("/dashboard")
async def dashboard_page():
    """Serve the dashboard page."""
    return FileResponse(get_html_file_path("dashboard.html"))


# Redirect old dashboard.html to dashboard
@app.get("/dashboard.html")
async def dashboard_html_redirect():
    """Redirect old dashboard.html to dashboard route."""
    return RedirectResponse(url="/dashboard", status_code=301)


# Serve demo page
@app.get("/demo")
async def demo_page():
    """Serve the demo page."""
    return FileResponse(get_html_file_path("demo_login.html"))


# Serve test page
@app.get("/test")
async def test_page():
    """Serve the test page."""
    return FileResponse(get_html_file_path("test_login.html"))


# Favicon endpoint to prevent 404 errors
@app.get("/favicon.ico")
async def favicon():
    """Serve favicon.ico to prevent 404 errors."""
    # Return a simple 204 No Content response for favicon requests
    from fastapi import Response
    return Response(status_code=204)


# API information endpoint
@app.get("/api/info")
async def api_info():
    """Get API information and available endpoints."""
    return {
        "name": "LinkedIn-like Connection + Messaging App",
        "version": "1.0.0",
        "description": "FastAPI application for user connections and real-time messaging",
        "endpoints": {
            "users": {
                "register": "POST /api/v1/users/register",
                "login": "POST /api/v1/users/login",
                "profile": "GET /api/v1/users/me",
                "update_profile": "PUT /api/v1/users/me",
                "list_users": "GET /api/v1/users/",
                "get_user": "GET /api/v1/users/{user_id}"
            },
            "connections": {
                "send_request": "POST /api/v1/connections/",
                "accept": "PUT /api/v1/connections/{connection_id}/accept",
                "reject": "PUT /api/v1/connections/{connection_id}/reject",
                "list": "GET /api/v1/connections/",
                "get": "GET /api/v1/connections/{connection_id}",
                "delete": "DELETE /api/v1/connections/{connection_id}"
            },
            "messages": {
                "send": "POST /api/v1/messages/",
                "chat_history": "GET /api/v1/messages/chat/{other_user_id}",
                "mark_read": "PUT /api/v1/messages/{message_id}/read",
                "websocket": "WS /api/v1/messages/ws/{user_id}"
            }
        },
        "authentication": "JWT Bearer token required for protected endpoints",
        "websocket": "Real-time messaging via WebSocket with JWT authentication",
        "frontend": {
            "login": "/login",
            "dashboard": "/dashboard"
        }
    }


if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    
    # Add the parent directory to Python path when running directly
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
