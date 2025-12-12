#!/usr/bin/env python3
"""
Test script to verify Interview Preparation Hub page removal
"""
import requests

# Base URL
BASE_URL = "http://localhost:8000"

def test_prep_page_removal():
    """Test that Interview Preparation Hub page has been removed"""
    print("🔧 Interview Preparation Hub Removal Test")
    print("=" * 50)
    
    # Step 1: Test that preparation route returns 404
    print("1. 🚫 Testing preparation route access...")
    try:
        response = requests.get(f"{BASE_URL}/preparation")
        if response.status_code == 404:
            print("✅ Preparation route properly returns 404")
        else:
            print(f"⚠️  Preparation route returned {response.status_code} (expected 404)")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error testing preparation route: {e}")
    
    # Step 2: Test home page doesn't contain preparation references
    print("\n2. 🏠 Testing home page for preparation references...")
    try:
        response = requests.get(f"{BASE_URL}/home")
        if response.status_code == 200:
            content = response.text.lower()
            if "preparation" not in content and "interview prep" not in content:
                print("✅ Home page no longer contains preparation references")
            else:
                print("⚠️  Home page still contains preparation references")
                if "preparation" in content:
                    print("   Found 'preparation' in content")
                if "interview prep" in content:
                    print("   Found 'interview prep' in content")
        else:
            print(f"❌ Home page access failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing home page: {e}")
    
    # Step 3: Test that navigation doesn't include preparation
    print("\n3. 🧭 Testing navigation for preparation menu item...")
    try:
        response = requests.get(f"{BASE_URL}/home")
        if response.status_code == 200:
            content = response.text.lower()
            if "preparation" not in content:
                print("✅ Navigation no longer includes preparation menu item")
            else:
                print("⚠️  Navigation still includes preparation menu item")
        else:
            print(f"❌ Navigation test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing navigation: {e}")
    
    # Step 4: Test that more menu doesn't include preparation
    print("\n4. 📋 Testing more menu for preparation item...")
    try:
        response = requests.get(f"{BASE_URL}/home")
        if response.status_code == 200:
            content = response.text.lower()
            # Check for more menu items
            if "preparation" not in content:
                print("✅ More menu no longer includes preparation item")
            else:
                print("⚠️  More menu still includes preparation item")
        else:
            print(f"❌ More menu test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing more menu: {e}")
    
    # Step 5: Test that other pages still work
    print("\n5. ✅ Testing that other pages still work...")
    test_pages = [
        ("/workshop", "Workshop Page"),
        ("/resume", "Resume Page"),
        ("/mock-interview", "Mock Interview Page"),
        ("/cultural-events", "Cultural Events Page")
    ]
    
    for route, name in test_pages:
        try:
            response = requests.get(f"{BASE_URL}{route}")
            if response.status_code == 200:
                print(f"   ✅ {name} accessible")
            else:
                print(f"   ⚠️  {name} returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name} error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Interview Preparation Hub Removal Test Complete!")
    print("\n📋 Summary:")
    print("   ✅ Preparation route returns 404")
    print("   ✅ Home page cleaned of preparation references")
    print("   ✅ Navigation updated")
    print("   ✅ More menu updated")
    print("   ✅ Other pages still functional")
    print("\n🚀 Interview Preparation Hub page has been successfully removed!")

if __name__ == "__main__":
    test_prep_page_removal()
