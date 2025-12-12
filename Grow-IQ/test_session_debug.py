#!/usr/bin/env python3
"""
Debug session storage issues
"""

import requests
import time

def test_session_debug():
    base_url = "http://localhost:8000"
    
    print("🔍 Debugging session storage...")
    
    # Test data
    test_user = {
        'username': 'debuguser888',
        'email': 'debuguser888@example.com',
        'full_name': 'Debug User 888',
        'company': 'Debug Company',
        'password': 'DebugPassword888!',
        'confirm_password': 'DebugPassword888!'
    }
    
    try:
        # Step 1: Signup
        print("\n1️⃣ Signing up user...")
        response = requests.post(f"{base_url}/auth/signup", data=test_user)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            session_token = data.get('session_token')
            user_id = data.get('user_id')
            print(f"   ✅ Signup successful")
            print(f"   Session token: {session_token[:30]}..." if session_token else "No token")
            print(f"   User ID: {user_id}")
            
            # Step 2: Wait a moment
            print("\n2️⃣ Waiting 1 second...")
            time.sleep(1)
            
            # Step 3: Try to access a very simple endpoint
            print("\n3️⃣ Testing simple endpoint...")
            cookies = {'session_token': session_token}
            
            # Try to access the root endpoint (should redirect to login if not authenticated)
            response = requests.get(f"{base_url}/", cookies=cookies, allow_redirects=False)
            print(f"   Root status: {response.status_code}")
            
            if response.status_code == 303:
                redirect_url = response.headers.get('location')
                print(f"   ⚠️ Root redirected to: {redirect_url}")
            elif response.status_code == 200:
                print(f"   ✅ Root accessible!")
            else:
                print(f"   ❌ Root error: {response.status_code}")
            
            # Step 4: Try to access login page (should work)
            print("\n4️⃣ Testing login page access...")
            response = requests.get(f"{base_url}/auth/login", cookies=cookies, allow_redirects=False)
            print(f"   Login page status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Login page accessible!")
            else:
                print(f"   ❌ Login page error: {response.status_code}")
            
            # Step 5: Try to access signup page (should work)
            print("\n5️⃣ Testing signup page access...")
            response = requests.get(f"{base_url}/auth/signup", cookies=cookies, allow_redirects=False)
            print(f"   Signup page status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Signup page accessible!")
            else:
                print(f"   ❌ Signup page error: {response.status_code}")
            
            # Step 6: Try to access home page again
            print("\n6️⃣ Testing home page again...")
            response = requests.get(f"{base_url}/home", cookies=cookies, allow_redirects=False)
            print(f"   Home status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Home page accessible!")
            elif response.status_code == 303:
                redirect_url = response.headers.get('location')
                print(f"   ⚠️ Home page redirected to: {redirect_url}")
            else:
                print(f"   ❌ Home page error: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
            
        else:
            print(f"   ❌ Signup failed: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_session_debug()
