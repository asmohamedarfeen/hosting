#!/usr/bin/env python3
"""
Test script to check if app_working.py can import streak routes
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test importing the main app components"""
    try:
        print("🔄 Testing imports...")
        
        # Test importing streak routes
        print("1️⃣ Testing streak_routes import...")
        from streak_routes import router as streak_router
        print("   ✅ streak_routes imported successfully")
        print(f"   Router prefix: {streak_router.prefix}")
        print(f"   Router routes: {[route.path for route in streak_router.routes]}")
        
        # Test importing app_working
        print("\n2️⃣ Testing app_working import...")
        from app_working import app
        print("   ✅ app_working imported successfully")
        
        # Check if streak routes are included
        print("\n3️⃣ Checking if streak routes are included in app...")
        streak_routes_found = False
        print(f"   Total routes in app: {len(app.routes)}")
        
        for i, route in enumerate(app.routes):
            print(f"   Route {i}: {route}")
            if hasattr(route, 'prefix'):
                print(f"     Prefix: {route.prefix}")
            if hasattr(route, 'path'):
                print(f"     Path: {route.path}")
            if hasattr(route, 'name'):
                print(f"     Name: {route.name}")
            print()
            
            if hasattr(route, 'prefix') and route.prefix == '/streaks':
                streak_routes_found = True
                print(f"   ✅ Found streak routes with prefix: {route.prefix}")
                break
        
        if not streak_routes_found:
            print("   ❌ Streak routes not found in app")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Qrow IQ App Imports")
    print("=" * 50)
    
    success = test_imports()
    
    if success:
        print("\n🎉 All imports successful!")
    else:
        print("\n💥 Import test failed!")
        sys.exit(1)
