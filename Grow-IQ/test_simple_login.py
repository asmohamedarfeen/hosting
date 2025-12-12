#!/usr/bin/env python3
"""
Simple login test
"""
import requests

# Base URL
BASE_URL = "http://localhost:8000"

def test_simple_login():
    """Test simple login"""
    print("🔧 Simple Login Test")
    print("=" * 30)
    
    # Test master admin login
    print("1. Testing master admin login...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "identifier": "master_admin",
            "password": "MasterAdmin2024!"
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Login successful")
                print(f"User ID: {data.get('user_id')}")
                print(f"Session Token: {data.get('session_token')[:20]}...")
            except:
                print("❌ Response is not JSON")
        else:
            print(f"❌ Login failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n2. Testing regular user login...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "identifier": "testuser_api",
            "password": "testpass123"
        })
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Login successful")
                print(f"User ID: {data.get('user_id')}")
            except:
                print("❌ Response is not JSON")
        else:
            print(f"❌ Login failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_login()
