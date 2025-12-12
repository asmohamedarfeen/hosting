#!/usr/bin/env python3
"""
Comprehensive test to identify any issues in the mock interview system
"""
import requests
import json
import time

# Base URL
BASE_URL = "http://localhost:8000"

def test_complete_system():
    """Test the complete mock interview system to identify any issues"""
    print("🔍 Comprehensive Mock Interview System Test")
    print("=" * 60)
    
    issues_found = []
    
    # Step 1: Test Server Health
    print("1. 🏥 Testing server health...")
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ Server is healthy")
        else:
            print(f"❌ Server health check failed: {health_response.status_code}")
            issues_found.append("Server health check failed")
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        issues_found.append("Server not responding")
        return issues_found
    
    # Step 2: Test Authentication
    print("\n2. 🔐 Testing authentication...")
    session = requests.Session()
    
    try:
        login_data = {
            "identifier": "testuser_api",
            "password": "password123"
        }
        login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Login successful")
            login_data = login_response.json()
            print(f"   User ID: {login_data.get('user_id')}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            issues_found.append("Login failed")
    except Exception as e:
        print(f"❌ Login error: {e}")
        issues_found.append("Login error")
    
    # Step 3: Test Profile Access
    print("\n3. 👤 Testing profile access...")
    try:
        profile_response = session.get(f"{BASE_URL}/auth/profile")
        if profile_response.status_code == 200:
            print("✅ Profile access successful")
            user_data = profile_response.json()
            print(f"   Username: {user_data.get('username')}")
        else:
            print(f"❌ Profile access failed: {profile_response.status_code}")
            issues_found.append("Profile access failed")
    except Exception as e:
        print(f"❌ Profile access error: {e}")
        issues_found.append("Profile access error")
    
    # Step 4: Test Interview Session Creation
    print("\n4. 🎯 Testing interview session creation...")
    try:
        interview_data = {
            "job_role": "Software Engineer",
            "job_desc": "Test interview for software engineering position"
        }
        start_response = session.post(
            f"{BASE_URL}/mock-interview/video/start",
            json=interview_data,
            headers={"Content-Type": "application/json"}
        )
        
        if start_response.status_code == 200:
            print("✅ Interview session created successfully")
            session_data = start_response.json()
            session_id = session_data.get("session_id")
            print(f"   Session ID: {session_id}")
        else:
            print(f"❌ Interview session creation failed: {start_response.status_code}")
            print(f"   Response: {start_response.text}")
            issues_found.append("Interview session creation failed")
            return issues_found
    except Exception as e:
        print(f"❌ Interview session creation error: {e}")
        issues_found.append("Interview session creation error")
        return issues_found
    
    # Step 5: Test Message Sending
    print("\n5. 📤 Testing message sending...")
    try:
        message_data = {
            "message": "Hello, I am a software engineer with 5 years of experience",
            "session_id": session_id
        }
        message_response = session.post(
            f"{BASE_URL}/mock-interview/video/message",
            json=message_data,
            headers={"Content-Type": "application/json"}
        )
        
        if message_response.status_code == 200:
            print("✅ Message sent successfully")
            response_data = message_response.json()
            ai_reply = response_data.get("reply", "")
            print(f"   AI Response: {ai_reply[:100]}...")
        else:
            print(f"❌ Message sending failed: {message_response.status_code}")
            print(f"   Response: {message_response.text}")
            issues_found.append("Message sending failed")
    except Exception as e:
        print(f"❌ Message sending error: {e}")
        issues_found.append("Message sending error")
    
    # Step 6: Test Multiple Messages
    print("\n6. 🔄 Testing multiple messages...")
    test_messages = [
        "I have experience with Python, JavaScript, and React",
        "I enjoy solving complex problems and working in teams",
        "I have worked on both frontend and backend development"
    ]
    
    for i, message in enumerate(test_messages, 1):
        try:
            message_data = {
                "message": message,
                "session_id": session_id
            }
            print(f"   📤 Sending message {i}: {message[:50]}...")
            message_response = session.post(
                f"{BASE_URL}/mock-interview/video/message",
                json=message_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   📡 Response status: {message_response.status_code}")
            if message_response.status_code == 200:
                print(f"   ✅ Message {i} sent successfully")
                response_data = message_response.json()
                ai_reply = response_data.get("reply", "")
                print(f"   🤖 AI Response: {ai_reply[:100]}...")
            else:
                print(f"   ❌ Message {i} failed: {message_response.status_code}")
                print(f"   📄 Response: {message_response.text}")
                issues_found.append(f"Message {i} sending failed")
        except Exception as e:
            print(f"   ❌ Message {i} error: {e}")
            issues_found.append(f"Message {i} sending error")
        
        time.sleep(1)  # Longer delay between messages
    
    # Step 7: Test Frontend Access
    print("\n7. 🌐 Testing frontend access...")
    try:
        frontend_response = session.get(f"{BASE_URL}/mock-interview")
        if frontend_response.status_code == 200:
            print("✅ Frontend is accessible")
            if "index.html" in frontend_response.text or "root" in frontend_response.text:
                print("✅ Frontend is serving React app")
            else:
                print("⚠️  Frontend might not be serving React app correctly")
                issues_found.append("Frontend React app issue")
        else:
            print(f"❌ Frontend access failed: {frontend_response.status_code}")
            issues_found.append("Frontend access failed")
    except Exception as e:
        print(f"❌ Frontend access error: {e}")
        issues_found.append("Frontend access error")
    
    # Summary
    print("\n" + "=" * 60)
    if not issues_found:
        print("🎉 All tests passed! The mock interview system is working correctly.")
        print("\n📋 System Status:")
        print("   ✅ Server is running and healthy")
        print("   ✅ Authentication is working")
        print("   ✅ Profile access is working")
        print("   ✅ Interview session creation is working")
        print("   ✅ Message sending is working")
        print("   ✅ Multiple messages are working")
        print("   ✅ Frontend is accessible")
        print("\n🚀 The system is ready for use!")
    else:
        print(f"❌ Found {len(issues_found)} issues:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        print("\n🔧 These issues need to be fixed.")
    
    return issues_found

if __name__ == "__main__":
    issues = test_complete_system()
    if issues:
        print(f"\n💥 Test completed with {len(issues)} issues found.")
    else:
        print("\n✅ Test completed successfully - no issues found!")
