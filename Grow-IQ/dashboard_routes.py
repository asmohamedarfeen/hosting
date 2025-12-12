import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from auth_utils import get_current_user
from models import User, Post, Job, Connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(tags=["Dashboard"])

# Get templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Display user dashboard"""
    try:
        # Get user's posts
        posts = db.query(Post).filter(Post.user_id == current_user.id).order_by(Post.created_at.desc()).limit(10).all()
        
        # Get recent jobs
        jobs = db.query(Job).filter(Job.is_active == True).order_by(Job.posted_at.desc()).limit(5).all()
        
        # Get user's connections
        connections = db.query(Connection).filter(
            (Connection.user_id == current_user.id) | (Connection.connected_user_id == current_user.id)
        ).filter(Connection.status == 'accepted').limit(10).all()
        
        # Get connection count
        connection_count = db.query(Connection).filter(
            (Connection.user_id == current_user.id) | (Connection.connected_user_id == current_user.id)
        ).filter(Connection.status == 'accepted').count()
        
        # Get post count
        post_count = db.query(Post).filter(Post.user_id == current_user.id).count()
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": current_user,
            "posts": posts,
            "jobs": jobs,
            "connections": connections,
            "connection_count": connection_count,
            "post_count": post_count
        })
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while loading dashboard"
        )

@router.get("/test", response_class=HTMLResponse)
async def test_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Simple test page to verify authentication"""
    try:
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <h1>Authentication Test</h1>
                    <p>✅ You are authenticated!</p>
                    <p>User ID: {current_user.id}</p>
                    <p>Username: {current_user.username}</p>
                    <p>Email: {current_user.email}</p>
                    <p>Full Name: {current_user.full_name}</p>
                    <br>
                    <a href="/home">Go to Home</a><br>
                    <a href="/dashboard">Go to Dashboard</a><br>
                    <a href="/auth/login">Go to Login</a>
                </body>
            </html>
            """
        )
        
    except Exception as e:
        logger.error(f"Test page error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Display user profile page"""
    try:
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": current_user
        })
        
    except Exception as e:
        logger.error(f"Profile page error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while loading profile"
        )

@router.get("/connections", response_class=HTMLResponse)
async def connections_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Display user connections page"""
    try:
        # Get all connections
        connections = db.query(Connection).filter(
            (Connection.user_id == current_user.id) | (Connection.connected_user_id == current_user.id)
        ).all()
        
        # Get pending requests
        pending_requests = db.query(Connection).filter(
            Connection.connected_user_id == current_user.id,
            Connection.status == 'pending'
        ).all()
        
        return templates.TemplateResponse("connections.html", {
            "request": request,
            "user": current_user,
            "connections": connections,
            "pending_requests": pending_requests
        })
        
    except Exception as e:
        logger.error(f"Connections page error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while loading connections"
        )

# Removed duplicate /jobs route - now handled by job_routes.py

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Display user settings page"""
    try:
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "user": current_user
        })
        
    except Exception as e:
        logger.error(f"Settings page error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while loading settings"
        )
