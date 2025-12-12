#!/usr/bin/env python3
"""
Simple test to check basic functionality
"""
import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing Imports...")
    print("=" * 50)
    
    try:
        print("1️⃣ Testing database import...")
        from database import get_db
        print("✅ Database import successful")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        print("2️⃣ Testing models import...")
        from models import User, Post, Connection, Comment
        print("✅ Models import successful")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    try:
        print("3️⃣ Testing auth_utils import...")
        from auth_utils import get_current_user
        print("✅ Auth utils import successful")
    except Exception as e:
        print(f"❌ Auth utils import failed: {e}")
        return False
    
    try:
        print("4️⃣ Testing home_routes import...")
        from home_routes import router
        print("✅ Home routes import successful")
        print(f"   Router: {router}")
        print(f"   Router routes: {len(router.routes)}")
        for route in router.routes:
            print(f"     {route.methods} {route.path}")
    except Exception as e:
        print(f"❌ Home routes import failed: {e}")
        return False
    
    try:
        print("5️⃣ Testing app import...")
        from app import app
        print("✅ App import successful")
        print(f"   App routes: {len(app.routes)}")
        print("   First few routes:")
        for i, route in enumerate(app.routes[:5]):
            if hasattr(route, 'path'):
                print(f"     {getattr(route, 'methods', 'MOUNT')} {route.path}")
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting Simple Import Test...")
    print()
    
    success = test_imports()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All imports successful!")
        print("The issue might be in the route registration or server startup.")
    else:
        print("❌ Some imports failed!")
        print("This explains why the routes aren't working.")
    
    print("\n🔧 Next Steps:")
    print("1. Fix any import errors above")
    print("2. Check if the database is properly initialized")
    print("3. Try starting the server again")
