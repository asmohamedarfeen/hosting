"""
User management router.
Handles user registration, login, profile updates, and user listing.
Integrated with main database authentication.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from ..db import get_db
from ..models import User
from ..schemas import (
    UserCreate, UserResponse, UserUpdate, UserLogin, Token, UserListResponse
)
from ..auth import (
    get_current_active_user, authenticate_user, get_password_hash, create_user_token
)
from ..auth_integration import auth_integration_service
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Token: JWT token for the new user
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if user with email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        bio=user_data.bio
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create and return token
    token_data = create_user_token(db_user)
    return Token(**token_data)


@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate and login a user using main database credentials.
    
    Args:
        user_credentials: User login credentials
        db: Database session
        
    Returns:
        Token: JWT token for the authenticated user
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # First try main database authentication
    try:
        main_auth_result = auth_integration_service.authenticate_user_with_main_db(
            user_credentials.email, user_credentials.password
        )
        
        if main_auth_result:
            # User authenticated with main database, create messaging token
            token_data = auth_integration_service.create_messaging_token(main_auth_result)
            return Token(**token_data)
    except Exception as e:
        logger.warning(f"Main database authentication failed: {e}")
        # Continue to local authentication
    
    # Fallback to local messaging database authentication
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create and return token
    token_data = create_user_token(user)
    return Token(**token_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user's profile
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    
    Args:
        user_update: Profile update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserResponse: Updated user profile
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if email is being changed and if it already exists
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all users (excluding current user).
    
    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserListResponse: List of users and total count
    """
    # Get total count
    total = db.query(func.count(User.id)).filter(User.id != current_user.id).scalar()
    
    # Get users (excluding current user)
    users = (
        db.query(User)
        .filter(User.id != current_user.id)
        .filter(User.is_active == True)
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return UserListResponse(users=users, total=total)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID.
    
    Args:
        user_id: ID of the user to retrieve
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserResponse: User profile
        
    Raises:
        HTTPException: If user not found
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot get own profile using this endpoint"
        )
    
    user = db.query(User).filter(
        User.id == user_id,
        User.is_active == True
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/auto-login", response_model=Token)
async def auto_login_with_main_app(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Automatically login using main app session.
    This endpoint checks for main app session and creates messaging token.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Token: JWT token for messaging system
        
    Raises:
        HTTPException: If no valid main app session found
    """
    try:
        # Get session token from cookies
        session_token = request.cookies.get('session_token')
        
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No session token found"
            )
        
        # Try to authenticate with main app
        main_user = auth_integration_service.authenticate_user_with_main_db(session_token)
        
        if not main_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session token"
            )
        
        # Check if user exists in messaging system
        messaging_user = db.query(User).filter(User.email == main_user['email']).first()
        
        if not messaging_user:
            # Create user in messaging system if they don't exist
            messaging_user = User(
                name=main_user.get('full_name') or main_user.get('username', ''),
                email=main_user['email'],
                password_hash="",  # No password needed for auto-login
                bio=main_user.get('bio', ''),
                is_active=True
            )
            db.add(messaging_user)
            db.commit()
            db.refresh(messaging_user)
        
        # Create JWT token for messaging system
        token = create_user_token(messaging_user.id, messaging_user.email)
        
        return Token(access_token=token, token_type="bearer")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Auto-login failed: {str(e)}"
        )
