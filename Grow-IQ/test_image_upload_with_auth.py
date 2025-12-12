#!/usr/bin/env python3
"""
Test script to test image upload functionality with proper authentication
"""

import requests
import os
import base64

def create_test_image():
    """Create a simple test image"""
    test_image_path = "test_image.png"
    if not os.path.exists(test_image_path):
        print("Creating test image...")
        # Create a simple 1x1 pixel PNG image
        png_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
        with open(test_image_path, "wb") as f:
            f.write(png_data)
        print(f"Test image created: {test_image_path}")
    return test_image_path

def test_image_upload_with_auth():
    """Test image upload with proper authentication"""
    
    base_url = "http://localhost:8000"
    
    print("🔐 Testing Image Upload with Authentication")
    print("=" * 50)
    
    # Test credentials
    credentials = {
        "identifier": "hr@testcompany.com",
        "password": "hrpass123"
    }
    
    # Create test image
    test_image_path = create_test_image()
    
    # Step 1: Get the login page to establish session
    print("\n1️⃣ Getting login page...")
    try:
        session = requests.Session()
        response = session.get(f"{base_url}/auth/login")
        print(f"   Login page status: {response.status_code}")
        
        if response.status_code != 200:
            print("   ❌ Cannot access login page")
            return
            
    except Exception as e:
        print(f"   ❌ Error accessing login page: {e}")
        return
    
    # Step 2: Attempt to login
    print("\n2️⃣ Attempting to login...")
    try:
        login_data = {
            "identifier": credentials["identifier"],
            "password": credentials["password"]
        }
        
        response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
        print(f"   Login response status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        
        if response.status_code == 303:
            redirect_location = response.headers.get('location', '')
            print(f"   🔄 Redirecting to: {redirect_location}")
            
            if redirect_location == '/home':
                print("   ✅ Login successful, redirected to home")
            else:
                print(f"   ❓ Unexpected redirect location: {redirect_location}")
        elif response.status_code == 200:
            print("   📝 Login page returned (might be showing error)")
            if "error" in response.text.lower() or "invalid" in response.text.lower():
                print("   ❌ Login failed - check credentials")
                return
        else:
            print(f"   ❓ Unexpected login response: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error during login: {e}")
        return
    
    # Step 3: Check if we can access the home page
    print("\n3️⃣ Testing home page access after login...")
    try:
        response = session.get(f"{base_url}/home", allow_redirects=False)
        print(f"   Home page status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Home page accessible after login")
        elif response.status_code == 303:
            redirect_location = response.headers.get('location', '')
            print(f"   🔄 Still redirecting to: {redirect_location}")
            if redirect_location == '/auth/login':
                print("   ❌ Still not authenticated")
                return
        else:
            print(f"   ❓ Unexpected home page status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error accessing home page: {e}")
        return
    
    # Step 4: Test image upload
    print("\n4️⃣ Testing image upload...")
    try:
        with open(test_image_path, "rb") as f:
            files = {"image": ("test.png", f, "image/png")}
            data = {
                "content": "Test post with image upload",
                "post_type": "general",
                "is_public": "true"
            }
            
            response = session.post(f"{base_url}/social/posts/create", files=files, data=data, allow_redirects=False)
        
        print(f"   Upload response status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Image upload successful!")
            try:
                result = response.json()
                print(f"   Response: {result}")
            except:
                print(f"   Response text: {response.text[:200]}")
        elif response.status_code == 401:
            print("   ❌ Still not authenticated")
        elif response.status_code == 303:
            redirect_location = response.headers.get('location', '')
            print(f"   🔄 Redirecting to: {redirect_location}")
        else:
            print(f"   ❓ Unexpected upload response: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error during image upload: {e}")
    
    # Step 5: Check session cookies
    print("\n5️⃣ Checking session cookies...")
    cookies = session.cookies
    print(f"   Session cookies: {dict(cookies)}")
    
    if 'session_token' in cookies:
        print("   ✅ Session token found")
    else:
        print("   ❌ No session token found")
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)
    print("If login is successful and home page is accessible, but image upload fails:")
    print("1. Check the browser console for JavaScript errors")
    print("2. Check the terminal for backend errors")
    print("3. Verify the upload directory permissions")
    print("4. Check if the form data is being sent correctly")
    
    print("\nTo test manually in browser:")
    print("1. Go to http://localhost:8000/auth/login")
    print("2. Login with hr@testcompany.com / hrpass123")
    print("3. Try to create a post with an image")
    print("4. Check browser console and terminal for errors")

if __name__ == "__main__":
    test_image_upload_with_auth()
