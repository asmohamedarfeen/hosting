#!/usr/bin/env python3
"""
Simple test for streak routes without dependencies
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_simple_streak():
    """Test the simple streak endpoint"""
    print("🧪 Testing Simple Streak Endpoint")
    print("=" * 50)
    
    # Wait for app to start
    print("⏳ Waiting for application to start...")
    time.sleep(3)
    
    # Test the simple endpoint
    print("\n1️⃣ Testing GET /streaks/...")
    try:
        response = requests.get(f"{BASE_URL}/streaks/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Streak endpoint is working!")
        elif response.status_code == 401:
            print("   ✅ Streak endpoint is working but requires authentication")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test other endpoints
    print("\n2️⃣ Testing GET /streaks/get-streak-stats...")
    try:
        response = requests.get(f"{BASE_URL}/streaks/get-streak-stats")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Endpoint working, requires authentication")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Simple Streak Route Test")
    test_simple_streak()
