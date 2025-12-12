#!/usr/bin/env python3
"""
Test script for AdminDesk functionality
"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_admin_desk():
    """Test AdminDesk functionality"""
    print("🔧 AdminDesk Test")
    print("=" * 50)
    
    issues_found = []
    
    # Step 1: Login as admin
    print("1. 🔑 Logging in as admin...")
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
            return issues_found
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        issues_found.append("Admin login error")
        return issues_found
    
    # Step 2: Test AdminDesk frontend access
    print("\n2. 🌐 Testing AdminDesk frontend access...")
    try:
        response = admin_session.get(f"{BASE_URL}/admin-desk")
        if response.status_code == 200:
            print("✅ AdminDesk frontend accessible")
            if "admin" in response.text.lower() or "workshop" in response.text.lower():
                print("✅ Frontend is serving AdminDesk")
            else:
                print("⚠️  Frontend might not be serving AdminDesk correctly")
        else:
            print(f"❌ AdminDesk frontend access failed: {response.status_code}")
            issues_found.append("AdminDesk frontend access failed")
    except Exception as e:
        print(f"❌ AdminDesk frontend access error: {e}")
        issues_found.append("AdminDesk frontend access error")
    
    # Step 3: Test pending workshops API
    print("\n3. 📋 Testing pending workshops API...")
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
    
    # Step 4: Test approved workshops API
    print("\n4. ✅ Testing approved workshops API...")
    try:
        response = admin_session.get(f"{BASE_URL}/admin/api/workshops?approval_status=approved")
        if response.status_code == 200:
            data = response.json()
            approved_workshops = data.get('workshops', [])
            print(f"✅ Found {len(approved_workshops)} approved workshops")
        else:
            print(f"❌ Failed to fetch approved workshops: {response.status_code}")
            issues_found.append("Failed to fetch approved workshops")
    except Exception as e:
        print(f"❌ Error fetching approved workshops: {e}")
        issues_found.append("Error fetching approved workshops")
    
    # Step 5: Test rejected workshops API
    print("\n5. ❌ Testing rejected workshops API...")
    try:
        response = admin_session.get(f"{BASE_URL}/admin/api/workshops?approval_status=rejected")
        if response.status_code == 200:
            data = response.json()
            rejected_workshops = data.get('workshops', [])
            print(f"✅ Found {len(rejected_workshops)} rejected workshops")
        else:
            print(f"❌ Failed to fetch rejected workshops: {response.status_code}")
            issues_found.append("Failed to fetch rejected workshops")
    except Exception as e:
        print(f"❌ Error fetching rejected workshops: {e}")
        issues_found.append("Error fetching rejected workshops")
    
    # Step 6: Test all workshops API
    print("\n6. 📚 Testing all workshops API...")
    try:
        response = admin_session.get(f"{BASE_URL}/admin/api/workshops")
        if response.status_code == 200:
            data = response.json()
            all_workshops = data.get('workshops', [])
            print(f"✅ Found {len(all_workshops)} total workshops")
            
            # Count by status
            pending_count = len([w for w in all_workshops if w.get('approval_status') == 'pending'])
            approved_count = len([w for w in all_workshops if w.get('approval_status') == 'approved'])
            rejected_count = len([w for w in all_workshops if w.get('approval_status') == 'rejected'])
            
            print(f"   Pending: {pending_count}")
            print(f"   Approved: {approved_count}")
            print(f"   Rejected: {rejected_count}")
        else:
            print(f"❌ Failed to fetch all workshops: {response.status_code}")
            issues_found.append("Failed to fetch all workshops")
    except Exception as e:
        print(f"❌ Error fetching all workshops: {e}")
        issues_found.append("Error fetching all workshops")
    
    # Step 7: Test workshop approval workflow
    print("\n7. 🔄 Testing workshop approval workflow...")
    try:
        # Get a pending workshop
        response = admin_session.get(f"{BASE_URL}/admin/api/workshops/pending")
        if response.status_code == 200:
            data = response.json()
            pending_workshops = data.get('workshops', [])
            
            if pending_workshops:
                workshop_id = pending_workshops[0]['id']
                print(f"   Testing with workshop ID: {workshop_id}")
                
                # Approve the workshop
                approve_response = admin_session.post(f"{BASE_URL}/admin/api/workshops/{workshop_id}/approve")
                if approve_response.status_code == 200:
                    print("   ✅ Workshop approved successfully")
                    
                    # Verify it's now approved
                    verify_response = admin_session.get(f"{BASE_URL}/admin/api/workshops")
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        workshops = verify_data.get('workshops', [])
                        approved_workshop = next((w for w in workshops if w.get('id') == workshop_id), None)
                        
                        if approved_workshop and approved_workshop.get('approval_status') == 'approved':
                            print("   ✅ Workshop status updated correctly")
                        else:
                            print("   ❌ Workshop status not updated correctly")
                            issues_found.append("Workshop status not updated after approval")
                    else:
                        print("   ❌ Failed to verify workshop status")
                        issues_found.append("Failed to verify workshop status")
                else:
                    print(f"   ❌ Workshop approval failed: {approve_response.status_code}")
                    issues_found.append("Workshop approval failed")
            else:
                print("   ⚠️  No pending workshops available for testing")
        else:
            print(f"❌ Failed to fetch pending workshops for testing: {response.status_code}")
            issues_found.append("Failed to fetch pending workshops for testing")
    except Exception as e:
        print(f"❌ Error testing approval workflow: {e}")
        issues_found.append("Error testing approval workflow")
    
    # Step 8: Test admin stats
    print("\n8. 📊 Testing admin stats...")
    try:
        response = admin_session.get(f"{BASE_URL}/admin/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Admin stats retrieved successfully")
            print(f"   Total Users: {stats.get('users', {}).get('total', 0)}")
            print(f"   Total Workshops: {stats.get('workshops', {}).get('total', 0)}")
            print(f"   Published Workshops: {stats.get('workshops', {}).get('published', 0)}")
        else:
            print(f"❌ Failed to fetch admin stats: {response.status_code}")
            issues_found.append("Failed to fetch admin stats")
    except Exception as e:
        print(f"❌ Error fetching admin stats: {e}")
        issues_found.append("Error fetching admin stats")
    
    # Summary
    print("\n" + "=" * 50)
    if not issues_found:
        print("🎉 All AdminDesk tests passed!")
        print("\n📋 AdminDesk Status:")
        print("   ✅ AdminDesk frontend accessible")
        print("   ✅ Pending workshops API working")
        print("   ✅ Approved workshops API working")
        print("   ✅ Rejected workshops API working")
        print("   ✅ All workshops API working")
        print("   ✅ Workshop approval workflow working")
        print("   ✅ Admin stats working")
        print("\n🚀 AdminDesk is fully functional!")
        print("\n🔗 Access URLs:")
        print("   Admin Dashboard: http://localhost:8000/admin")
        print("   Admin Desk: http://localhost:8000/admin-desk")
    else:
        print(f"❌ Found {len(issues_found)} issues:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        print("\n🔧 These issues need to be fixed.")
    
    return issues_found

if __name__ == "__main__":
    issues = test_admin_desk()
    if issues:
        print(f"\n💥 Test completed with {len(issues)} issues found.")
    else:
        print("\n✅ Test completed successfully - no issues found!")
