#!/usr/bin/env python3
"""
Comprehensive test for the workshop system
"""
import requests
import json
import time

# Base URL
BASE_URL = "http://localhost:8000"

def test_workshop_system():
    """Test the complete workshop system"""
    print("🔧 Workshop System Test")
    print("=" * 50)
    
    issues_found = []
    
    # Step 1: Test Server Health
    print("1. 🏥 Testing server health...")
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ Server is healthy")
        else:
            print(f"❌ Server health check failed: {health_response.status_code}")
            issues_found.append("Server health check failed")
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        issues_found.append("Server not responding")
        return issues_found
    
    # Step 2: Test Authentication
    print("\n2. 🔐 Testing authentication...")
    session = requests.Session()
    
    try:
        login_data = {
            "identifier": "testuser_api",
            "password": "password123"
        }
        login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Login successful")
            login_data = login_response.json()
            print(f"   User ID: {login_data.get('user_id')}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            issues_found.append("Login failed")
    except Exception as e:
        print(f"❌ Login error: {e}")
        issues_found.append("Login error")
    
    # Step 3: Test Workshop Categories API
    print("\n3. 📚 Testing workshop categories...")
    try:
        categories_response = session.get(f"{BASE_URL}/workshops/api/categories")
        if categories_response.status_code == 200:
            print("✅ Categories API working")
            categories_data = categories_response.json()
            print(f"   Available categories: {len(categories_data.get('categories', []))}")
        else:
            print(f"❌ Categories API failed: {categories_response.status_code}")
            issues_found.append("Categories API failed")
    except Exception as e:
        print(f"❌ Categories API error: {e}")
        issues_found.append("Categories API error")
    
    # Step 4: Test Workshop Levels API
    print("\n4. 🎯 Testing workshop levels...")
    try:
        levels_response = session.get(f"{BASE_URL}/workshops/api/levels")
        if levels_response.status_code == 200:
            print("✅ Levels API working")
            levels_data = levels_response.json()
            print(f"   Available levels: {len(levels_data.get('levels', []))}")
        else:
            print(f"❌ Levels API failed: {levels_response.status_code}")
            issues_found.append("Levels API failed")
    except Exception as e:
        print(f"❌ Levels API error: {e}")
        issues_found.append("Levels API error")
    
    # Step 5: Test Get Workshops
    print("\n5. 📖 Testing get workshops...")
    try:
        workshops_response = session.get(f"{BASE_URL}/workshops/api/workshops?status=published")
        if workshops_response.status_code == 200:
            print("✅ Get workshops working")
            workshops_data = workshops_response.json()
            workshops = workshops_data.get('workshops', [])
            print(f"   Found {len(workshops)} published workshops")
            
            if workshops:
                workshop = workshops[0]
                print(f"   Sample workshop: {workshop.get('title')}")
                print(f"   Instructor: {workshop.get('instructor')}")
                print(f"   Category: {workshop.get('category')}")
                print(f"   Level: {workshop.get('level')}")
                print(f"   Price: ${workshop.get('price', 0) / 100}")
        else:
            print(f"❌ Get workshops failed: {workshops_response.status_code}")
            issues_found.append("Get workshops failed")
    except Exception as e:
        print(f"❌ Get workshops error: {e}")
        issues_found.append("Get workshops error")
    
    # Step 6: Test Create Workshop
    print("\n6. ➕ Testing create workshop...")
    try:
        workshop_data = {
            "title": "API Test Workshop",
            "description": "This workshop was created via API testing",
            "instructor": "API Test Instructor",
            "instructor_email": "test@example.com",
            "instructor_bio": "Test instructor for API testing",
            "category": "technical",
            "level": "intermediate",
            "duration_hours": 3,
            "max_participants": 15,
            "price": 2500,  # $25.00
            "currency": "USD",
            "start_date": "2024-12-15T14:00:00",
            "end_date": "2024-12-15T17:00:00",
            "location": "Online",
            "is_online": True,
            "meeting_link": "https://meet.google.com/api-test",
            "materials": ["Laptop", "Internet connection", "Notebook"],
            "prerequisites": ["Basic programming knowledge"],
            "learning_objectives": ["Learn API testing", "Understand workshop creation"],
            "status": "draft"
        }
        
        create_response = session.post(
            f"{BASE_URL}/workshops/api/workshops",
            json=workshop_data,
            headers={"Content-Type": "application/json"}
        )
        
        if create_response.status_code == 200:
            print("✅ Create workshop working")
            new_workshop = create_response.json()
            workshop_id = new_workshop.get('id')
            print(f"   Created workshop ID: {workshop_id}")
            print(f"   Title: {new_workshop.get('title')}")
            print(f"   Status: {new_workshop.get('status')}")
        else:
            print(f"❌ Create workshop failed: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
            issues_found.append("Create workshop failed")
    except Exception as e:
        print(f"❌ Create workshop error: {e}")
        issues_found.append("Create workshop error")
    
    # Step 7: Test Get Specific Workshop
    print("\n7. 🔍 Testing get specific workshop...")
    try:
        if 'workshop_id' in locals():
            workshop_detail_response = session.get(f"{BASE_URL}/workshops/api/workshops/{workshop_id}")
            if workshop_detail_response.status_code == 200:
                print("✅ Get specific workshop working")
                workshop_detail = workshop_detail_response.json()
                print(f"   Retrieved workshop: {workshop_detail.get('title')}")
            else:
                print(f"❌ Get specific workshop failed: {workshop_detail_response.status_code}")
                issues_found.append("Get specific workshop failed")
        else:
            print("⚠️  Skipping specific workshop test (no workshop ID)")
    except Exception as e:
        print(f"❌ Get specific workshop error: {e}")
        issues_found.append("Get specific workshop error")
    
    # Step 8: Test Workshop Registration
    print("\n8. 📝 Testing workshop registration...")
    try:
        # Get a published workshop for registration
        workshops_response = session.get(f"{BASE_URL}/workshops/api/workshops?status=published")
        if workshops_response.status_code == 200:
            workshops_data = workshops_response.json()
            workshops = workshops_data.get('workshops', [])
            
            if workshops:
                test_workshop = workshops[0]
                test_workshop_id = test_workshop.get('id')
                
                registration_data = {
                    "workshop_id": test_workshop_id,
                    "notes": "Test registration via API"
                }
                
                registration_response = session.post(
                    f"{BASE_URL}/workshops/api/registrations",
                    json=registration_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if registration_response.status_code == 200:
                    print("✅ Workshop registration working")
                    registration = registration_response.json()
                    print(f"   Registration ID: {registration.get('id')}")
                    print(f"   Workshop: {registration.get('workshop', {}).get('title')}")
                else:
                    print(f"❌ Workshop registration failed: {registration_response.status_code}")
                    print(f"   Response: {registration_response.text}")
                    issues_found.append("Workshop registration failed")
            else:
                print("⚠️  No published workshops available for registration test")
        else:
            print("❌ Could not fetch workshops for registration test")
            issues_found.append("Could not fetch workshops for registration")
    except Exception as e:
        print(f"❌ Workshop registration error: {e}")
        issues_found.append("Workshop registration error")
    
    # Step 9: Test Get User Registrations
    print("\n9. 📋 Testing get user registrations...")
    try:
        registrations_response = session.get(f"{BASE_URL}/workshops/api/registrations")
        if registrations_response.status_code == 200:
            print("✅ Get user registrations working")
            registrations_data = registrations_response.json()
            registrations = registrations_data if isinstance(registrations_data, list) else []
            print(f"   Found {len(registrations)} registrations")
        else:
            print(f"❌ Get user registrations failed: {registrations_response.status_code}")
            issues_found.append("Get user registrations failed")
    except Exception as e:
        print(f"❌ Get user registrations error: {e}")
        issues_found.append("Get user registrations error")
    
    # Step 10: Test Frontend Access
    print("\n10. 🌐 Testing frontend access...")
    try:
        frontend_response = session.get(f"{BASE_URL}/workshop")
        if frontend_response.status_code == 200:
            print("✅ Workshop frontend is accessible")
            if "workshop" in frontend_response.text.lower() or "react" in frontend_response.text.lower():
                print("✅ Frontend is serving workshop page")
            else:
                print("⚠️  Frontend might not be serving workshop page correctly")
        else:
            print(f"❌ Workshop frontend access failed: {frontend_response.status_code}")
            issues_found.append("Workshop frontend access failed")
    except Exception as e:
        print(f"❌ Workshop frontend access error: {e}")
        issues_found.append("Workshop frontend access error")
    
    # Summary
    print("\n" + "=" * 50)
    if not issues_found:
        print("🎉 All workshop system tests passed!")
        print("\n📋 Workshop System Status:")
        print("   ✅ Server is running and healthy")
        print("   ✅ Authentication is working")
        print("   ✅ Workshop categories API is working")
        print("   ✅ Workshop levels API is working")
        print("   ✅ Get workshops API is working")
        print("   ✅ Create workshop API is working")
        print("   ✅ Get specific workshop API is working")
        print("   ✅ Workshop registration API is working")
        print("   ✅ Get user registrations API is working")
        print("   ✅ Workshop frontend is accessible")
        print("\n🚀 The workshop system is fully functional!")
    else:
        print(f"❌ Found {len(issues_found)} issues:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        print("\n🔧 These issues need to be fixed.")
    
    return issues_found

if __name__ == "__main__":
    issues = test_workshop_system()
    if issues:
        print(f"\n💥 Test completed with {len(issues)} issues found.")
    else:
        print("\n✅ Test completed successfully - no issues found!")
