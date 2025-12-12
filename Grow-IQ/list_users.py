#!/usr/bin/env python3
"""
List all users in the database with their login credentials
"""
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_enhanced import get_db, init_database
from models import User

def list_all_users():
    """List all users with their credentials"""
    print("=" * 70)
    print("🔍 LISTING ALL USERS IN DATABASE")
    print("=" * 70)
    
    try:
        # Initialize database
        init_database()
        
        # Get database session
        db = next(get_db())
        
        try:
            # Query all users
            users = db.query(User).order_by(User.id).all()
            
            if not users:
                print("\n❌ No users found in database!")
                print("\n💡 To create test accounts, run one of these scripts:")
                print("   - python create_three_test_accounts.py")
                print("   - python create_test_accounts.py")
                print("   - python clean_db_create_test_accounts.py")
                return
            
            print(f"\n📊 Total Users: {len(users)}\n")
            print("-" * 70)
            
            for idx, user in enumerate(users, 1):
                print(f"\n{idx}. USER ID: {user.id}")
                print(f"   Username:  {user.username}")
                print(f"   Email:     {user.email}")
                print(f"   Full Name: {getattr(user, 'full_name', 'N/A')}")
                print(f"   User Type: {getattr(user, 'user_type', 'N/A')}")
                print(f"   Verified:  {getattr(user, 'is_verified', False)}")
                print(f"   Active:    {getattr(user, 'is_active', True)}")
                
                # Note: Passwords are hashed, so we can't show them
                # But we can show which test accounts might exist
                print(f"   ⚠️  Password: [HASHED - Cannot display]")
                
                # Check if this matches known test account patterns
                known_accounts = {
                    "admin@test.com": "admin123",
                    "hr@testcompany.com": "hrpass123",
                    "user@test.com": "user123",
                    "testuser@example.com": "test123",
                    "hr@techcorp.com": "hr123",
                    "premium@example.com": "premium123",
                    "admin@qrowiq.com": "Admin123!",
                    "demo@qrowiq.com": "Demo123!",
                    "test@qrowiq.com": "Test123!",
                }
                
                if user.email in known_accounts:
                    print(f"   💡 Likely Password: {known_accounts[user.email]}")
                
                print("-" * 70)
            
            print("\n" + "=" * 70)
            print("📝 NOTE: Passwords are stored as hashes and cannot be retrieved.")
            print("   If you need to reset a password, use the password reset feature")
            print("   or create new test accounts using the creation scripts.")
            print("=" * 70)
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_all_users()

