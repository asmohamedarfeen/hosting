#!/usr/bin/env python3
"""
Script to check the exact login error
"""
import requests

def check_login_error():
    """Check what error occurs during login"""
    base_url = "http://localhost:8000"
    
    print("🔍 Checking Login Error Details...")
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
    
    # Test 2: Try to login with a test user
    print("\n2️⃣ Testing login with test user...")
    test_data = {
        "identifier": "testuser",
        "password": "testpass"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", data=test_data)
        print(f"Login response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
        elif response.status_code == 401:
            print("✅ Login properly rejected (wrong credentials)")
        elif response.status_code == 500:
            print("❌ Server error - this is the problem!")
            print(f"Response text: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print("Response is not JSON")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Login request failed: {e}")
    
    # Test 3: Check what users exist
    print("\n3️⃣ Checking existing users...")
    try:
        # Try to create a new user to see if that works
        signup_data = {
            "username": f"debuguser_{int(time.time())}",
            "email": f"debug_{int(time.time())}@test.com",
            "full_name": "Debug User",
            "company": "Debug Co",
            "password": "DebugPass123!",
            "confirm_password": "DebugPass123!"
        }
        
        response = requests.post(f"{base_url}/auth/signup", data=signup_data)
        print(f"Signup test status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Signup works - the issue is with existing users")
        else:
            print(f"❌ Signup also fails: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Signup test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Analysis:")
    print("If you see a 500 error with details, that's the root cause.")
    print("If signup works but login fails, the issue is with existing user data.")
    print("\n🔧 Next Steps:")
    print("1. Check your server terminal for Python error messages")
    print("2. Look for tracebacks or exception details")
    print("3. We may need to reset the database after all")

if __name__ == "__main__":
    import time
    print("Starting Login Error Check...")
    print("Make sure your app is running on port 8000!")
    print()
    
    input("Press Enter when your app is running, or Ctrl+C to cancel...")
    check_login_error()
