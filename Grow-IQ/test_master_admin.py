#!/usr/bin/env python3
"""
Test script for master admin functionality
"""
import requests
import json
import time

# Base URL
BASE_URL = "http://localhost:8000"

def test_master_admin():
    """Test master admin functionality"""
    print("🔐 Master Admin Test")
    print("=" * 50)
    
    issues_found = []
    
    # Step 1: Test Master Admin Login
    print("1. 🔑 Testing master admin login...")
    session = requests.Session()
    
    try:
        login_data = {
            "identifier": "master_admin",
            "password": "MasterAdmin2024!"
        }
        login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Master admin login successful")
            login_data = login_response.json()
            print(f"   User ID: {login_data.get('user_id')}")
        else:
            print(f"❌ Master admin login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            issues_found.append("Master admin login failed")
    except Exception as e:
        print(f"❌ Master admin login error: {e}")
        issues_found.append("Master admin login error")
        return issues_found
    
    # Step 2: Test Admin Stats API
    print("\n2. 📊 Testing admin stats API...")
    try:
        stats_response = session.get(f"{BASE_URL}/admin/api/stats")
        if stats_response.status_code == 200:
            print("✅ Admin stats API working")
            stats_data = stats_response.json()
            print(f"   Total Users: {stats_data.get('users', {}).get('total', 0)}")
            print(f"   Active Users: {stats_data.get('users', {}).get('active', 0)}")
            print(f"   Total Workshops: {stats_data.get('workshops', {}).get('total', 0)}")
            print(f"   Total Jobs: {stats_data.get('jobs', {}).get('total', 0)}")
        else:
            print(f"❌ Admin stats API failed: {stats_response.status_code}")
            print(f"   Response: {stats_response.text}")
            issues_found.append("Admin stats API failed")
    except Exception as e:
        print(f"❌ Admin stats API error: {e}")
        issues_found.append("Admin stats API error")
    
    # Step 3: Test Get All Users API
    print("\n3. 👥 Testing get all users API...")
    try:
        users_response = session.get(f"{BASE_URL}/admin/api/users")
        if users_response.status_code == 200:
            print("✅ Get all users API working")
            users_data = users_response.json()
            users = users_data.get('users', [])
            print(f"   Found {len(users)} users")
            
            # Check if master admin is in the list
            master_admin = next((u for u in users if u.get('username') == 'master_admin'), None)
            if master_admin:
                print(f"   Master admin found: {master_admin.get('full_name')}")
                print(f"   User type: {master_admin.get('user_type')}")
                print(f"   Is active: {master_admin.get('is_active')}")
            else:
                print("   ⚠️  Master admin not found in users list")
        else:
            print(f"❌ Get all users API failed: {users_response.status_code}")
            issues_found.append("Get all users API failed")
    except Exception as e:
        print(f"❌ Get all users API error: {e}")
        issues_found.append("Get all users API error")
    
    # Step 4: Test Get All Workshops API
    print("\n4. 📚 Testing get all workshops API...")
    try:
        workshops_response = session.get(f"{BASE_URL}/admin/api/workshops")
        if workshops_response.status_code == 200:
            print("✅ Get all workshops API working")
            workshops_data = workshops_response.json()
            workshops = workshops_data.get('workshops', [])
            print(f"   Found {len(workshops)} workshops")
        else:
            print(f"❌ Get all workshops API failed: {workshops_response.status_code}")
            issues_found.append("Get all workshops API failed")
    except Exception as e:
        print(f"❌ Get all workshops API error: {e}")
        issues_found.append("Get all workshops API error")
    
    # Step 5: Test Get All Jobs API
    print("\n5. 💼 Testing get all jobs API...")
    try:
        jobs_response = session.get(f"{BASE_URL}/admin/api/jobs")
        if jobs_response.status_code == 200:
            print("✅ Get all jobs API working")
            jobs_data = jobs_response.json()
            jobs = jobs_data.get('jobs', [])
            print(f"   Found {len(jobs)} jobs")
        else:
            print(f"❌ Get all jobs API failed: {jobs_response.status_code}")
            issues_found.append("Get all jobs API failed")
    except Exception as e:
        print(f"❌ Get all jobs API error: {e}")
        issues_found.append("Get all jobs API error")
    
    # Step 6: Test Admin Dashboard Frontend
    print("\n6. 🌐 Testing admin dashboard frontend...")
    try:
        frontend_response = session.get(f"{BASE_URL}/admin")
        if frontend_response.status_code == 200:
            print("✅ Admin dashboard frontend accessible")
            if "admin" in frontend_response.text.lower() or "react" in frontend_response.text.lower():
                print("✅ Frontend is serving admin dashboard")
            else:
                print("⚠️  Frontend might not be serving admin dashboard correctly")
        else:
            print(f"❌ Admin dashboard frontend access failed: {frontend_response.status_code}")
            issues_found.append("Admin dashboard frontend access failed")
    except Exception as e:
        print(f"❌ Admin dashboard frontend access error: {e}")
        issues_found.append("Admin dashboard frontend access error")
    
    # Step 7: Test User Management (if we have other users)
    print("\n7. 👤 Testing user management...")
    try:
        # Get a non-admin user to test with
        users_response = session.get(f"{BASE_URL}/admin/api/users")
        if users_response.status_code == 200:
            users_data = users_response.json()
            users = users_data.get('users', [])
            
            # Find a non-admin user
            test_user = next((u for u in users if u.get('user_type') != 'admin'), None)
            
            if test_user:
                user_id = test_user.get('id')
                print(f"   Testing with user: {test_user.get('username')} (ID: {user_id})")
                
                # Test toggle active status
                toggle_response = session.post(f"{BASE_URL}/admin/api/users/{user_id}/toggle_active")
                if toggle_response.status_code == 200:
                    print("   ✅ Toggle user active status working")
                else:
                    print(f"   ❌ Toggle user active status failed: {toggle_response.status_code}")
                    issues_found.append("Toggle user active status failed")
            else:
                print("   ⚠️  No non-admin users found for testing")
        else:
            print("   ❌ Could not fetch users for testing")
            issues_found.append("Could not fetch users for testing")
    except Exception as e:
        print(f"❌ User management test error: {e}")
        issues_found.append("User management test error")
    
    # Summary
    print("\n" + "=" * 50)
    if not issues_found:
        print("🎉 All master admin tests passed!")
        print("\n📋 Master Admin Status:")
        print("   ✅ Master admin login working")
        print("   ✅ Admin stats API working")
        print("   ✅ Get all users API working")
        print("   ✅ Get all workshops API working")
        print("   ✅ Get all jobs API working")
        print("   ✅ Admin dashboard frontend accessible")
        print("   ✅ User management working")
        print("\n🚀 Master admin system is fully functional!")
        print("\n🔐 Master Admin Credentials:")
        print("   Username: master_admin")
        print("   Password: MasterAdmin2024!")
        print("   Access: http://localhost:8000/admin")
    else:
        print(f"❌ Found {len(issues_found)} issues:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        print("\n🔧 These issues need to be fixed.")
    
    return issues_found

if __name__ == "__main__":
    issues = test_master_admin()
    if issues:
        print(f"\n💥 Test completed with {len(issues)} issues found.")
    else:
        print("\n✅ Test completed successfully - no issues found!")
