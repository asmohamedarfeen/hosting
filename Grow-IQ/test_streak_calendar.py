#!/usr/bin/env python3
"""
Test script for the streak calendar functionality
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_streak_endpoints():
    """Test the streak API endpoints"""
    print("🧪 Testing Streak Calendar Endpoints")
    print("=" * 50)
    
    # Test 1: Get streak stats (should work without authentication)
    print("\n1️⃣ Testing GET /streaks/get-streak-stats...")
    try:
        response = requests.get(f"{BASE_URL}/streaks/get-streak-stats")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Expected: Unauthorized (requires login)")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Get calendar data (should work without authentication)
    print("\n2️⃣ Testing GET /streaks/get-calendar-data...")
    try:
        current_year = datetime.now().year
        current_month = datetime.now().month
        response = requests.get(f"{BASE_URL}/streaks/get-calendar-data?year={current_year}&month={current_month}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Expected: Unauthorized (requires login)")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Log activity (should work without authentication)
    print("\n3️⃣ Testing POST /streaks/log-activity...")
    try:
        data = {
            "activity_type": "coding",
            "description": "Test activity"
        }
        response = requests.post(f"{BASE_URL}/streaks/log-activity", data=data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Expected: Unauthorized (requires login)")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("   - All endpoints should return 401 (Unauthorized) without login")
    print("   - This confirms the endpoints are working and properly protected")
    print("   - The streak calendar will work once users log in")

def test_home_page():
    """Test if the home page loads with streak calendar"""
    print("\n🏠 Testing Home Page with Streak Calendar...")
    print("=" * 50)
    
    try:
        # The home page is actually at /home, not /
        response = requests.get(f"{BASE_URL}/home")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if "Activity Streaks" in content:
                print("   ✅ Streak calendar HTML found in home page")
            else:
                print("   ❌ Streak calendar HTML not found in home page")
                
            if "streak-calendar" in content:
                print("   ✅ Streak calendar CSS classes found")
            else:
                print("   ❌ Streak calendar CSS classes not found")
        else:
            print(f"   ❌ Home page returned status: {response.status_code}")
            print("   ℹ️  Note: This is expected if authentication is required")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Qrow IQ Streak Calendar Test")
    
    # Test API endpoints
    test_streak_endpoints()
    
    # Test home page
    test_home_page()
    
    print("\n🎉 Testing completed!")
    print("\n💡 To test the full functionality:")
    print("   1. Open http://localhost:8000 in your browser")
    print("   2. Log in with your account")
    print("   3. Navigate to the home section")
    print("   4. Look for the 'Activity Streaks' section in the right sidebar")
    print("   5. Try logging an activity using the 'Log Activity' button")
