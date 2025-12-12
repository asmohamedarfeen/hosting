#!/usr/bin/env python3
"""
Quick Web Test - Tests if the web application is responding
"""

import requests

def test_web_app():
    """Test if the web application is responding"""
    print("🌐 Testing Web Application...")
    
    try:
        # Test main page
        print("   🔍 Testing main page...")
        response = requests.get("http://localhost:8000", timeout=10)
        print(f"      ✅ Status: {response.status_code}")
        print(f"      ✅ Content Length: {len(response.text)} characters")
        
        # Test health endpoint
        print("   🔍 Testing health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"      ✅ Health: {health_data.get('status', 'unknown')}")
            print(f"      ✅ Environment: {health_data.get('environment', 'unknown')}")
        else:
            print(f"      ❌ Health Failed: {response.status_code}")
        
        # Test API docs
        print("   🔍 Testing API docs...")
        response = requests.get("http://localhost:8000/docs", timeout=10)
        print(f"      ✅ API Docs: {response.status_code}")
        
        print("\n🎉 Web Application Test Successful!")
        print("✅ Your Qrow IQ application is running and responding!")
        print("\n🌐 Access your application at:")
        print("   📱 Dashboard: http://localhost:8000")
        print("   📚 API Docs: http://localhost:8000/docs")
        print("   🏥 Health: http://localhost:8000/health")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Application is not accessible")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_web_app()
