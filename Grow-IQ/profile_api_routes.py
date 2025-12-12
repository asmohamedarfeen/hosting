"""
Enhanced Profile API Routes
Handles comprehensive profile management including avatar upload, data updates, and portfolio management.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
import os
import uuid
import json
import logging
from datetime import datetime
from PIL import Image
import io

from database import get_db
from models import User
from auth_utils import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Configuration
UPLOAD_DIR = "static/uploads/profile_pics"
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGE_SIZE = (800, 800)  # Max dimensions

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

def validate_and_process_image(file_content: bytes, filename: str) -> tuple[bytes, str]:
    """Validate and process uploaded image"""
    
    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image too large (>5MB)")
    
    # Check file extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Use JPG, PNG, GIF, or WebP")
    
    try:
        # Open and process image
        image = Image.open(io.BytesIO(file_content))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        
        # Resize if too large
        if image.size[0] > MAX_IMAGE_SIZE[0] or image.size[1] > MAX_IMAGE_SIZE[1]:
            image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=90, optimize=True)
        processed_content = output.getvalue()
        
        return processed_content, '.jpg'
        
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        raise HTTPException(status_code=400, detail="Invalid image file")

@router.get("/api/profile/current")
async def get_current_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's complete profile data"""
    try:
        logger.info(f"Fetching profile for user ID: {current_user.id}")
        
        # Get user from current session to avoid session conflicts
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Safely get attributes with fallbacks
        def safe_get(obj, attr, default=""):
            try:
                return getattr(obj, attr) or default
            except AttributeError:
                logger.warning(f"User model missing attribute: {attr}")
                return default
        
        profile_data = {
            "id": user.id,
            "username": safe_get(user, 'username'),
            "email": safe_get(user, 'email'),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": safe_get(user, 'full_name'),
            "title": safe_get(user, 'title'),
            "company": safe_get(user, 'company'),
            "location": safe_get(user, 'location'),
            "bio": safe_get(user, 'bio'),
            "phone": safe_get(user, 'phone'),
            "website": safe_get(user, 'website'),
            "linkedin_url": safe_get(user, 'linkedin_url'),
            "github_url": safe_get(user, 'github_url'),
            "twitter_url": safe_get(user, 'twitter_url'),
            "industry": safe_get(user, 'industry'),
            "skills": safe_get(user, 'skills'),
            "interests": safe_get(user, 'interests'),
            "education": safe_get(user, 'education'),
            "certifications": safe_get(user, 'certifications'),
            "experience_years": safe_get(user, 'experience_years', 0),
            "profile_image_url": getattr(user, 'get_profile_pic_url', lambda: '/static/uploads/default-avatar.svg')(),
            "show_email": safe_get(user, 'show_email', True),
            "show_phone": safe_get(user, 'show_phone', False),
            "profile_visibility": safe_get(user, 'profile_visibility', 'public'),
            "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None,
            "updated_at": user.updated_at.isoformat() if hasattr(user, 'updated_at') and user.updated_at else None
        }
        
        logger.info(f"Successfully fetched profile for user: {safe_get(user, 'username', user.id)}")
        return {"success": True, "data": profile_data}
        
    except Exception as e:
        logger.error(f"Error fetching profile for user {getattr(current_user, 'id', 'unknown')}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile data: {str(e)}")

