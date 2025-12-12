import os
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database_enhanced import get_db
from models import User, Session as SessionModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_session_token(user_id: int, db: Session) -> str:
    """Create a session token and store it in the database"""
    token = secrets.token_urlsafe(32)
    
    # Create session record
    session = SessionModel(
        token=token,
        user_id=user_id,
        expires_at=datetime.now() + timedelta(days=7)  # 7 days expiration
    )
    
    db.add(session)
    db.commit()
    
    logger.info(f"Session token created for user {user_id}: {token[:20]}...")
    return token

def get_user_from_session(token: str, db: Session) -> Optional[dict]:
    """Get user from session token with database lookup"""
    if not token:
        return None
    
    # Find active session
    session = db.query(SessionModel).filter(
        SessionModel.token == token,
        SessionModel.is_active == True,
        SessionModel.expires_at > datetime.now()
    ).first()
    
    if not session:
        logger.warning(f"Session token not found or expired: {token[:20]}...")
        return None
    
    logger.info(f"Session token found for user {session.user_id}")
    return {'user_id': session.user_id}

def delete_session(token: str, db: Session) -> bool:
    """Delete a session token from database"""
    session = db.query(SessionModel).filter(SessionModel.token == token).first()
    if session:
        session.is_active = False
        db.commit()
        logger.info(f"Session token deactivated: {token[:20]}...")
        return True
    return False

def validate_profile_image(image_value: str) -> str:
    """Validate and process profile image value"""
    if not image_value:
        return '/static/uploads/default-avatar.svg'
    
    image_value = image_value.strip()
    
    # If it's an external URL, validate the format
    if image_value.startswith(('http://', 'https://')):
        # Basic URL validation
        if len(image_value) > 500:  # Reasonable max length for URLs
            raise ValueError("Profile image URL is too long")
        return image_value
    
    # If it's a local filename, validate it exists
    if not image_value or image_value == 'default-avatar.svg':
        return '/static/uploads/default-avatar.svg'
    
    # Check if the file exists in uploads directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(BASE_DIR, "static", "uploads")
    image_path = os.path.join(uploads_dir, image_value)
    
    if not os.path.exists(image_path):
        logger.warning(f"Profile image file not found: {image_path}")
        return '/static/uploads/default-avatar.svg'
    
    # If it's a local file, return the full path
    if not image_value.startswith('/static/uploads/'):
        return f'/static/uploads/{image_value}'
    
    return image_value

# Utility function to get current user
def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    session_token = request.cookies.get("session_token")
    logger.info(f"Cookie session_token: {session_token[:20] if session_token else 'None'}...")
    
    if not session_token:
        logger.warning("No session token in cookies")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    session_data = get_user_from_session(session_token, db)
    if not session_data:
        logger.warning("Session data not found or expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = db.query(User).filter(User.id == session_data['user_id']).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
