#!/usr/bin/env python3
"""
Test script to verify login flow and redirect
"""
import requests

def test_login_flow():
    """Test the complete login flow"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Login Flow...")
    print("=" * 50)
    
    # Test 1: Check if app is running
    print("\n1️⃣ Checking if app is running...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ App is running")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to app: {e}")
        return
    
    # Test 2: Try to login with test credentials
    print("\n2️⃣ Testing login with test credentials...")
    login_data = {
        "identifier": "test@qrowiq.com",
        "password": "TestPass123!"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
        print(f"Login response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            print(f"Response content: {response.text[:200]}...")
            
            # Check if it's JSON
            try:
                data = response.json()
                print(f"JSON response: {data}")
                if 'redirect_url' in data:
                    print(f"✅ Redirect URL found: {data['redirect_url']}")
                else:
                    print("⚠️  No redirect URL in response")
            except:
                print("⚠️  Response is not JSON")
                
        elif response.status_code == 303:
            print("✅ Login redirects (as expected)")
            print(f"Redirect location: {response.headers.get('location')}")
        else:
            print(f"❌ Unexpected login response: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
    
    # Test 3: Try to access home page directly
    print("\n3️⃣ Testing direct access to home page...")
    try:
        response = requests.get(f"{base_url}/home", allow_redirects=False)
        print(f"Home page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Home page accessible")
        elif response.status_code == 303:
            print("✅ Home page redirects (requires login)")
            print(f"Redirect location: {response.headers.get('location')}")
        elif response.status_code == 401:
            print("✅ Home page requires authentication")
        else:
            print(f"❌ Unexpected home page response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Home page test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Analysis:")
    print("If login returns 200 with JSON containing redirect_url, the flow should work.")
    print("If home page returns 303 to /auth/login, authentication is working.")
    print("\n🔧 Next Steps:")
    print("1. Try logging in through the browser")
    print("2. Check browser console for any JavaScript errors")
    print("3. Verify the redirect happens after successful login")

if __name__ == "__main__":
    print("Starting Login Flow Test...")
    print("Make sure your app is running on port 8000!")
    print()
    
    input("Press Enter when your app is running, or Ctrl+C to cancel...")
    test_login_flow()
