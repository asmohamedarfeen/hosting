import os
import logging
import hashlib
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database_enhanced import get_db
from sqlalchemy import and_, func
from models import Streak, StreakLog
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from auth_utils import (
    create_session_token, 
    get_user_from_session, 
    validate_profile_image
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(tags=["Authentication"])

# Get templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Routes

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the main SPA with login page"""
    # Check if main SPA exists
    main_spa_path = os.path.join(BASE_DIR, "fronted", "dist", "public", "index.html")
    if os.path.exists(main_spa_path):
        return FileResponse(main_spa_path, media_type="text/html")
    # Fallback to redirect
    return RedirectResponse(url="/", status_code=302)

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Serve the main SPA with signup page"""
    # Check if main SPA exists
    main_spa_path = os.path.join(BASE_DIR, "fronted", "dist", "public", "index.html")
    if os.path.exists(main_spa_path):
        return FileResponse(main_spa_path, media_type="text/html")
    # Fallback to redirect
    return RedirectResponse(url="/", status_code=302)

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Handle user login"""
    try:
        logger.info("Login attempt started")
        form_data = await request.form()
        identifier = form_data.get("identifier", "").strip()
        password = form_data.get("password", "")
        remember = form_data.get("remember") == "on"
        
        logger.info(f"Login attempt for identifier: {identifier}")
        
        if not identifier or not password:
            logger.warning("Login failed: Missing identifier or password")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email/username and password are required"
            )
        
        # Find user by email or username
        logger.info("Searching for user in database")
        user = db.query(User).filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()
        
        if not user:
            logger.warning(f"Login failed: User not found for identifier: {identifier}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Invalid email or password"}
            )
        
        logger.info(f"User found: {user.username}")
        
        # Check password
        logger.info("Checking password hash")
        if not check_password_hash(user.password_hash, password):
            logger.warning(f"Login failed: Invalid password for user: {user.username}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Invalid email or password"}
            )
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login failed: Inactive account for user: {user.username}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Account is deactivated"}
            )
        
        # Update last login
        logger.info("Updating last login timestamp")
        user.last_login = datetime.now()
        db.commit()
        
        # Log login as activity for streaks (activity_type: 'general')
        try:
            today = date.today()
            # Avoid duplicate log for today
            existing_log = db.query(StreakLog).filter(
                and_(
                    StreakLog.user_id == user.id,
                    StreakLog.activity_type == 'general',
                    func.date(StreakLog.activity_date) == today
                )
            ).first()
            if not existing_log:
                # Create log
                new_log = StreakLog(
                    user_id=user.id,
                    activity_type='general',
                    description='User login'
                )
                db.add(new_log)
                # Get or create streak record
                streak = db.query(Streak).filter(
                    and_(
                        Streak.user_id == user.id,
                        Streak.activity_type == 'general'
                    )
                ).first()
                if not streak:
                    streak = Streak(
                        user_id=user.id,
                        activity_type='general',
                        current_streak=1,
                        longest_streak=1,
                        last_activity_date=datetime.now()
                    )
                    db.add(streak)
                else:
                    if streak.last_activity_date:
                        last_date = streak.last_activity_date.date()
                        if today - last_date == timedelta(days=1):
                            streak.current_streak += 1
                            if streak.current_streak > streak.longest_streak:
                                streak.longest_streak = streak.current_streak
                        elif today - last_date > timedelta(days=1):
                            streak.current_streak = 1
                        # same-day login doesn't change streak count
                    else:
                        streak.current_streak = 1
                        streak.longest_streak = 1
                    streak.last_activity_date = datetime.now()
                db.commit()
        except Exception as streak_err:
            logger.warning(f"Streak logging on login failed: {streak_err}")
            db.rollback()

        # Create session
        logger.info("Creating session token")
        session_token = create_session_token(user.id, db)
        
        # Set cookie
        max_age = 86400 * 30 if remember else 86400  # 30 days or 1 day
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=max_age,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            path="/"
        )
        

        
        logger.info(f"User {user.username} logged in successfully")
        
        # Return JSON response for frontend to handle redirect
        return {
            "message": "Login successful", 
            "user_id": user.id, 
            "session_token": session_token,  # Include session token for frontend
            "redirect_url": "/home"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.post("/signup")
async def signup(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Handle user signup"""
    try:
        logger.info("Signup attempt started")
        form_data = await request.form()
        
        # Extract form data
        username = form_data.get("username", "").strip()
        email = form_data.get("email", "").strip()
        full_name = form_data.get("full_name", "").strip()
        company = form_data.get("company", "").strip()
        password = form_data.get("password", "")
        confirm_password = form_data.get("confirm_password", "")
        profile_image = form_data.get("profile_image", "").strip()
        
        logger.info(f"Signup attempt for username: {username}, email: {email}")
        
        # Validation
        if not all([username, email, full_name, password, confirm_password]):
            logger.warning("Signup failed: Missing required fields")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All required fields must be provided"
            )
        
        if password != confirm_password:
            logger.warning("Signup failed: Passwords do not match")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        if len(password) < 8:
            logger.warning("Signup failed: Password too short")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        if len(username) < 3:
            logger.warning("Signup failed: Username too short")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters long"
            )
        
        # Check if username already exists
        logger.info("Checking if username already exists")
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            logger.warning(f"Signup failed: Username {username} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email already exists
        logger.info("Checking if email already exists")
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            logger.warning(f"Signup failed: Email {email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Validate profile image if provided
        if profile_image:
            try:
                profile_image = validate_profile_image(profile_image)
            except ValueError as e:
                logger.warning(f"Signup failed: Invalid profile image: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        else:
            profile_image = 'default-avatar.svg'
        
        # Create new user
        logger.info("Creating new user in database")
        hashed_password = generate_password_hash(password)
        
        # Determine user type based on email domain
        user_type = 'normal'
        domain = None
        is_verified = False
        
        if '@' in email:
            email_domain = email.split('@')[1].lower()
            # List of common free email providers
            free_domains = {
                'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
                'icloud.com', 'protonmail.com', 'mail.com', 'yandex.com', 'zoho.com',
                'gmx.com', 'live.com', 'msn.com', 'rocketmail.com', 'ymail.com'
            }
            
            if email_domain not in free_domains:
                user_type = 'domain'
                domain = email_domain
                is_verified = True  # Auto-verify domain users for now
                logger.info(f"User {username} classified as domain user with domain: {domain}")
            else:
                logger.info(f"User {username} classified as normal user")
        
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            company=company,
            password_hash=hashed_password,
            profile_image=profile_image,
            user_type=user_type,
            domain=domain,
            is_verified=is_verified,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user {username} registered successfully")
        
        # Automatically log in the user after signup
        session_token = create_session_token(new_user.id, db)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "User registered successfully", 
                "user_id": new_user.id,
                "session_token": session_token,
                "redirect_url": "/home"
            }
        )
        
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error during signup: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Signup error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signup"
        )

