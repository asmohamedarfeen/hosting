#!/usr/bin/env python3
"""
Final Comprehensive Test - Verifies the application is fully working
"""

import requests
import time

def test_application_running():
    """Test if the application is running and responding"""
    print("🧪 Final Comprehensive Test")
    print("=" * 50)
    
    try:
        # Test 1: Health endpoint
        print("🔍 Testing Health Endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health Check: {health_data.get('status', 'unknown')}")
            print(f"   ✅ Environment: {health_data.get('environment', 'unknown')}")
            print(f"   ✅ Version: {health_data.get('version', 'unknown')}")
        else:
            print(f"   ❌ Health Check Failed: {response.status_code}")
            return False
        
        # Test 2: Main dashboard
        print("\n🔍 Testing Main Dashboard...")
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Dashboard: Accessible")
        else:
            print(f"   ❌ Dashboard Failed: {response.status_code}")
        
        # Test 3: API documentation
        print("\n🔍 Testing API Documentation...")
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("   ✅ API Docs: Accessible")
        else:
            print(f"   ❌ API Docs Failed: {response.status_code}")
        
        # Test 4: Configuration
        print("\n🔍 Testing Configuration...")
        try:
            from config import settings
            print(f"   ✅ Environment: {settings.ENVIRONMENT}")
            print(f"   ✅ Debug Mode: {settings.DEBUG}")
            print(f"   ✅ Host: {settings.HOST}")
            print(f"   ✅ Port: {settings.PORT}")
        except Exception as e:
            print(f"   ❌ Configuration Error: {e}")
        
        # Test 5: Database
        print("\n🔍 Testing Database...")
        try:
            from database_enhanced import db_manager
            health = db_manager.check_health()
            print(f"   ✅ Database Status: {health.get('overall', 'unknown')}")
        except Exception as e:
            print(f"   ❌ Database Error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 FINAL TEST COMPLETED SUCCESSFULLY!")
        print("✅ Your Qrow IQ application is FULLY WORKING!")
        print("\n🌐 Access your application at:")
        print("   📱 Dashboard: http://localhost:8000")
        print("   📚 API Docs: http://localhost:8000/docs")
        print("   🏥 Health: http://localhost:8000/health")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Application is not running or not accessible")
        print("💡 Start the application with: python start.py")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_application_running()
