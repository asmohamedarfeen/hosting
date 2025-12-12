#!/usr/bin/env python3
"""
Test script to verify Qrow IQ authentication functionality
"""
import requests
import json
import time

def test_auth_functionality():
    """Test the complete authentication flow"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Qrow IQ Authentication...")
    print("=" * 50)
    
    # Test 1: Check if login page is accessible
    print("\n1️⃣ Testing login page accessibility...")
    try:
        response = requests.get(f"{base_url}/auth/login")
        if response.status_code == 200:
            print("✅ Login page is accessible")
            if "login_modern.css" in response.text:
                print("✅ CSS file is referenced")
            else:
                print("❌ CSS file is NOT referenced")
        else:
            print(f"❌ Login page returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Test signup functionality
    print("\n2️⃣ Testing signup functionality...")
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "email": f"testuser_{int(time.time())}@example.com",
        "full_name": "Test User",
        "company": "Test Company",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!"
    }
    
    try:
        # Create form data
        form_data = test_user.copy()
        
        response = requests.post(f"{base_url}/auth/signup", data=form_data)
        print(f"Signup status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Signup successful!")
            try:
                data = response.json()
                print(f"   User ID: {data.get('user_id')}")
                print(f"   Message: {data.get('message')}")
            except:
                print("   Response is not JSON")
        else:
            print(f"❌ Signup failed with status: {response.status_code}")
            try:
                data = response.json()
                print(f"   Error: {data.get('detail')}")
            except:
                print("   Response is not JSON")
                
    except Exception as e:
        print(f"❌ Signup error: {e}")
    
    # Test 3: Test login functionality
    print("\n3️⃣ Testing login functionality...")
    try:
        login_data = {
            "identifier": test_user["username"],  # Try with username
            "password": test_user["password"]
        }
        
        response = requests.post(f"{base_url}/auth/login", data=login_data)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            try:
                data = response.json()
                print(f"   User ID: {data.get('user_id')}")
                print(f"   Message: {data.get('message')}")
            except:
                print("   Response is not JSON")
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            try:
                data = response.json()
                print(f"   Error: {data.get('detail')}")
            except:
                print("   Response is not JSON")
                
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    # Test 4: Test login with email
    print("\n4️⃣ Testing login with email...")
    try:
        login_data = {
            "identifier": test_user["email"],  # Try with email
            "password": test_user["password"]
        }
        
        response = requests.post(f"{base_url}/auth/login", data=login_data)
        print(f"Login with email status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login with email successful!")
        else:
            print(f"❌ Login with email failed with status: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Login with email error: {e}")
    
    # Test 5: Test invalid login
    print("\n5️⃣ Testing invalid login...")
    try:
        invalid_data = {
            "identifier": "nonexistentuser",
            "password": "wrongpassword"
        }
        
        response = requests.post(f"{base_url}/auth/login", data=invalid_data)
        print(f"Invalid login status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Invalid login properly rejected!")
        else:
            print(f"❌ Invalid login should return 401, got {response.status_code}")
                
    except Exception as e:
        print(f"❌ Invalid login test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Authentication Test Summary:")
    print("If all tests show ✅, your authentication is working correctly!")
    print("\n🚀 Next steps:")
    print("1. Start your app: python start.py")
    print("2. Visit: http://localhost:8000")
    print("3. Should redirect to login page")
    print("4. Test signup with a new account")
    print("5. Test login with the created account")
    print("6. Should redirect to dashboard after successful login")

if __name__ == "__main__":
    print("Starting Qrow IQ Authentication Tests...")
    print("Make sure your app is running on port 8000!")
    print()
    
    input("Press Enter when your app is running, or Ctrl+C to cancel...")
    test_auth_functionality()
