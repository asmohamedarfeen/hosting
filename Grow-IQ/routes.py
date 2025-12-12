import os
import time
import logging
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename
from database import get_db, test_db_connection
from models import User, Post, Job, Notification, Connection
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Template access functions
def get_templates_simple():
    """Get templates without dependency injection"""
    try:
        import app
        return app.templates
    except Exception as e:
        logger.error(f"Failed to get templates: {e}")
        return None

# Upload folder - we'll get this from the app context
UPLOAD_FOLDER = None

def set_upload_folder(folder):
    global UPLOAD_FOLDER
    UPLOAD_FOLDER = folder

# Test routes
@router.get("/test")
async def test_route():
    return {"message": "Test route working!", "status": "success"}

@router.get("/test2")
async def test_route2():
    return {"message": "Test route 2 working!", "status": "success"}

@router.get("/test-redirect")
async def test_redirect():
    """Test redirect functionality"""
    return RedirectResponse(url="/test", status_code=303)

@router.get("/dashboard-minimal")
async def dashboard_minimal(request: Request, db: Session = Depends(get_db)):
    """Minimal dashboard route for testing"""
    try:
        # Just check if users exist
        user_count = db.query(User).count()
        return {"message": f"Dashboard minimal route working! User count: {user_count}", "status": "success"}
    except Exception as e:
        return {"message": f"Error: {str(e)}", "status": "error"}

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        templates = get_templates_simple()
        if not templates:
            raise HTTPException(status_code=500, detail="Templates not available")
            
        # Check if any users exist
        if not db.query(User).first():
            # Create a default user if none exists
            default_user = User(
                username="admin",
                email="admin@qrowiq.com",
                full_name="Administrator",
                is_active=True
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
            logger.info("Created default admin user")
        
        # Get the first user (or default user)
        user = db.query(User).first()
        
        # Get recent posts
        posts = db.query(Post).order_by(Post.created_at.desc()).limit(10).all()
        
        # Get recent jobs
        jobs = db.query(Job).filter(Job.is_active == True).order_by(Job.posted_at.desc()).limit(5).all()
        
        # Get notifications
        notifications = db.query(Notification).filter(
            Notification.user_id == user.id, 
            Notification.is_read == False
        ).order_by(Notification.created_at.desc()).limit(5).all()
        
        # Dashboard statistics
        stats = {
            'total_posts': db.query(Post).count(),
            'total_connections': db.query(Connection).filter(Connection.status == 'accepted').count(),
            'total_jobs': db.query(Job).filter(Job.is_active == True).count(),
            'unread_notifications': len(notifications)
        }
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": user, 
            "posts": posts, 
            "jobs": jobs, 
            "notifications": notifications,
            "stats": stats
        })
    except Exception as e:
        import traceback
        print(f"Error in dashboard route: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_redirect(request: Request, db: Session = Depends(get_db)):
    """Dashboard route that redirects to root path"""
    return RedirectResponse(url="/", status_code=302)

@router.post("/create_post")
async def create_post(
    request: Request,
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        # Get the first user (or create default if none exists)
        user = db.query(User).first()
        if not user:
            default_user = User(
                username="admin",
                email="admin@qrowiq.com",
                full_name="Administrator",
                is_active=True
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
            user = default_user
        
        if not content:
            raise HTTPException(status_code=400, detail="Post content is required.")
        
        # Handle file upload
        image_path = None
        if image and image.filename:
            if allowed_file(image.filename):
                # Generate unique filename
                filename = str(uuid.uuid4()) + '.' + image.filename.rsplit('.', 1)[1].lower()
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                
                # Save file
                with open(file_path, "wb") as buffer:
                    content_data = await image.read()
                    buffer.write(content_data)
                
                image_path = filename
            else:
                raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Create post
        post = Post(
            user_id=user.id,
            content=content,
            image_path=image_path,
            created_at=datetime.utcnow()
        )
        
        db.add(post)
        db.commit()
        db.refresh(post)
        
        logger.info(f"Post created successfully by user {user.username}")
        return RedirectResponse(url="/", status_code=303)
        
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create post")

@router.post("/create_job")
async def create_job(
    title: str = Form(...),
    company: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    salary_min: Optional[int] = Form(None),
    salary_max: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        # Get the first user (or create default if none exists)
        user = db.query(User).first()
        if not user:
            default_user = User(
                username="admin",
                email="admin@qrowiq.com",
                full_name="Administrator",
                is_active=True
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
            user = default_user
        
        # Create job
        job = Job(
            title=title,
            company=company,
            location=location,
            description=description,
            salary_min=salary_min,
            salary_max=salary_max,
            posted_by=user.id,
            posted_at=datetime.utcnow(),
            is_active=True
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        logger.info(f"Job created successfully by user {user.username}")
        return RedirectResponse(url="/", status_code=303)
        
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create job")

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    try:
        templates = get_templates_simple()
        if not templates:
            raise HTTPException(status_code=500, detail="Templates not available")
        
        # Get the first user
        user = db.query(User).first()
        if not user:
            raise HTTPException(status_code=404, detail="No users found")
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": user, 
            "page": "settings"
        })
    except Exception as e:
        logger.error(f"Error in settings route: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Utility function for creating users (simplified)
def create_user_in_db(db: Session, user_data: dict):
    """Create a new user in the database"""
    try:
        # Check if username or email already exists
        existing_user = db.query(User).filter(
            (User.username == user_data['username']) | (User.email == user_data['email'])
        ).first()
        
        if existing_user:
            raise ValueError("Username or email already exists")
        
        # Create new user (without password for now)
        new_user = User(
            username=user_data['username'],
            email=user_data['email'],
            full_name=user_data['full_name'],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User created successfully: {new_user.username}")
        return new_user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise
