#!/usr/bin/env python3
"""
Test workshop creation with master admin
"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_workshop_creation():
    """Test workshop creation with master admin"""
    print("🔧 Workshop Creation Test (Fixed)")
    print("=" * 50)
    
    # Step 1: Login as master admin
    print("1. 🔑 Logging in as master admin...")
    session = requests.Session()
    
    try:
        login_data = {
            "identifier": "master_admin",
            "password": "MasterAdmin2024!"
        }
        login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Admin login successful")
            login_data = login_response.json()
            print(f"   User ID: {login_data.get('user_id')}")
        else:
            print(f"❌ Admin login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return
    
    # Step 2: Test workshop creation
    print("\n2. 📝 Testing workshop creation...")
    try:
        workshop_data = {
            "title": "Test Workshop for Debugging",
            "description": "This is a test workshop to debug the creation process",
            "instructor": "Master Admin",
            "instructor_email": "admin@glow-iq.com",
            "instructor_bio": "Master administrator with extensive experience",
            "category": "Technology",
            "level": "Beginner",
            "duration_hours": 2,
            "max_participants": 25,
            "price": 75.0,
            "currency": "USD",
            "start_date": "2024-12-15T10:00:00",
            "end_date": "2024-12-15T12:00:00",
            "location": "Online",
            "is_online": True,
            "meeting_link": "https://meet.google.com/test-workshop",
            "materials": ["Laptop", "Notebook", "Internet connection"],
            "prerequisites": ["Basic computer skills", "Interest in technology"],
            "learning_objectives": [
                "Understand the fundamentals",
                "Learn practical applications",
                "Gain hands-on experience"
            ]
        }
        
        print("   Sending workshop data:")
        print(f"   Title: {workshop_data['title']}")
        print(f"   Instructor: {workshop_data['instructor']}")
        print(f"   Category: {workshop_data['category']}")
        print(f"   Price: ${workshop_data['price']}")
        
        response = session.post(
            f"{BASE_URL}/workshops/api/workshops",
            json=workshop_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            workshop = response.json()
            print("✅ Workshop created successfully!")
            print(f"   Workshop ID: {workshop.get('id')}")
            print(f"   Title: {workshop.get('title')}")
            print(f"   Status: {workshop.get('status')}")
            print(f"   Approval Status: {workshop.get('approval_status')}")
            print(f"   Created By: {workshop.get('created_by')}")
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
    
    # Step 3: Test with minimal data
    print("\n3. 🔄 Testing with minimal data...")
    try:
        minimal_workshop_data = {
            "title": "Minimal Test Workshop",
            "description": "Minimal workshop for testing",
            "instructor": "Test Instructor",
            "instructor_email": "instructor@test.com",
            "instructor_bio": "Test bio",
            "category": "Technology",
            "level": "Beginner",
            "duration_hours": 1,
            "max_participants": 10,
            "price": 25.0,
            "currency": "USD",
            "start_date": "2024-12-20T10:00:00",
            "end_date": "2024-12-20T11:00:00",
            "location": "Test Location",
            "is_online": False
        }
        
        response = session.post(
            f"{BASE_URL}/workshops/api/workshops",
            json=minimal_workshop_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Response Status: {response.status_code}")
        if response.status_code == 200:
            workshop = response.json()
            print("✅ Minimal workshop created successfully!")
            print(f"   Workshop ID: {workshop.get('id')}")
            print(f"   Title: {workshop.get('title')}")
        else:
            print(f"❌ Minimal workshop creation failed: {response.text}")
    except Exception as e:
        print(f"❌ Error creating minimal workshop: {e}")
    
    # Step 4: Check workshop list
    print("\n4. 📋 Checking workshop list...")
    try:
        response = session.get(f"{BASE_URL}/workshops/api/workshops")
        if response.status_code == 200:
            data = response.json()
            workshops = data.get('workshops', [])
            print(f"✅ Found {len(workshops)} workshops")
            
            # Show recent workshops
            for workshop in workshops[:3]:
                print(f"   - {workshop.get('title')} (ID: {workshop.get('id')}) - {workshop.get('approval_status')}")
        else:
            print(f"❌ Failed to fetch workshops: {response.status_code}")
    except Exception as e:
        print(f"❌ Error fetching workshops: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Workshop Creation Test Complete!")

if __name__ == "__main__":
    test_workshop_creation()