@router.post("/logout")
async def logout(response: Response):
    """Handle user logout"""
    try:
        # Clear session cookie
        response.delete_cookie(key="session_token", path="/")
        
        logger.info("User logged out successfully")
        
        # Return redirect response instead of JSON
        return RedirectResponse(url="/auth/login", status_code=303)
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        # Even if there's an error, redirect to login
        return RedirectResponse(url="/auth/login", status_code=303)

@router.get("/logout")
async def logout_get(request: Request, response: Response):
    """Handle user logout via GET request (redirects to login)"""
    try:
        # Clear session cookie
        response.delete_cookie(key="session_token", path="/")
        
        logger.info("User logged out successfully via GET request")
        
        # Redirect to login page
        return RedirectResponse(url="/auth/login", status_code=303)
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        # Even if there's an error, redirect to login
        return RedirectResponse(url="/auth/login", status_code=303)

@router.get("/profile")
async def get_profile(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    try:
        # Get session token from cookie
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Get user from session
        session_data = get_user_from_session(session_token, db)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == session_data['user_id']).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving profile"
        )

@router.get("/profile/{user_id}")
async def get_user_profile_by_id(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get user profile by ID (for HR viewing applicant profiles)"""
    try:
        # Get session token from cookie
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Get current user from session
        session_data = get_user_from_session(session_token, db)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Get current user from database
        current_user = db.query(User).filter(User.id == session_data['user_id']).first()
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Current user not found"
            )
        
        # Check if current user is HR/domain user (with dev bypass and capability method)
        has_hr_capability = False
        try:
            if hasattr(current_user, 'can_manage_applications'):
                has_hr_capability = bool(current_user.can_manage_applications())
        except Exception:
            has_hr_capability = False
        if (current_user.user_type not in ['domain', 'hr', 'hr_user']) and (not has_hr_capability) and (not os.path.exists('.hr_dev_mode')):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. HR privileges required."
            )
        
        # Get target user from database
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return target_user.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User profile retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving user profile"
        )

@router.put("/profile")
async def update_profile(
    request: Request,
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    try:
        # Get session token from cookie
        session_token = request.cookies.get("session_token")
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Get user from session
        session_data = get_user_from_session(session_token, db)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == session_data['user_id']).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get form data
        form_data = await request.form()
        
        # Update allowed fields
        if "full_name" in form_data:
            user.full_name = form_data["full_name"].strip()
        
        if "company" in form_data:
            user.company = form_data["company"].strip()
        
        if "title" in form_data:
            user.title = form_data["title"].strip()
        
        if "location" in form_data:
            user.location = form_data["location"].strip()
        
        if "bio" in form_data:
            user.bio = form_data["bio"].strip()
        
        if "phone" in form_data:
            user.phone = form_data["phone"].strip()
        
        if "website" in form_data:
            user.website = form_data["website"].strip()
        
        # Handle profile image update
        if "profile_image" in form_data:
            try:
                profile_image = validate_profile_image(form_data["profile_image"])
                user.profile_image = profile_image
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        
        user.updated_at = datetime.now()
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User {user.username} profile updated successfully")
        
        return {"message": "Profile updated successfully", "user": user.to_dict()}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating profile"
        )

@router.post("/upload-profile-image")
async def upload_profile_image(
    request: Request,
    db: Session = Depends(get_db)
):
    """Upload a new profile image"""
    try:
        # Get form data
        form_data = await request.form()
        profile_image = form_data.get("profile_image", "").strip()
        
        if not profile_image:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile image is required"
            )
        
        # Get session token from cookie
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Get user from session
        session_data = get_user_from_session(session_token, db)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == session_data['user_id']).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate the profile image
        try:
            validated_image = validate_profile_image(profile_image)
            user.profile_image = validated_image
            user.updated_at = datetime.now()
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"User {user.username} profile image updated successfully")
            
            return {
                "message": "Profile image updated successfully",
                "profile_image": user.profile_image,
                "profile_image_url": user.get_profile_image_url()
            }
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Profile image upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while uploading profile image"
        )

@router.post("/change-password")
async def change_password(
    request: Request,
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        # Get session token from cookie
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Get user from session
        session_data = get_user_from_session(session_token, db)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == session_data['user_id']).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get form data
        form_data = await request.form()
        
        current_password = form_data.get("current_password", "")
        new_password = form_data.get("new_password", "")
        confirm_password = form_data.get("confirm_password", "")
        
        # Validation
        if not all([current_password, new_password, confirm_password]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All password fields are required"
            )
        
        if new_password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New passwords do not match"
            )
        
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long"
            )
        
        # Verify current password
        if not check_password_hash(user.password_hash, current_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        user.updated_at = datetime.now()
        
        db.commit()
        
        logger.info(f"User {user.username} password changed successfully")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while changing password"
        )
