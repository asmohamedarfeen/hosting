import os
import logging
import requests
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth_utils import get_user_from_session, create_session_token, delete_session
from datetime import datetime, timedelta
import secrets
import hashlib

# Initialize router
router = APIRouter(prefix="/auth", tags=["oauth"])

from config import settings

# OAuth Configuration
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
# Use environment variable if set, otherwise auto-generate from request
GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI

def get_oauth_redirect_uri(request: Request) -> str:
    """Get OAuth redirect URI, using env var or auto-detecting from request"""
    if GOOGLE_REDIRECT_URI:
        return GOOGLE_REDIRECT_URI
    # Auto-generate from request
    from config import get_base_url
    base_url = get_base_url(request)
    return f"{base_url}/auth/google/callback"

# OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Store OAuth state tokens (in production, use Redis or database)
oauth_states = {}

# ==================== GOOGLE OAUTH ====================

@router.get("/google")
async def google_oauth_login(request: Request):
    """Initiate Google OAuth login"""
    try:
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        oauth_states[state] = {
            "created_at": datetime.utcnow(),
            "redirect_after": request.query_params.get("redirect", "/dashboard")
        }
        
        # Get redirect URI (use env var or auto-detect)
        redirect_uri = get_oauth_redirect_uri(request)
        
        # Build OAuth URL
        oauth_params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        # Construct authorization URL
        auth_url = f"{GOOGLE_AUTH_URL}?"
        auth_url += "&".join([f"{k}={v}" for k, v in oauth_params.items()])
        
        return RedirectResponse(url=auth_url, status_code=302)
        
    except Exception as e:
        logging.error(f"Error initiating Google OAuth: {str(e)}")
        raise HTTPException(status_code=500, detail="Error initiating OAuth login")

@router.get("/google/callback")
async def google_oauth_callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    error: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        # Check for OAuth errors
        if error:
            logging.error(f"Google OAuth error: {error}")
            return RedirectResponse(url="/login?error=oauth_failed", status_code=302)
        
        # Validate state parameter
        if state not in oauth_states:
            logging.error("Invalid OAuth state parameter")
            return RedirectResponse(url="/login?error=invalid_state", status_code=302)
        
        state_data = oauth_states.pop(state)
        
        # Check if state is expired (5 minutes)
        if datetime.utcnow() - state_data["created_at"] > timedelta(minutes=5):
            logging.error("OAuth state expired")
            return RedirectResponse(url="/login?error=state_expired", status_code=302)
        
        # Get redirect URI (use env var or auto-detect)
        redirect_uri = get_oauth_redirect_uri(request)
        
        # Exchange authorization code for access token
        token_response = requests.post(GOOGLE_TOKEN_URL, data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        })
        
        if token_response.status_code != 200:
            logging.error(f"Token exchange failed: {token_response.text}")
            return RedirectResponse(url="/login?error=token_exchange_failed", status_code=302)
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            logging.error("No access token received")
            return RedirectResponse(url="/login?error=no_access_token", status_code=302)
        
        # Get user information from Google
        userinfo_response = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if userinfo_response.status_code != 200:
            logging.error(f"Failed to get user info: {userinfo_response.text}")
            return RedirectResponse(url="/login?error=userinfo_failed", status_code=302)
        
        userinfo = userinfo_response.json()
        
        # Process user information
        user = await process_google_user(userinfo, db)
        
        # Create session
        session_token = create_session_token(user.id)
        
        # Redirect to dashboard or intended page
        redirect_url = state_data.get("redirect_after", "/dashboard")
        
        response = RedirectResponse(url=redirect_url, status_code=302)
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=3600 * 24 * 7  # 7 days
        )
        
        return response
        
    except Exception as e:
        logging.error(f"Error processing Google OAuth callback: {str(e)}")
        return RedirectResponse(url="/login?error=callback_failed", status_code=302)

# ==================== OAUTH USER PROCESSING ====================

