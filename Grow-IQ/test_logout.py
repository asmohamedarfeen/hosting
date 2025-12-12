#!/usr/bin/env python3
"""
Test script to verify logout functionality
"""
import requests

def test_logout():
    """Test logout functionality"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Logout Functionality...")
    print("=" * 40)
    
    # Test 1: POST logout (should redirect to login)
    print("\n1️⃣ Testing POST logout...")
    try:
        response = requests.post(f"{base_url}/auth/logout", allow_redirects=False)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 303:
            redirect_url = response.headers.get('location')
            print(f"✅ Redirects to: {redirect_url}")
            if redirect_url == "/auth/login":
                print("✅ Correctly redirects to login page!")
            else:
                print(f"❌ Expected /auth/login, got {redirect_url}")
        else:
            print(f"❌ Expected 303 redirect, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: GET logout (should also redirect to login)
    print("\n2️⃣ Testing GET logout...")
    try:
        response = requests.get(f"{base_url}/auth/logout", allow_redirects=False)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 303:
            redirect_url = response.headers.get('location')
            print(f"✅ Redirects to: {redirect_url}")
            if redirect_url == "/auth/login":
                print("✅ Correctly redirects to login page!")
            else:
                print(f"❌ Expected /auth/login, got {redirect_url}")
        else:
            print(f"❌ Expected 303 redirect, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Verify login page is accessible after logout
    print("\n3️⃣ Testing login page accessibility...")
    try:
        response = requests.get(f"{base_url}/auth/login")
        if response.status_code == 200:
            print("✅ Login page is accessible after logout")
        else:
            print(f"❌ Login page returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 Logout Test Summary:")
    print("If all tests show ✅, logout is working correctly!")
    print("The app should now redirect to login page after logout.")

if __name__ == "__main__":
    print("Starting Logout Test...")
    print("Make sure your app is running on port 8000!")
    print()
    
    input("Press Enter when your app is running, or Ctrl+C to cancel...")
    test_logout()
