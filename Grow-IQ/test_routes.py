#!/usr/bin/env python3
"""
Simple test routes to check if route registration is working
"""

from fastapi import APIRouter

# Create a simple router
test_router = APIRouter(prefix="/test", tags=["Test"])

@test_router.get("/")
async def test_root():
    """Test root endpoint"""
    return {"message": "Test routes are working!"}

@test_router.get("/hello")
async def test_hello():
    """Test hello endpoint"""
    return {"message": "Hello from test routes!"}
