#!/usr/bin/env python3
"""
Test authentication flow for workshop creation
"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """Test authentication flow"""
    print("🔧 Authentication Flow Test")
    print("=" * 50)
    
    # Step 1: Test admin login
    print("1. 🔑 Testing admin login...")
    admin_session = requests.Session()
    
    try:
        login_data = {
            "identifier": "master_admin",
            "password": "MasterAdmin2024!"
        }
        login_response = admin_session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        print(f"   Status Code: {login_response.status_code}")
        print(f"   Content Type: {login_response.headers.get('content-type')}")
        
        if login_response.status_code == 200:
            try:
                login_json = login_response.json()
                print("✅ Admin login successful (JSON response)")
                print(f"   User ID: {login_json.get('user_id')}")
            except:
                print("⚠️  Admin login returned non-JSON response")
                print(f"   Response: {login_response.text[:200]}...")
        else:
            print(f"❌ Admin login failed: {login_response.status_code}")
    except Exception as e:
        print(f"❌ Admin login error: {e}")
    
    # Step 2: Test admin profile
    print("\n2. 👤 Testing admin profile...")
    try:
        profile_response = admin_session.get(f"{BASE_URL}/auth/profile")
        print(f"   Status Code: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            try:
                profile_json = profile_response.json()
                print("✅ Admin profile successful")
                print(f"   User Type: {profile_json.get('user_type')}")
                print(f"   Username: {profile_json.get('username')}")
            except:
                print("⚠️  Admin profile returned non-JSON response")
        else:
            print(f"❌ Admin profile failed: {profile_response.status_code}")
    except Exception as e:
        print(f"❌ Admin profile error: {e}")
    
    # Step 3: Test admin workshop creation
    print("\n3. 📝 Testing admin workshop creation...")
    try:
        workshop_data = {
            "title": "Auth Test Workshop",
            "description": "Testing authentication flow",
            "instructor": "Auth Test Instructor",
            "category": "Technology",
            "level": "Beginner",
            "duration_hours": 1,
            "max_participants": 5,
            "price": 25,
            "currency": "USD",
            "start_date": "2024-12-01T10:00:00",
            "end_date": "2024-12-01T11:00:00",
            "location": "Test Location",
            "is_online": False
        }
        
        response = admin_session.post(
            f"{BASE_URL}/workshops/api/workshops",
            json=workshop_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Admin workshop creation successful")
        else:
            print(f"❌ Admin workshop creation failed: {response.text}")
    except Exception as e:
        print(f"❌ Admin workshop creation error: {e}")
    
    # Step 4: Test regular user login
    print("\n4. 🔑 Testing regular user login...")
    regular_session = requests.Session()
    
    try:
        login_data = {
            "identifier": "testuser_api",
            "password": "testpass123"
        }
        login_response = regular_session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        print(f"   Status Code: {login_response.status_code}")
        print(f"   Content Type: {login_response.headers.get('content-type')}")
        
        if login_response.status_code == 200:
            try:
                login_json = login_response.json()
                print("✅ Regular user login successful (JSON response)")
                print(f"   User ID: {login_json.get('user_id')}")
            except:
                print("⚠️  Regular user login returned non-JSON response")
                print(f"   Response: {login_response.text[:200]}...")
        else:
            print(f"❌ Regular user login failed: {login_response.status_code}")
    except Exception as e:
        print(f"❌ Regular user login error: {e}")
    
    # Step 5: Test regular user profile
    print("\n5. 👤 Testing regular user profile...")
    try:
        profile_response = regular_session.get(f"{BASE_URL}/auth/profile")
        print(f"   Status Code: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            try:
                profile_json = profile_response.json()
                print("✅ Regular user profile successful")
                print(f"   User Type: {profile_json.get('user_type')}")
                print(f"   Username: {profile_json.get('username')}")
            except:
                print("⚠️  Regular user profile returned non-JSON response")
        else:
            print(f"❌ Regular user profile failed: {profile_response.status_code}")
    except Exception as e:
        print(f"❌ Regular user profile error: {e}")
    
    # Step 6: Test regular user workshop creation
    print("\n6. 📝 Testing regular user workshop creation...")
    try:
        workshop_data = {
            "title": "Regular User Auth Test Workshop",
            "description": "Testing regular user authentication flow",
            "instructor": "Regular Auth Test Instructor",
            "category": "Technology",
            "level": "Beginner",
            "duration_hours": 1,
            "max_participants": 5,
            "price": 25,
            "currency": "USD",
            "start_date": "2024-12-01T10:00:00",
            "end_date": "2024-12-01T11:00:00",
            "location": "Test Location",
            "is_online": False
        }
        
        response = regular_session.post(
            f"{BASE_URL}/workshops/api/workshops",
            json=workshop_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Regular user workshop creation successful")
        else:
            print(f"❌ Regular user workshop creation failed: {response.text}")
    except Exception as e:
        print(f"❌ Regular user workshop creation error: {e}")

if __name__ == "__main__":
    test_auth_flow()
