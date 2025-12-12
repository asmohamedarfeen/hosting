#!/usr/bin/env python3
"""
Test script for streak endpoints with authentication
"""

import requests
import json
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:8000"

def test_streak_with_auth():
    """Test streak endpoints with proper authentication"""
    print("🚀 Qrow IQ Streak Calendar Test with Authentication")
    print("🧪 Testing Streak Calendar Endpoints")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # First, try to access the home page to see if we need to log in
    print("1️⃣ Testing home page access...")
    try:
        response = session.get(f"{BASE_URL}/home")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Home page accessible - user is logged in")
            # Check if streak calendar HTML is present
            if "Activity Streaks" in response.text:
                print("   ✅ Streak calendar HTML found")
            else:
                print("   ❌ Streak calendar HTML not found")
        elif response.status_code == 303:
            print("   🔄 Redirecting to login page")
            print("   💡 User needs to log in first")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error accessing home page: {e}")
        return
    
    # Test streak endpoints
    print("\n2️⃣ Testing streak endpoints...")
    
    # Test the test endpoint first
    try:
        response = session.get(f"{BASE_URL}/streaks/")
        print(f"   GET /streaks/ - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error testing /streaks/: {e}")
    
    # Test get-streak-stats
    try:
        response = session.get(f"{BASE_URL}/streaks/get-streak-stats")
        print(f"   GET /streaks/get-streak-stats - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error testing get-streak-stats: {e}")
    
    # Test get-calendar-data
    try:
        response = session.get(f"{BASE_URL}/streaks/get-calendar-data")
        print(f"   GET /streaks/get-calendar-data - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error testing get-calendar-data: {e}")
    
    # Test log-activity
    try:
        data = {
            "activity_type": "coding",
            "description": "Test activity from script"
        }
        response = session.post(f"{BASE_URL}/streaks/log-activity", data=data)
        print(f"   POST /streaks/log-activity - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error testing log-activity: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("   - If endpoints return 401/403, user needs to log in")
    print("   - If endpoints return 200 with JSON, streak system is working")
    print("   - If endpoints return 500, there's a server error")
    
    print("\n💡 To test the full functionality:")
    print("   1. Open http://localhost:8000 in your browser")
    print("   2. Log in with your account")
    print("   3. Navigate to the home section")
    print("   4. Look for the 'Activity Streaks' section in the right sidebar")
    print("   5. Try logging an activity using the 'Log Activity' button")
    
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    test_streak_with_auth()
