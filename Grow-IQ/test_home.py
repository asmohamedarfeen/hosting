#!/usr/bin/env python3
"""
Test script to check if home route is working
"""
import requests

def test_home_route():
    """Test the home route"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Home Route...")
    print("=" * 50)
    
    # Test 1: Check if app is running
    print("\n1️⃣ Checking if app is running...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ App is running")
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Database: {health_data.get('database')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to app: {e}")
        print("   Make sure your app is running with: python start.py")
        return
    
    # Test 2: Check root route
    print("\n2️⃣ Testing root route (/)...")
    try:
        response = requests.get(f"{base_url}/", allow_redirects=False)
        print(f"Root response status: {response.status_code}")
        if response.status_code == 303:
            print("✅ Root route redirects (as expected)")
            print(f"   Redirect location: {response.headers.get('location')}")
        else:
            print(f"❌ Unexpected root response: {response.status_code}")
    except Exception as e:
        print(f"❌ Root route test failed: {e}")
    
    # Test 3: Check home route
    print("\n3️⃣ Testing home route (/home)...")
    try:
        response = requests.get(f"{base_url}/home", allow_redirects=False)
        print(f"Home route status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Home route accessible")
            print(f"   Content type: {response.headers.get('content-type')}")
            print(f"   Content length: {response.headers.get('content-length')}")
        elif response.status_code == 401:
            print("✅ Home route requires authentication (as expected)")
        elif response.status_code == 404:
            print("❌ Home route not found - this is the problem!")
            print("   The route might not be properly registered")
        else:
            print(f"❌ Unexpected home response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Home route test failed: {e}")
    
    # Test 4: Check available routes
    print("\n4️⃣ Checking available routes...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ API docs accessible")
            print("   Check http://localhost:8000/docs for all available routes")
        else:
            print(f"❌ API docs not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Analysis:")
    print("If you see 'Home route not found', the route registration has an issue.")
    print("If you see 'Home route requires authentication', that's working correctly.")
    print("\n🔧 Next Steps:")
    print("1. Check the server logs for any error messages")
    print("2. Verify that home_routes.py is properly imported")
    print("3. Check if there are any syntax errors in the route files")

if __name__ == "__main__":
    print("Starting Home Route Test...")
    print("Make sure your app is running on port 8000!")
    print()
    
    input("Press Enter when your app is running, or Ctrl+C to cancel...")
    test_home_route()
