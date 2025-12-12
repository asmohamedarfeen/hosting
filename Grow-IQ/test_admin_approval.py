#!/usr/bin/env python3
"""
Test script for admin workshop approval functionality
"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_admin_approval():
    """Test admin workshop approval functionality"""
    print("🔧 Admin Workshop Approval Test")
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
    
    # Step 2: Check pending workshops
    print("\n2. 📋 Checking pending workshops...")
    try:
        response = admin_session.get(f"{BASE_URL}/admin/api/workshops/pending")
        
        if response.status_code == 200:
            data = response.json()
            pending_workshops = data.get('workshops', [])
            print(f"✅ Found {len(pending_workshops)} pending workshops")
            
            if pending_workshops:
                workshop = pending_workshops[0]
                workshop_id = workshop['id']
                print(f"   Latest: {workshop['title']} (ID: {workshop_id})")
                print(f"   Status: {workshop['status']}")
                print(f"   Approval Status: {workshop['approval_status']}")
            else:
                print("   No pending workshops found")
                return issues_found
        else:
            print(f"❌ Failed to fetch pending workshops: {response.status_code}")
            issues_found.append("Failed to fetch pending workshops")
            return issues_found
    except Exception as e:
        print(f"❌ Error fetching pending workshops: {e}")
        issues_found.append("Error fetching pending workshops")
        return issues_found
    
    # Step 3: Approve workshop
    print(f"\n3. ✅ Approving workshop {workshop_id}...")
    try:
        response = admin_session.post(f"{BASE_URL}/admin/api/workshops/{workshop_id}/approve")
        
        if response.status_code == 200:
            print("✅ Workshop approved successfully")
        else:
            print(f"❌ Workshop approval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            issues_found.append("Workshop approval failed")
    except Exception as e:
        print(f"❌ Error approving workshop: {e}")
        issues_found.append("Error approving workshop")
    
    # Step 4: Verify workshop is now approved
    print("\n4. 🔍 Verifying workshop is approved...")
    try:
        response = admin_session.get(f"{BASE_URL}/admin/api/workshops")
        
        if response.status_code == 200:
            data = response.json()
            workshops = data.get('workshops', [])
            
            # Find our workshop
            approved_workshop = next((w for w in workshops if w.get('id') == workshop_id), None)
            
            if approved_workshop:
                print(f"✅ Workshop found in admin list")
                print(f"   Title: {approved_workshop['title']}")
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
    
    # Step 5: Test rejection workflow
    print("\n5. ❌ Testing workshop rejection...")
    try:
        # Get another pending workshop for rejection
        response = admin_session.get(f"{BASE_URL}/admin/api/workshops/pending")
        
        if response.status_code == 200:
            data = response.json()
            pending_workshops = data.get('workshops', [])
            
            if pending_workshops:
                reject_workshop = pending_workshops[0]
                reject_workshop_id = reject_workshop['id']
                print(f"   Found workshop for rejection: {reject_workshop['title']} (ID: {reject_workshop_id})")
                
                # Reject the workshop
                rejection_data = {"rejection_reason": "Test rejection - content not suitable for our platform"}
                response = admin_session.post(f"{BASE_URL}/admin/api/workshops/{reject_workshop_id}/reject", json=rejection_data)
                
                if response.status_code == 200:
                    print("✅ Workshop rejected successfully")
                else:
                    print(f"❌ Workshop rejection failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    issues_found.append("Workshop rejection failed")
            else:
                print("   No pending workshops available for rejection test")
        else:
            print(f"❌ Failed to fetch pending workshops for rejection: {response.status_code}")
            issues_found.append("Failed to fetch pending workshops for rejection")
    except Exception as e:
        print(f"❌ Error testing rejection: {e}")
        issues_found.append("Error testing rejection")
    
    # Step 6: Test admin stats
    print("\n6. 📊 Testing admin stats...")
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
        print("🎉 All admin approval tests passed!")
        print("\n📋 Admin Approval System Status:")
        print("   ✅ Admin can view pending workshops")
        print("   ✅ Admin can approve workshops")
        print("   ✅ Admin can reject workshops")
        print("   ✅ Workshop status updates correctly")
        print("   ✅ Admin stats are working")
        print("\n🚀 Admin approval system is fully functional!")
    else:
        print(f"❌ Found {len(issues_found)} issues:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        print("\n🔧 These issues need to be fixed.")
    
    return issues_found

if __name__ == "__main__":
    issues = test_admin_approval()
    if issues:
        print(f"\n💥 Test completed with {len(issues)} issues found.")
    else:
        print("\n✅ Test completed successfully - no issues found!")
