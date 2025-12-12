#!/usr/bin/env python3
"""
Debug script for workshop creation issues
"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def debug_workshop_creation():
    """Debug workshop creation process"""
    print("🔧 Workshop Creation Debug")
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
        
        if login_response.status_code == 200:
            print("✅ User login successful")
            login_data = login_response.json()
            print(f"   User ID: {login_data.get('user_id')}")
        else:
            print(f"❌ User login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
    except Exception as e:
        print(f"❌ User login error: {e}")
        return
    
    # Step 2: Test workshop creation with minimal data
    print("\n2. 📝 Testing workshop creation with minimal data...")
    try:
        workshop_data = {
            "title": "Debug Test Workshop",
            "description": "This is a test workshop for debugging",
            "instructor": "Test Instructor",
            "instructor_email": "instructor@test.com",
            "instructor_bio": "Test instructor bio",
            "category": "Technology",
            "level": "Beginner",
            "duration_hours": 2,
            "max_participants": 20,
            "price": 50.0,
            "currency": "USD",
            "start_date": "2024-12-01T10:00:00",
            "end_date": "2024-12-01T12:00:00",
            "location": "Test Location",
            "is_online": False,
            "materials": ["Laptop", "Notebook"],
            "prerequisites": ["Basic knowledge"],
            "learning_objectives": ["Learn something new"]
        }
        
        print("   Sending workshop data:")
        print(f"   Title: {workshop_data['title']}")
        print(f"   Instructor: {workshop_data['instructor']}")
        print(f"   Category: {workshop_data['category']}")
        
        response = session.post(
            f"{BASE_URL}/workshops/api/workshops",
            json=workshop_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            workshop = response.json()
            print("✅ Workshop created successfully")
            print(f"   Workshop ID: {workshop.get('id')}")
            print(f"   Status: {workshop.get('status')}")
            print(f"   Approval Status: {workshop.get('approval_status')}")
        else:
            print(f"❌ Workshop creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                print("   Could not parse error response as JSON")
    except Exception as e:
        print(f"❌ Error creating workshop: {e}")
    
    # Step 3: Test with different data formats
    print("\n3. 🔄 Testing with different data formats...")
    try:
        # Test with string dates
        workshop_data_str = {
            "title": "Debug Test Workshop 2",
            "description": "This is a test workshop for debugging",
            "instructor": "Test Instructor 2",
            "instructor_email": "instructor2@test.com",
            "instructor_bio": "Test instructor bio 2",
            "category": "Technology",
            "level": "Beginner",
            "duration_hours": 1,
            "max_participants": 10,
            "price": 25.0,
            "currency": "USD",
            "start_date": "2024-12-02T10:00:00Z",
            "end_date": "2024-12-02T11:00:00Z",
            "location": "Test Location 2",
            "is_online": False
        }
        
        response = session.post(
            f"{BASE_URL}/workshops/api/workshops",
            json=workshop_data_str,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Response Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Workshop created with string dates")
        else:
            print(f"❌ Workshop creation failed: {response.text}")
    except Exception as e:
        print(f"❌ Error with string dates: {e}")
    
    # Step 4: Check server logs or error details
    print("\n4. 🔍 Checking server response details...")
    try:
        # Test a simple request to see if server is responding
        health_response = session.get(f"{BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ Server is responding")
        else:
            print(f"❌ Server health check failed: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Server health check error: {e}")
    
    # Step 5: Test authentication
    print("\n5. 🔐 Testing authentication...")
    try:
        profile_response = session.get(f"{BASE_URL}/auth/profile")
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print("✅ Authentication is working")
            print(f"   User: {profile_data.get('username')}")
            print(f"   Type: {profile_data.get('user_type')}")
        else:
            print(f"❌ Authentication failed: {profile_response.status_code}")
            print(f"   Response: {profile_response.text}")
    except Exception as e:
        print(f"❌ Authentication error: {e}")

if __name__ == "__main__":
    debug_workshop_creation()