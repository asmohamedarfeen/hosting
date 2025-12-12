#!/usr/bin/env python3
"""
Test route to debug authentication dependency injection
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from auth_utils import get_current_user
from models import User

router = APIRouter(prefix="/test-auth", tags=["Test Auth"])

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """Test protected route that requires authentication"""
    return JSONResponse({
        "message": "This route is protected",
        "user_id": current_user.id,
        "username": current_user.username
    })

@router.get("/public")
async def public_route():
    """Test public route that doesn't require authentication"""
    return JSONResponse({
        "message": "This route is public"
    })