async def process_google_user(userinfo: Dict[str, Any], db: Session) -> User:
    """Process Google user information and create/update user account"""
    try:
        google_id = userinfo.get("id")
        email = userinfo.get("email")
        name = userinfo.get("name")
        given_name = userinfo.get("given_name", "")
        family_name = userinfo.get("family_name", "")
        picture = userinfo.get("picture")
        
        if not email:
            raise ValueError("No email provided by Google")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            # Update existing user with latest Google info
            existing_user.full_name = name or existing_user.full_name
            existing_user.profile_image = picture or existing_user.profile_image
            existing_user.last_login = datetime.utcnow()
            existing_user.updated_at = datetime.utcnow()
            
            # Add Google ID if not present
            if not existing_user.google_id:
                existing_user.google_id = google_id
            
            db.commit()
            db.refresh(existing_user)
            return existing_user
        
        else:
            # Create new user
            new_user = User(
                username=generate_unique_username(email, db),
                email=email,
                full_name=name or f"{given_name} {family_name}".strip(),
                profile_image=picture or "default-avatar.svg",
                google_id=google_id,
                is_verified=True,  # Google accounts are pre-verified
                user_type="normal",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            logging.info(f"Created new user via Google OAuth: {new_user.email}")
            return new_user
            
    except Exception as e:
        logging.error(f"Error processing Google user: {str(e)}")
        raise

def generate_unique_username(email: str, db: Session) -> str:
    """Generate a unique username from email"""
    base_username = email.split("@")[0]
    username = base_username
    counter = 1
    
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1
    
    return username

# ==================== OAUTH LOGOUT ====================

@router.get("/logout")
async def oauth_logout(request: Request):
    """Logout user and clear session"""
    try:
        session_token = request.cookies.get('session_token')
        if session_token:
            delete_session(session_token)
        
        response = RedirectResponse(url="/login", status_code=302)
        response.delete_cookie("session_token")
        
        return response
        
    except Exception as e:
        logging.error(f"Error during logout: {str(e)}")
        return RedirectResponse(url="/login", status_code=302)

# ==================== OAUTH STATUS ====================

@router.get("/status")
async def oauth_status(request: Request, db: Session = Depends(get_db)):
    """Check OAuth authentication status"""
    try:
        session_token = request.cookies.get('session_token')
        if not session_token:
            return {"authenticated": False, "user": None}
        
        user_id = get_user_from_session(session_token)
        if not user_id:
            return {"authenticated": False, "user": None}
        
        user = db.query(User).get(user_id)
        if not user:
            return {"authenticated": False, "user": None}
        
        return {
            "authenticated": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "profile_image": user.profile_image,
                "user_type": user.user_type,
                "is_verified": user.is_verified
            }
        }
        
    except Exception as e:
        logging.error(f"Error checking OAuth status: {str(e)}")
        return {"authenticated": False, "user": None}

# ==================== OAUTH ERROR HANDLING ====================

@router.get("/error")
async def oauth_error(
    error: str = Query(...),
    error_description: Optional[str] = Query(None)
):
    """Handle OAuth errors"""
    error_messages = {
        "access_denied": "Access was denied by the user",
        "invalid_scope": "Invalid OAuth scope requested",
        "server_error": "OAuth server error occurred",
        "temporarily_unavailable": "OAuth service temporarily unavailable",
        "oauth_failed": "OAuth authentication failed",
        "invalid_state": "Invalid OAuth state parameter",
        "state_expired": "OAuth state parameter expired",
        "token_exchange_failed": "Failed to exchange authorization code for token",
        "no_access_token": "No access token received from OAuth provider",
        "userinfo_failed": "Failed to retrieve user information",
        "callback_failed": "OAuth callback processing failed"
    }
    
    error_message = error_messages.get(error, error_description or "Unknown OAuth error")
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth Error - CareerConnect</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
            .error {{ color: #d32f2f; margin: 20px 0; }}
            .back-link {{ margin-top: 30px; }}
            a {{ color: #1976d2; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h1>OAuth Authentication Error</h1>
        <div class="error">
            <h2>{error_message}</h2>
        </div>
        <div class="back-link">
            <a href="/login">← Back to Login</a>
        </div>
    </body>
    </html>
    """)
