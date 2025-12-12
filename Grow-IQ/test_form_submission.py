#!/usr/bin/env python3
"""
Test script to verify form submission to login and signup endpoints
"""
import requests
import time

def test_form_submission():
    """Test actual form submission to auth endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Form Submission to Auth Endpoints...")
    print("=" * 60)
    
    # Test 1: Test signup with form data
    print("\n1️⃣ Testing signup form submission...")
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "email": f"testuser_{int(time.time())}@example.com",
        "full_name": "Test User",
        "company": "Test Company",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/signup", data=test_user)
        print(f"Signup response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Signup successful!")
            try:
                data = response.json()
                print(f"   Response data: {data}")
            except:
                print("   Response is not JSON")
        else:
            print(f"❌ Signup failed")
            print(f"   Response text: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Signup request failed: {e}")
    
    # Test 2: Test login with the created user
    print("\n2️⃣ Testing login form submission...")
    try:
        login_data = {
            "identifier": test_user["username"],
            "password": test_user["password"]
        }
        
        response = requests.post(f"{base_url}/auth/login", data=login_data)
        print(f"Login response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            try:
                data = response.json()
                print(f"   Response data: {data}")
            except:
                print("   Response is not JSON")
        else:
            print(f"❌ Login failed")
            print(f"   Response text: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Login request failed: {e}")
    
    # Test 3: Test login with existing user (from database test)
    print("\n3️⃣ Testing login with existing user...")
    try:
        existing_user_data = {
            "identifier": "MURUGANANDAM",  # From database test
            "password": "test123"  # Try a common password
        }
        
        response = requests.post(f"{base_url}/auth/login", data=existing_user_data)
        print(f"Existing user login status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Existing user login successful!")
        elif response.status_code == 401:
            print("✅ Existing user login properly rejected (wrong password)")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Existing user login test failed: {e}")
    
    # Test 4: Test with invalid form data
    print("\n4️⃣ Testing invalid form data...")
    try:
        invalid_data = {
            "identifier": "",
            "password": ""
        }
        
        response = requests.post(f"{base_url}/auth/login", data=invalid_data)
        print(f"Invalid data login status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Invalid data properly rejected")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Invalid data test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Form Submission Test Summary:")
    print("This will help identify if the issue is with:")
    print("1. Backend endpoints")
    print("2. Form data handling")
    print("3. Response format")
    print("4. JavaScript form submission")

if __name__ == "__main__":
    print("Starting Form Submission Tests...")
    print("Make sure your app is running on port 8000!")
    print()
    
    input("Press Enter when your app is running, or Ctrl+C to cancel...")
    test_form_submission()
