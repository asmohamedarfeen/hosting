#!/usr/bin/env python3
"""
Test script for regular user workshop creation
"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_regular_user_workshop():
    """Test regular user workshop creation"""
    print("🔧 Regular User Workshop Creation Test")
    print("=" * 50)
    
    # Step 1: Login as regular user
    print("1. 🔑 Logging in as regular user...")
    session = requests.Session()
    
    try:
        login_data = {
            "identifier": "testuser_api",
            "password": "testpass123"
        }
        login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        print(f"   Status Code: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        
        if login_response.status_code == 200:
            print("✅ Regular user login successful")
            login_data = login_response.json()
            print(f"   User ID: {login_data.get('user_id')}")
        else:
            print(f"❌ Regular user login failed")
            return
    except Exception as e:
        print(f"❌ Regular user login error: {e}")
        return
    
    # Step 2: Test workshop creation as regular user
    print("\n2. 📝 Testing workshop creation as regular user...")
    try:
        workshop_data = {
            "title": "Regular User Test Workshop",
            "description": "This workshop was created by a regular user",
            "instructor": "Regular User Instructor",
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
        
        response = session.post(
            f"{BASE_URL}/workshops/api/workshops",
            json=workshop_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Regular user workshop creation successful")
            workshop = response.json()
            print(f"   Workshop ID: {workshop.get('id')}")
            print(f"   Title: {workshop.get('title')}")
            print(f"   Status: {workshop.get('status')}")
            print(f"   Approval Status: {workshop.get('approval_status')}")
        else:
            print("❌ Regular user workshop creation failed")
            try:
                error_data = response.json()
                print(f"   Error Detail: {error_data.get('detail', 'No detail')}")
                print(f"   Error Message: {error_data.get('message', 'No message')}")
            except:
                print("   Could not parse error response as JSON")
    except Exception as e:
        print(f"❌ Regular user workshop creation error: {e}")
    
    # Step 3: Check if user is authenticated
    print("\n3. 🔍 Checking user authentication...")
    try:
        profile_response = session.get(f"{BASE_URL}/auth/profile")
        print(f"   Profile Status: {profile_response.status_code}")
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print(f"   User Type: {profile_data.get('user_type')}")
            print(f"   Username: {profile_data.get('username')}")
        else:
            print("   Profile check failed")
    except Exception as e:
        print(f"   Profile check error: {e}")

if __name__ == "__main__":
    test_regular_user_workshop()