@router.post("/api/profile/update")
async def update_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile information"""
    try:
        logger.info(f"Updating profile for user ID: {current_user.id}")
        
        # Get the user from the current database session to avoid session conflicts
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get JSON data
        profile_data = await request.json()
        logger.info(f"Profile update data: {profile_data}")
        
        # Update user fields
        if 'first_name' in profile_data and 'last_name' in profile_data:
            first_name = profile_data['first_name'].strip()
            last_name = profile_data['last_name'].strip()
            
            if not first_name:
                raise HTTPException(status_code=400, detail="First name is required")
            
            if hasattr(user, 'set_names'):
                user.set_names(first_name, last_name)
            else:
                # Fallback if set_names method doesn't exist
                user.full_name = f"{first_name} {last_name}".strip()
        
        # Update other fields
        updateable_fields = {
            'title': 'title',
            'company': 'company', 
            'location': 'location',
            'bio': 'bio',
            'about': 'bio',  # Map 'about' to 'bio'
            'phone': 'phone',
            'website': 'website',
            'plink': 'website',  # Map portfolio link to website
            'linkedin_url': 'linkedin_url',
            'github_url': 'github_url',
            'twitter_url': 'twitter_url',
            'industry': 'industry',
            'education': 'education',
            'certifications': 'certifications'
        }
        
        for field_name, db_field in updateable_fields.items():
            if field_name in profile_data:
                value = profile_data[field_name]
                if isinstance(value, str):
                    value = value.strip()
                setattr(user, db_field, value)
        
        # Handle skills and categories
        if 'skills' in profile_data:
            if isinstance(profile_data['skills'], list):
                user.skills = ','.join(profile_data['skills'])
            else:
                user.skills = profile_data['skills']
        
        if 'categories' in profile_data:
            if isinstance(profile_data['categories'], list):
                user.interests = ','.join(profile_data['categories'])
            else:
                user.interests = profile_data['categories']
        
        if 'interests' in profile_data:
            if isinstance(profile_data['interests'], list):
                user.interests = ','.join(profile_data['interests'])
            else:
                user.interests = profile_data['interests']
        
        # Handle experience years
        if 'experience_years' in profile_data:
            try:
                user.experience_years = int(profile_data['experience_years'])
            except (ValueError, TypeError):
                user.experience_years = 0
        
        # Handle privacy settings
        if 'show_email' in profile_data:
            user.show_email = bool(profile_data['show_email'])
        
        if 'show_phone' in profile_data:
            user.show_phone = bool(profile_data['show_phone'])
        
        if 'notify' in profile_data:
            # Store notification preference (you might want to add this field to User model)
            pass
        
        # Update timestamp
        user.updated_at = datetime.now()
        
        # Save changes
        db.commit()
        
        # Get the updated user from current session instead of refreshing
        updated_user = db.query(User).filter(User.id == current_user.id).first()
        
        logger.info(f"Profile updated successfully for user {getattr(updated_user, 'username', updated_user.id)}")
        
        return {
            "success": True, 
            "message": "Profile updated successfully",
            "data": {
                "full_name": getattr(updated_user, 'full_name', ''),
                "title": getattr(updated_user, 'title', ''),
                "company": getattr(updated_user, 'company', ''),
                "updated_at": updated_user.updated_at.isoformat() if hasattr(updated_user, 'updated_at') and updated_user.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating profile for user {current_user.id}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Database error occurred: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating profile for user {current_user.id}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@router.post("/api/profile/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and update user avatar"""
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate and process image
        processed_content, ext = validate_and_process_image(file_content, file.filename)
        
        # Generate unique filename
        filename = f"profile_{current_user.id}_{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(processed_content)
        
        # Get user from current session to avoid session conflicts
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user profile
        profile_pic_url = f"/static/uploads/profile_pics/{filename}"
        
        # Remove old profile picture if it exists and is not default
        old_pic = user.profile_pic
        if old_pic and old_pic != '/static/uploads/default-avatar.svg' and old_pic.startswith('/static/uploads/'):
            old_file_path = old_pic.replace('/static/', 'static/')
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except OSError:
                    pass  # Ignore if file can't be deleted
        
        # Update profile picture
        if hasattr(user, 'update_profile_pic'):
            user.update_profile_pic(profile_pic_url)
        else:
            user.profile_pic = profile_pic_url
        
        user.updated_at = datetime.now()
        
        # Save changes
        db.commit()
        
        # Get updated user data
        updated_user = db.query(User).filter(User.id == user.id).first()
        
        logger.info(f"Avatar uploaded for user {getattr(updated_user, 'username', updated_user.id)}")
        
        return {
            "success": True,
            "message": "Avatar uploaded successfully",
            "data": {
                "profile_image_url": profile_pic_url,
                "filename": filename,
                "updated_at": updated_user.updated_at.isoformat() if hasattr(updated_user, 'updated_at') and updated_user.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading avatar: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload avatar")

@router.delete("/api/profile/avatar")
async def delete_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user avatar and revert to default"""
    try:
        # Get current profile pic
        old_pic = current_user.profile_pic
        
        # Reset to default
        current_user.profile_pic = None
        current_user.profile_image = 'default-avatar.svg'
        current_user.updated_at = datetime.now()
        
        # Remove old file if it exists
        if old_pic and old_pic.startswith('/static/uploads/'):
            old_file_path = old_pic.replace('/static/', 'static/')
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except OSError:
                    pass
        
        # Save changes
        db.commit()
        
        return {
            "success": True,
            "message": "Avatar removed successfully",
            "data": {
                "profile_image_url": "/static/uploads/default-avatar.svg"
            }
        }
        
    except Exception as e:
        logger.error(f"Error deleting avatar: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete avatar")

@router.get("/api/profile/skills/suggestions")
async def get_skill_suggestions(
    query: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get skill suggestions based on query"""
    
    # Common skills database - in production, this could come from a database
    common_skills = [
        "JavaScript", "Python", "Java", "C++", "React", "Node.js", "Angular", "Vue.js",
        "HTML", "CSS", "SQL", "MongoDB", "PostgreSQL", "MySQL", "Docker", "Kubernetes",
        "AWS", "Azure", "Google Cloud", "Git", "Jenkins", "CI/CD", "Agile", "Scrum",
        "Project Management", "Leadership", "Communication", "Problem Solving",
        "Data Analysis", "Machine Learning", "Artificial Intelligence", "DevOps",
        "Cybersecurity", "Network Administration", "System Administration",
        "Marketing", "Digital Marketing", "SEO", "Content Writing", "Graphic Design",
        "UI/UX Design", "Product Management", "Business Analysis", "Sales",
        "Customer Service", "Human Resources", "Finance", "Accounting"
    ]
    
    if query:
        suggestions = [skill for skill in common_skills 
                      if query.lower() in skill.lower()][:10]
    else:
        suggestions = common_skills[:20]
    
    return {"success": True, "data": suggestions}

@router.get("/api/profile/debug")
async def debug_profile_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Debug endpoint to check user profile information and available fields"""
    try:
        logger.info(f"Debug profile info for user ID: {current_user.id}")
        
        # Get all attributes of the user object
        user_attrs = {}
        for attr in dir(current_user):
            if not attr.startswith('_') and not callable(getattr(current_user, attr)):
                try:
                    value = getattr(current_user, attr)
                    user_attrs[attr] = str(value) if value is not None else None
                except Exception as e:
                    user_attrs[attr] = f"Error accessing: {str(e)}"
        
        # Check for specific methods
        methods_info = {
            'has_set_names': hasattr(current_user, 'set_names'),
            'has_get_profile_pic_url': hasattr(current_user, 'get_profile_pic_url'),
            'has_first_name_property': hasattr(current_user, 'first_name'),
            'has_last_name_property': hasattr(current_user, 'last_name'),
        }
        
        return {
            "success": True,
            "data": {
                "user_id": current_user.id,
                "user_attributes": user_attrs,
                "methods_available": methods_info,
                "table_name": getattr(current_user, '__tablename__', 'unknown')
            }
        }
        
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "user_id": getattr(current_user, 'id', 'unknown')
        }
