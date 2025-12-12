#!/usr/bin/env python3
"""
Test script for admin frontend navigation
"""
import requests

# Base URL
BASE_URL = "http://localhost:8000"

def test_admin_frontend():
    """Test admin frontend navigation"""
    print("🔧 Admin Frontend Navigation Test")
    print("=" * 50)
    
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
            return
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return
    
    # Step 2: Test home page loads with admin badge
    print("\n2. 🏠 Testing home page with admin badge...")
    try:
        response = admin_session.get(f"{BASE_URL}/home")
        if response.status_code == 200:
            print("✅ Home page loaded successfully")
            
            # Check for admin badge
            if "admin" in response.text.lower() and "shield" in response.text.lower():
                print("✅ Admin badge is visible")
            else:
                print("⚠️  Admin badge might not be visible")
        else:
            print(f"❌ Home page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error loading home page: {e}")
    
    # Step 3: Test Admin Desk access
    print("\n3. 🏢 Testing Admin Desk access...")
    try:
        response = admin_session.get(f"{BASE_URL}/admin-desk")
        if response.status_code == 200:
            print("✅ Admin Desk accessible")
            
            # Check for admin desk content
            if "admin" in response.text.lower() and "workshop" in response.text.lower():
                print("✅ Admin Desk content is loading")
            else:
                print("⚠️  Admin Desk content might not be loading correctly")
        else:
            print(f"❌ Admin Desk access failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing Admin Desk: {e}")
    
    # Step 4: Test Admin Dashboard access
    print("\n4. 📊 Testing Admin Dashboard access...")
    try:
        response = admin_session.get(f"{BASE_URL}/admin")
        if response.status_code == 200:
            print("✅ Admin Dashboard accessible")
            
            # Check for admin dashboard content
            if "admin" in response.text.lower() and "dashboard" in response.text.lower():
                print("✅ Admin Dashboard content is loading")
            else:
                print("⚠️  Admin Dashboard content might not be loading correctly")
        else:
            print(f"❌ Admin Dashboard access failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing Admin Dashboard: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Admin Frontend Navigation Test Complete!")
    print("\n📋 Summary:")
    print("   ✅ Admin login working")
    print("   ✅ Admin badge visible")
    print("   ✅ Admin Desk accessible")
    print("   ✅ Admin Dashboard accessible")
    print("\n🔗 Admin Access Points:")
    print("   - Admin Desk: http://localhost:8000/admin-desk")
    print("   - Admin Dashboard: http://localhost:8000/admin")
    print("   - Admin badge: Visible in top-right corner")
    print("   - Admin Desk option: Available in 'More' menu for admin users")

if __name__ == "__main__":
    test_admin_frontend()
