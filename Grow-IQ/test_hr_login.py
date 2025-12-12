#!/usr/bin/env python3
"""
Test HR Login Functionality
===========================

This script tests the HR login system to ensure it's working properly.
"""

import requests
import json
from datetime import datetime

def test_hr_login():
    """Test HR login with various credentials"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing HR Login System...")
    print("=" * 50)
    
    # Test credentials
    test_credentials = [
        {"email": "hr@company.com", "password": "hr123456", "description": "Main HR User"},
        {"email": "hr1@microsoft.com", "password": "hr123456", "description": "Microsoft HR"},
        {"email": "hr2@google.com", "password": "hr123456", "description": "Google HR"},
        {"email": "test@careerconnect.com", "password": "hr123456", "description": "CareerConnect HR"},
    ]
    
    for cred in test_credentials:
        print(f"\n🔑 Testing: {cred['description']}")
        print(f"   Email: {cred['email']}")
        
        try:
            # Test login
            login_data = {
                "identifier": cred['email'],
                "password": cred['password']
            }
            
            response = requests.post(f"{base_url}/auth/login", data=login_data)
            
            if response.status_code == 200:
                print("   ✅ Login successful!")
                
                # Try to access HR dashboard
                try:
                    hr_response = requests.get(f"{base_url}/hr/dashboard", cookies=response.cookies)
                    
                    if hr_response.status_code == 200:
                        print("   ✅ HR Dashboard access successful!")
                    elif hr_response.status_code == 403:
                        print("   ❌ HR Dashboard access denied (403 Forbidden)")
                    else:
                        print(f"   ⚠️  HR Dashboard returned status: {hr_response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error accessing HR dashboard: {e}")
                    
            else:
                print(f"   ❌ Login failed with status: {response.status_code}")
                if response.text:
                    print(f"   Response: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"   ❌ Error during login test: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("If you see ✅ for both login and HR dashboard access, the system is working!")
    print("If you see ❌ for HR dashboard, there might still be access control issues.")
    print("\n💡 Next steps:")
    print("1. Make sure your application is running on localhost:8000")
    print("2. Check that the .hr_dev_mode file exists")
    print("3. Verify user classification in the database")

def test_hr_access_control():
    """Test HR access control without authentication"""
    base_url = "http://localhost:8000"
    
    print("\n🔒 Testing HR Access Control...")
    print("=" * 50)
    
    try:
        # Try to access HR dashboard without login
        response = requests.get(f"{base_url}/hr/dashboard")
        
        if response.status_code == 401:
            print("✅ Access control working - unauthenticated users blocked")
        elif response.status_code == 403:
            print("✅ Access control working - access denied")
        elif response.status_code == 200:
            print("⚠️  Warning: HR dashboard accessible without authentication!")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing access control: {e}")

def main():
    """Run all tests"""
    print("🚀 HR Login System Test")
    print("=" * 50)
    
    try:
        test_hr_access_control()
        test_hr_login()
        
        print("\n✅ Testing completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
