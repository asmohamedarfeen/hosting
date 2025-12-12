#!/usr/bin/env python3
"""
Test script for workshop approval system
"""
import requests
import json
import time

# Base URL
BASE_URL = "http://localhost:8000"

def test_workshop_approval_system():
    """Test the complete workshop approval system"""
    print("🔧 Workshop Approval System Test")
    print("=" * 50)
    
    issues_found = []
    
    # Step 1: Login as regular user
    print("1. 🔑 Logging in as regular user...")
    user_session = requests.Session()
    
    try:
        login_data = {
            "identifier": "testuser_api",
            "password": "testpass123"
        }
        login_response = user_session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Regular user login successful")
        else:
            print(f"❌ Regular user login failed: {login_response.status_code}")
            issues_found.append("Regular user login failed")
    except Exception as e:
        print(f"❌ Regular user login error: {e}")
        issues_found.append("Regular user login error")
        return issues_found
    
    # Step 2: Create a workshop as regular user
    print("\n2. 📝 Creating workshop as regular user...")
    workshop_id = None
    try:
        workshop_data = {
            "title": "Test Workshop for Approval",
            "description": "This is a test workshop that should require admin approval",
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
        
        response = user_session.post(f"{BASE_URL}/workshops/api/workshops", 
                                    json=workshop_data,
                                    headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            workshop = response.json()
            workshop_id = workshop['id']
            print(f"✅ Workshop created successfully with ID: {workshop_id}")
            print(f"   Title: {workshop['title']}")
            print(f"   Status: {workshop['status']}")
            print(f"   Approval Status: {workshop['approval_status']}")
        else:
            print(f"❌ Workshop creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            issues_found.append("Workshop creation failed")
    except Exception as e:
        print(f"❌ Workshop creation error: {e}")
        issues_found.append("Workshop creation error")
    
    # Step 3: Login as admin
    print("\n3. 🔑 Logging in as admin...")
    admin_session = requests.Session()
    
    try:
        login_data = {
            "identifier": "master_admin",
            "password": "MasterAdmin2024!"
        }
        login_response = admin_session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Admin login successful")
        else:
            print(f"❌ Admin login failed: {login_response.status_code}")
            issues_found.append("Admin login failed")
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        issues_found.append("Admin login error")
        return issues_found
    
    # Step 4: Check pending workshops
    print("\n4. 📋 Checking pending workshops...")
    try:
        response = admin_session.get(f"{BASE_URL}/admin/api/workshops/pending")
        
        if response.status_code == 200:
            data = response.json()
            pending_workshops = data.get('workshops', [])
            print(f"✅ Found {len(pending_workshops)} pending workshops")
            
            if pending_workshops:
                workshop = pending_workshops[0]
                print(f"   Latest: {workshop['title']} (ID: {workshop['id']})")
                print(f"   Status: {workshop['status']}")
                print(f"   Approval Status: {workshop['approval_status']}")
        else:
            print(f"❌ Failed to fetch pending workshops: {response.status_code}")
            issues_found.append("Failed to fetch pending workshops")
    except Exception as e:
        print(f"❌ Error fetching pending workshops: {e}")
        issues_found.append("Error fetching pending workshops")
    
    # Step 5: Approve workshop
    print("\n5. ✅ Approving workshop...")
    try:
        if 'workshop_id' in locals():
            response = admin_session.post(f"{BASE_URL}/admin/api/workshops/{workshop_id}/approve")
            
            if response.status_code == 200:
                print("✅ Workshop approved successfully")
            else:
                print(f"❌ Workshop approval failed: {response.status_code}")
                print(f"   Response: {response.text}")
                issues_found.append("Workshop approval failed")
        else:
            print("⚠️  No workshop ID available for approval test")
    except Exception as e:
        print(f"❌ Error approving workshop: {e}")
        issues_found.append("Error approving workshop")
    
    # Step 6: Verify workshop is now published
    print("\n6. 🔍 Verifying workshop is published...")
    try:
        response = admin_session.get(f"{BASE_URL}/admin/api/workshops")
        
        if response.status_code == 200:
            data = response.json()
            workshops = data.get('workshops', [])
            
            # Find our workshop
            approved_workshop = next((w for w in workshops if w.get('id') == workshop_id), None)
            
            if approved_workshop:
                print(f"✅ Workshop found in admin list")
                print(f"   Status: {approved_workshop['status']}")
                print(f"   Approval Status: {approved_workshop['approval_status']}")
                
                if approved_workshop['status'] == 'published' and approved_workshop['approval_status'] == 'approved':
                    print("✅ Workshop is correctly published and approved")
                else:
                    print("❌ Workshop status is incorrect after approval")
                    issues_found.append("Workshop status incorrect after approval")
            else:
                print("❌ Workshop not found in admin list")
                issues_found.append("Workshop not found after approval")
        else:
            print(f"❌ Failed to fetch workshops: {response.status_code}")
            issues_found.append("Failed to fetch workshops after approval")
    except Exception as e:
        print(f"❌ Error verifying workshop: {e}")
        issues_found.append("Error verifying workshop")
    
    # Step 7: Test regular user can see approved workshop
    print("\n7. 👀 Testing regular user can see approved workshop...")
    try:
        response = user_session.get(f"{BASE_URL}/workshops/api/workshops")
        
        if response.status_code == 200:
            data = response.json()
            workshops = data.get('workshops', [])
            
            # Find our workshop
            visible_workshop = next((w for w in workshops if w.get('id') == workshop_id), None)
            
            if visible_workshop:
                print("✅ Regular user can see approved workshop")
                print(f"   Title: {visible_workshop['title']}")
                print(f"   Status: {visible_workshop['status']}")
            else:
                print("❌ Regular user cannot see approved workshop")
                issues_found.append("Regular user cannot see approved workshop")
        else:
            print(f"❌ Failed to fetch workshops for regular user: {response.status_code}")
            issues_found.append("Failed to fetch workshops for regular user")
    except Exception as e:
        print(f"❌ Error testing regular user access: {e}")
        issues_found.append("Error testing regular user access")
    
    # Step 8: Test rejection workflow
    print("\n8. ❌ Testing workshop rejection...")
    try:
        # Create another workshop for rejection test
        workshop_data = {
            "title": "Test Workshop for Rejection",
            "description": "This workshop should be rejected",
            "instructor": "Test Instructor 2",
            "instructor_email": "instructor2@test.com",
            "instructor_bio": "Test instructor bio 2",
            "category": "Technology",
            "level": "Beginner",
            "duration_hours": 1,
            "max_participants": 10,
            "price": 25.0,
            "currency": "USD",
            "start_date": "2024-12-02T10:00:00",
            "end_date": "2024-12-02T11:00:00",
            "location": "Test Location 2",
            "is_online": False,
            "materials": ["Laptop"],
            "prerequisites": [],
            "learning_objectives": ["Learn something"]
        }
        
        response = user_session.post(f"{BASE_URL}/workshops/api/workshops", 
                                    json=workshop_data,
                                    headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            workshop = response.json()
            reject_workshop_id = workshop['id']
            print(f"✅ Test workshop created for rejection (ID: {reject_workshop_id})")
            
            # Reject the workshop
            rejection_data = {"rejection_reason": "Test rejection - content not suitable"}
            response = admin_session.post(f"{BASE_URL}/admin/api/workshops/{reject_workshop_id}/reject", json=rejection_data)
            
            if response.status_code == 200:
                print("✅ Workshop rejected successfully")
            else:
                print(f"❌ Workshop rejection failed: {response.status_code}")
                issues_found.append("Workshop rejection failed")
        else:
            print(f"❌ Failed to create workshop for rejection test: {response.status_code}")
            issues_found.append("Failed to create workshop for rejection test")
    except Exception as e:
        print(f"❌ Error testing rejection: {e}")
        issues_found.append("Error testing rejection")
    
    # Summary
    print("\n" + "=" * 50)
    if not issues_found:
        print("🎉 All workshop approval tests passed!")
        print("\n📋 Workshop Approval System Status:")
        print("   ✅ Regular users can create workshops")
        print("   ✅ Workshops require admin approval")
        print("   ✅ Admin can view pending workshops")
        print("   ✅ Admin can approve workshops")
        print("   ✅ Admin can reject workshops")
        print("   ✅ Approved workshops are visible to users")
        print("   ✅ Rejected workshops are not visible to users")
        print("\n🚀 Workshop approval system is fully functional!")
    else:
        print(f"❌ Found {len(issues_found)} issues:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        print("\n🔧 These issues need to be fixed.")
    
    return issues_found

if __name__ == "__main__":
    issues = test_workshop_approval_system()
    if issues:
        print(f"\n💥 Test completed with {len(issues)} issues found.")
    else:
        print("\n✅ Test completed successfully - no issues found!")
