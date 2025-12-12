#!/usr/bin/env python3
"""
Session Debug Script
====================

This script helps debug and fix session management issues.
"""

import json
import os
from datetime import datetime, timedelta
from auth_utils import user_sessions, create_session_token, get_user_from_session, save_sessions_to_file
from database import get_db
from models import User

def show_session_status():
    """Show current session status"""
    print("🔍 Session Status")
    print("=" * 40)
    print(f"Active sessions: {len(user_sessions)}")
    
    if user_sessions:
        print("\nSession details:")
        for token, session_data in list(user_sessions.items())[:5]:  # Show first 5
            expired = datetime.now() > session_data['expires_at']
            print(f"  Token: {token[:20]}...")
            print(f"  User ID: {session_data['user_id']}")
            print(f"  Created: {session_data['created_at']}")
            print(f"  Expires: {session_data['expires_at']}")
            print(f"  Status: {'EXPIRED' if expired else 'ACTIVE'}")
            print()
    else:
        print("No active sessions found")
    
    # Check session file
    if os.path.exists('.sessions.json'):
        with open('.sessions.json', 'r') as f:
            try:
                file_sessions = json.load(f)
                print(f"Sessions in file: {len(file_sessions)}")
            except:
                print("Error reading sessions file")
    else:
        print("No sessions file found")

def create_test_session():
    """Create a test session for debugging"""
    print("\n🧪 Creating Test Session")
    print("=" * 40)
    
    db = next(get_db())
    
    # Get first user
    user = db.query(User).first()
    if not user:
        print("❌ No users found in database")
        return
    
    # Create session
    token = create_session_token(user.id)
    print(f"✅ Created session for user {user.email}")
    print(f"   Token: {token[:20]}...")
    print(f"   Full token: {token}")
    
    # Test session retrieval
    session_data = get_user_from_session(token)
    if session_data:
        print(f"✅ Session retrieval successful")
        print(f"   User ID: {session_data['user_id']}")
    else:
        print("❌ Session retrieval failed")
    
    db.close()

def cleanup_expired_sessions():
    """Clean up expired sessions"""
    print("\n🧹 Cleaning Up Expired Sessions")
    print("=" * 40)
    
    expired_count = 0
    current_time = datetime.now()
    
    expired_tokens = []
    for token, session_data in user_sessions.items():
        if current_time > session_data['expires_at']:
            expired_tokens.append(token)
    
    for token in expired_tokens:
        del user_sessions[token]
        expired_count += 1
    
    print(f"Removed {expired_count} expired sessions")
    
    if expired_count > 0:
        save_sessions_to_file()
        print("Sessions file updated")

def fix_session_permissions():
    """Fix session file permissions"""
    print("\n🔧 Fixing Session File Permissions")
    print("=" * 40)
    
    try:
        if os.path.exists('.sessions.json'):
            os.chmod('.sessions.json', 0o644)
            print("✅ Session file permissions fixed")
        else:
            print("No session file found")
    except Exception as e:
        print(f"❌ Error fixing permissions: {e}")

def simulate_login():
    """Simulate a login process for testing"""
    print("\n🎭 Simulating Login Process")
    print("=" * 40)
    
    db = next(get_db())
    
    # Get a user
    user = db.query(User).first()
    if not user:
        print("❌ No users found")
        return None
    
    print(f"Simulating login for: {user.email}")
    
    # Create session (as login would do)
    token = create_session_token(user.id)
    
    print(f"✅ Session created: {token[:20]}...")
    print(f"🍪 Cookie would be set with token: {token}")
    
    # Test immediate retrieval
    session_data = get_user_from_session(token)
    if session_data:
        print(f"✅ Session immediately retrievable")
    else:
        print(f"❌ Session not retrievable")
    
    db.close()
    return token

def test_job_posting_auth():
    """Test the authentication flow for job posting"""
    print("\n💼 Testing Job Posting Authentication")
    print("=" * 40)
    
    # Simulate the login and get token
    token = simulate_login()
    if not token:
        return
    
    # Test the job posting authentication flow
    print(f"Testing job posting with token: {token[:20]}...")
    
    # This simulates what the job posting route does
    session_data = get_user_from_session(token)
    if session_data:
        print("✅ Token validation successful")
        
        db = next(get_db())
        user = db.query(User).filter(User.id == session_data['user_id']).first()
        
        if user:
            print(f"✅ User found: {user.email}")
            print(f"   User type: {user.user_type}")
            print(f"   Verified: {user.is_verified}")
            print(f"   Can post jobs: {user.can_post_jobs()}")
        else:
            print("❌ User not found in database")
        
        db.close()
    else:
        print("❌ Token validation failed")

def main():
    """Main function"""
    print("🐛 Session Debug Tool")
    print("=" * 50)
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            show_session_status()
        elif command == "create":
            create_test_session()
        elif command == "cleanup":
            cleanup_expired_sessions()
        elif command == "fix":
            fix_session_permissions()
        elif command == "login":
            simulate_login()
        elif command == "test":
            test_job_posting_auth()
        elif command == "all":
            show_session_status()
            cleanup_expired_sessions()
            create_test_session()
            test_job_posting_auth()
        else:
            print(f"Unknown command: {command}")
    else:
        print("Available commands:")
        print("  status  - Show session status")
        print("  create  - Create test session")
        print("  cleanup - Clean expired sessions")
        print("  fix     - Fix file permissions")
        print("  login   - Simulate login")
        print("  test    - Test job posting auth")
        print("  all     - Run all tests")
        print()
        print("Usage: python debug_sessions.py <command>")

if __name__ == "__main__":
    main()
