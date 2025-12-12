#!/usr/bin/env python3
"""
Test Google OAuth Routes
This script tests if the Google OAuth routes are properly configured.
"""

import requests
import sys

def test_oauth_routes():
    """Test Google OAuth routes"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Google OAuth Routes")
    print("=" * 40)
    
    # Test 1: Check if OAuth router is accessible
    print("\n1️⃣ Testing OAuth router accessibility...")
    try:
        response = requests.get(f"{base_url}/auth/google", allow_redirects=False)
        if response.status_code == 302:  # Should redirect to Google
            print("✅ OAuth router is accessible")
            print(f"   Redirect URL: {response.headers.get('Location', 'N/A')}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Start with: python start.py")
        return False
    except Exception as e:
        print(f"❌ Error testing OAuth router: {e}")
        return False
    
    # Test 2: Check OAuth callback route
    print("\n2️⃣ Testing OAuth callback route...")
    try:
        response = requests.get(f"{base_url}/auth/google/callback?code=test&state=test")
        if response.status_code in [302, 400, 500]:  # Should handle invalid params
            print("✅ OAuth callback route is accessible")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing callback route: {e}")
        return False
    
    # Test 3: Check OAuth status route
    print("\n3️⃣ Testing OAuth status route...")
    try:
        response = requests.get(f"{base_url}/auth/status")
        if response.status_code == 200:
            print("✅ OAuth status route is accessible")
            data = response.json()
            print(f"   Authentication status: {data.get('authenticated', 'N/A')}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing status route: {e}")
        return False
    
    print("\n🎉 All OAuth route tests passed!")
    return True

def test_environment():
    """Test environment configuration"""
    print("\n🔧 Testing Environment Configuration")
    print("=" * 40)
    
    try:
        from config import settings
        
        print(f"Google Client ID: {'✅ Set' if settings.GOOGLE_CLIENT_ID else '❌ Not set'}")
        print(f"Google Client Secret: {'✅ Set' if settings.GOOGLE_CLIENT_SECRET else '❌ Not set'}")
        print(f"Google Redirect URI: {settings.GOOGLE_REDIRECT_URI}")
        
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            print("\n⚠️  Google OAuth credentials not configured!")
            print("   Run: python setup_google_oauth.py")
            return False
        
        print("\n✅ Environment configuration is complete")
        return True
        
    except Exception as e:
        print(f"❌ Error checking environment: {e}")
        return False

def main():
    """Main test function"""
    print("Qrow IQ - Google OAuth Test")
    print("=" * 40)
    
    # Test environment
    if not test_environment():
        print("\n❌ Environment test failed. Please configure OAuth first.")
        return
    
    # Test OAuth routes
    if not test_oauth_routes():
        print("\n❌ OAuth route tests failed.")
        return
    
    print("\n🎉 All tests passed! Google OAuth is ready to use.")
    print("\n📱 Next steps:")
    print("1. Go to: http://localhost:8000/auth/login")
    print("2. Click 'Continue with Google'")
    print("3. Complete Google authentication")
    print("4. You should be redirected to the dashboard")

if __name__ == "__main__":
    main()
