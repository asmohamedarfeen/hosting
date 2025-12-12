#!/usr/bin/env python3
"""
Test script to simulate the frontend flow for mock interview
"""
import requests
import json
import time

# Base URL
BASE_URL = "http://localhost:8000"

def test_mock_interview_flow():
    """Test the complete mock interview flow"""
    print("🧪 Testing Mock Interview Flow")
    print("=" * 50)
    
    # Step 1: Login
    print("1. 🔐 Logging in...")
    login_data = {
        "identifier": "testuser_api",
        "password": "password123"
    }
    
    session = requests.Session()
    login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code == 200:
        print("✅ Login successful")
        login_data = login_response.json()
        print(f"   User ID: {login_data.get('user_id')}")
        print(f"   Session Token: {login_data.get('session_token', 'N/A')[:20]}...")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        return False
    
    # Step 2: Start Interview Session
    print("\n2. 🎯 Starting interview session...")
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
        print("✅ Interview session started")
        session_data = start_response.json()
        session_id = session_data.get("session_id")
        initial_prompt = session_data.get("initial_prompt")
        print(f"   Session ID: {session_id}")
        print(f"   Initial Prompt: {initial_prompt[:100]}...")
    else:
        print(f"❌ Failed to start interview: {start_response.status_code}")
        print(f"   Response: {start_response.text}")
        return False
    
    # Step 3: Send Messages (Simulate Speech Recognition)
    print("\n3. 🎤 Testing message sending (simulating speech recognition)...")
    
    test_messages = [
        "Hello, I am a software engineer with 5 years of experience in Python and JavaScript",
        "A stack is a LIFO data structure where elements are added and removed from the top, while a queue is a FIFO data structure where elements are added at the rear and removed from the front",
        "I have experience with React, Node.js, and PostgreSQL",
        "I enjoy solving complex problems and working in agile teams"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   📤 Sending message {i}: {message[:50]}...")
        
        message_data = {
            "message": message,
            "session_id": session_id
        }
        
        message_response = session.post(
            f"{BASE_URL}/mock-interview/video/message",
            json=message_data,
            headers={"Content-Type": "application/json"}
        )
        
        if message_response.status_code == 200:
            print("   ✅ Message sent successfully")
            response_data = message_response.json()
            ai_reply = response_data.get("reply", "")
            print(f"   🤖 AI Response: {ai_reply[:100]}...")
        else:
            print(f"   ❌ Failed to send message: {message_response.status_code}")
            print(f"   Response: {message_response.text}")
            return False
        
        # Small delay between messages
        time.sleep(1)
    
    print("\n4. ✅ All tests passed!")
    print("   The mock interview API is working correctly.")
    print("   The issue might be in the frontend implementation.")
    
    return True

if __name__ == "__main__":
    success = test_mock_interview_flow()
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
