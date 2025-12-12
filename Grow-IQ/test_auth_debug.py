#!/usr/bin/env python3
"""
Debug authentication flow to understand why streak endpoints return HTML instead of JSON
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """Test the complete authentication flow"""
    print("🔍 Debugging Authentication Flow")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Try to access home page without authentication
    print("1️⃣ Testing home page without authentication...")
    try:
        response = session.get(f"{BASE_URL}/home")
        print(f"   Status: {response.status_code}")
        if response.status_code == 303:
            print("   ✅ Correctly redirected to login (expected)")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 2: Try to access login page
    print("\n2️⃣ Testing login page access...")
    try:
        response = session.get(f"{BASE_URL}/auth/login")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Login page accessible")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 3: Try to log in with test credentials
    print("\n3️⃣ Testing login with credentials...")
    try:
        login_data = {
            "identifier": "testuser",
            "password": "testpass"
        }
        response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response type: {type(response.text)}")
        print(f"   Response length: {len(response.text)}")
        print(f"   Response preview: {response.text[:200]}...")
        
        # Check if we got a session token
        if "session_token" in response.text:
            print("   ✅ Session token found in response")
        else:
            print("   ❌ No session token in response")
            
        # Check cookies
        cookies = session.cookies
        print(f"   Cookies: {dict(cookies)}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 4: Try to access home page after login
    print("\n4️⃣ Testing home page after login...")
    try:
        response = session.get(f"{BASE_URL}/home")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Home page accessible after login")
            # Check for streak calendar HTML
            if "Activity Streaks" in response.text:
                print("   ✅ Streak calendar HTML found")
            else:
                print("   ❌ Streak calendar HTML not found")
                # Let's see what's actually in the response
                print(f"   Response length: {len(response.text)}")
                print(f"   Response preview: {response.text[:500]}...")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 5: Test streak endpoints after login
    print("\n5️⃣ Testing streak endpoints after login...")
    try:
        response = session.get(f"{BASE_URL}/streaks/get-streak-stats")
        print(f"   GET /streaks/get-streak-stats - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response type: {type(response.text)}")
            print(f"   Response length: {len(response.text)}")
            print(f"   Response preview: {response.text[:200]}...")
            
            # Check if it's JSON or HTML
            if response.text.strip().startswith('{'):
                print("   ✅ JSON response received")
            elif response.text.strip().startswith('<'):
                print("   ❌ HTML response received (expected JSON)")
            else:
                print(f"   ❓ Unknown response format: {response.text[:50]}...")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Debug Summary:")
    print("   - Check if login is creating session tokens")
    print("   - Check if cookies are being set correctly")
    print("   - Check if home page contains streak calendar HTML")
    print("   - Check if streak endpoints return JSON or HTML")

if __name__ == "__main__":
    test_auth_flow()
