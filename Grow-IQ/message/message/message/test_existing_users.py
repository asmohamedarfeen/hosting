#!/usr/bin/env python3
"""
Test script for existing users in the LinkedIn-like Connection + Messaging App.
Demonstrates login, connections, and messaging functionality.
"""

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

def test_user_login():
    """Test user login and get tokens."""
    print("🔐 Testing User Login...")
    
    # Login first user (Alice)
    user1_data = {
        "email": "alice@example.com",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/users/login", json=user1_data)
    if response.status_code == 200:
        user1_token = response.json()["access_token"]
        print("✅ Alice logged in successfully")
    else:
        print(f"❌ Failed to login Alice: {response.text}")
        return None, None
    
    # Login second user (Bob)
    user2_data = {
        "email": "bob@example.com",
        "password": "securepassword456"
    }
    
    response = requests.post(f"{BASE_URL}/users/login", json=user2_data)
    if response.status_code == 200:
        user2_token = response.json()["access_token"]
        print("✅ Bob logged in successfully")
    else:
        print(f"❌ Failed to login Bob: {response.text}")
        return None, None
    
    return user1_token, user2_token

def test_user_listing(token):
    """Test listing users."""
    print("\n👥 Testing User Listing...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/", headers=headers)
    
    if response.status_code == 200:
        users = response.json()
        print(f"✅ Found {users['total']} users")
        for user in users['users']:
            print(f"   - {user['name']} (@{user['email']}) - ID: {user['id']}")
    else:
        print(f"❌ Failed to list users: {response.text}")

def test_connection_request(token, receiver_id):
    """Test sending a connection request."""
    print(f"\n🤝 Testing Connection Request to user {receiver_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {"receiver_id": receiver_id}
    
    response = requests.post(f"{BASE_URL}/connections/", json=data, headers=headers)
    
    if response.status_code == 201:
        connection = response.json()
        print(f"✅ Connection request sent successfully (ID: {connection['id']})")
        return connection['id']
    else:
        print(f"❌ Failed to send connection request: {response.text}")
        return None

def test_connection_acceptance(token, connection_id):
    """Test accepting a connection request."""
    print(f"\n✅ Testing Connection Acceptance for connection {connection_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/connections/{connection_id}/accept", headers=headers)
    
    if response.status_code == 200:
        connection = response.json()
        print(f"✅ Connection accepted successfully (Status: {connection['status']})")
        return True
    else:
        print(f"❌ Failed to accept connection: {response.text}")
        return False

def test_connection_listing(token):
    """Test listing connections."""
    print("\n📋 Testing Connection Listing...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/connections/", headers=headers)
    
    if response.status_code == 200:
        connections = response.json()
        print(f"✅ Sent connections: {connections['total_sent']}")
        print(f"✅ Received connections: {connections['total_received']}")
        
        for conn in connections['sent_connections']:
            print(f"   - Sent to: {conn['receiver']['name']} (Status: {conn['status']})")
        
        for conn in connections['received_connections']:
            print(f"   - Received from: {conn['sender']['name']} (Status: {conn['status']})")
    else:
        print(f"❌ Failed to list connections: {response.text}")

def test_message_sending(token, receiver_id, message_content):
    """Test sending a message."""
    print(f"\n💬 Testing Message Sending to user {receiver_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "receiver_id": receiver_id,
        "content": message_content
    }
    
    response = requests.post(f"{BASE_URL}/messages/", json=data, headers=headers)
    
    if response.status_code == 201:
        message = response.json()
        print(f"✅ Message sent successfully (ID: {message['id']})")
        print(f"   Content: {message['content']}")
        return message['id']
    else:
        print(f"❌ Failed to send message: {response.text}")
        return None

def test_chat_history(token, other_user_id):
    """Test retrieving chat history."""
    print(f"\n📚 Testing Chat History with user {other_user_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/messages/chat/{other_user_id}", headers=headers)
    
    if response.status_code == 200:
        chat = response.json()
        print(f"✅ Found {chat['total']} messages in chat history")
        
        for msg in chat['messages'][:3]:  # Show first 3 messages
            sender = msg['sender']['name']
            content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
            timestamp = msg['timestamp']
            print(f"   - {sender}: {content} ({timestamp})")
    else:
        print(f"❌ Failed to get chat history: {response.text}")

def main():
    """Main test function."""
    print("🚀 LinkedIn-like Connection + Messaging App - Test Suite (Existing Users)")
    print("=" * 70)
    
    # Test user login
    user1_token, user2_token = test_user_login()
    if not user1_token or not user2_token:
        print("❌ Cannot proceed without user tokens")
        return
    
    # Test user listing
    test_user_listing(user1_token)
    
    # Test connection request (Alice sends to Bob)
    print(f"\n{'='*70}")
    print("🔗 Testing Connection Flow...")
    
    connection_id = test_connection_request(user1_token, 3)  # Alice (ID: 2) connects to Bob (ID: 3)
    if not connection_id:
        print("❌ Cannot proceed without connection")
        return
    
    # Test connection acceptance (Bob accepts Alice's request)
    if test_connection_acceptance(user2_token, connection_id):
        print("✅ Connection established successfully!")
    
    # Test connection listing for both users
    print(f"\n{'='*70}")
    print("📋 Connection Status for Both Users...")
    
    print("\n--- Alice's Connections ---")
    test_connection_listing(user1_token)
    
    print("\n--- Bob's Connections ---")
    test_connection_listing(user2_token)
    
    # Test messaging (now that they're connected)
    print(f"\n{'='*70}")
    print("💬 Testing Messaging System...")
    
    # Alice sends message to Bob
    message1_id = test_message_sending(user1_token, 3, "Hi Bob! Great to connect with you!")
    if message1_id:
        time.sleep(1)  # Small delay
        
        # Bob sends reply to Alice
        message2_id = test_message_sending(user2_token, 2, "Hi Alice! Thanks for the connection request. Looking forward to collaborating!")
        if message2_id:
            time.sleep(1)  # Small delay
            
            # Test chat history for both users
            print(f"\n{'='*70}")
            print("📚 Chat History Test...")
            
            print("\n--- Alice's Chat History with Bob ---")
            test_chat_history(user1_token, 3)
            
            print("\n--- Bob's Chat History with Alice ---")
            test_chat_history(user2_token, 2)
    
    print(f"\n{'='*70}")
    print("🎉 Test Suite Completed Successfully!")
    print("\n📖 Next Steps:")
    print("1. Visit http://localhost:8000/docs for interactive API documentation")
    print("2. Test WebSocket connections for real-time messaging")
    print("3. Explore additional endpoints and features")
    print("4. Check the database for created data")

if __name__ == "__main__":
    main()
