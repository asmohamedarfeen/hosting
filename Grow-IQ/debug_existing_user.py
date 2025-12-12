#!/usr/bin/env python3
"""
Debug script to identify why existing user login fails
"""
import requests
import json

def debug_existing_user_login():
    """Debug existing user login issues"""
    base_url = "http://localhost:8000"
    
    print("🔍 Debugging Existing User Login Issues...")
    print("=" * 60)
    
    # Test 1: Check what users exist in database
    print("\n1️⃣ Checking existing users...")
    try:
        # Try to get user profile (this might show us the user structure)
        response = requests.get(f"{base_url}/auth/profile")
        print(f"Profile endpoint status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Profile endpoint properly requires authentication")
        else:
            print(f"❌ Unexpected profile response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Profile check failed: {e}")
    
    # Test 2: Try login with different existing users
    print("\n2️⃣ Testing login with different existing users...")
    
    test_users = [
        {"identifier": "MURUGANANDAM", "password": "test123"},
        {"identifier": "muruga004kvp@gmail.com", "password": "test123"},
        {"identifier": "admin", "password": "admin123"},
        {"identifier": "user", "password": "password123"}
    ]
    
    for i, user_data in enumerate(test_users, 1):
        print(f"\n   Testing user {i}: {user_data['identifier']}")
        try:
            response = requests.post(f"{base_url}/auth/login", data=user_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Login successful!")
                break
            elif response.status_code == 401:
                print("   ✅ Login properly rejected (wrong password)")
            elif response.status_code == 500:
                print("   ❌ Server error - this is the problem!")
                print(f"   Response: {response.text[:200]}...")
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    # Test 3: Check server logs
    print("\n3️⃣ Server Log Analysis:")
    print("   The 500 error suggests a server-side exception.")
    print("   Check your terminal where you ran 'python start.py'")
    print("   Look for error messages or tracebacks.")
    
    # Test 4: Try to identify the specific issue
    print("\n4️⃣ Potential Issues:")
    print("   - Existing users might have corrupted data")
    print("   - Password hash format might be incompatible")
    print("   - User model fields might be missing")
    print("   - Database schema mismatch")
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("1. Check your server terminal for error messages")
    print("2. Look for Python tracebacks or exceptions")
    print("3. The issue is likely in the User model or database")
    print("4. We may need to reset the database or fix user data")

if __name__ == "__main__":
    print("Starting Existing User Login Debug...")
    print("Make sure your app is running on port 8000!")
    print()
    
    input("Press Enter when your app is running, or Ctrl+C to cancel...")
    debug_existing_user_login()
