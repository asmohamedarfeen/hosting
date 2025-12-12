#!/usr/bin/env python3
"""
Clean the database and create 3 test accounts:
1. Admin account (user_type='premium' for now, since 'admin' is not in constraint)
2. HR account (user_type='domain', verified, company email)
3. Regular user account (user_type='normal')
"""
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, init_database
from models import Base, User
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import Session

def clean_and_create_test_accounts():
    """Clean database and create 3 test accounts"""
    print("🗑️  Cleaning Database and Creating Test Accounts...")
    print("=" * 60)
    
    try:
        # Drop all tables
        print("\n1️⃣  Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("   ✅ All tables dropped")
        
        # Recreate tables
        print("\n2️⃣  Recreating tables...")
        Base.metadata.create_all(bind=engine)
        print("   ✅ Tables recreated successfully")
        
        # Create database session
        db = Session(engine)
        
        try:
            # Create Admin Account
            print("\n3️⃣  Creating test accounts...")
            
            admin = User(
                username="admin",
                email="admin@test.com",
                full_name="Admin User",
                title="System Administrator",
                company="Test Company",
                location="Global",
                password_hash=generate_password_hash("admin123"),
                user_type="premium",  # Using 'premium' since 'admin' is not in constraint
                is_verified=True,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(admin)
            
            # Create HR Account (company email domain for HR access)
            hr = User(
                username="hr",
                email="hr@testcompany.com",  # Company domain email (not free email provider)
                full_name="HR Manager",
                title="HR Manager",
                company="Test Company",
                location="New York, NY",
                password_hash=generate_password_hash("hr123"),
                user_type="domain",
                domain="testcompany.com",  # Company domain
                is_verified=True,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(hr)
            
            # Create Regular User Account
            user = User(
                username="user",
                email="user@test.com",
                full_name="Test User",
                title="Software Developer",
                company="Tech Corp",
                location="San Francisco, CA",
                password_hash=generate_password_hash("user123"),
                user_type="normal",
                is_verified=False,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(user)
            
            # Commit all users
            db.commit()
            print("   ✅ 3 test accounts created successfully")
            
            # Verify and display accounts
            print("\n4️⃣  Verification:")
            users = db.query(User).all()
            print(f"   Total users in database: {len(users)}")
            for u in users:
                print(f"   - {u.username} ({u.email}) - Type: {u.user_type}")
            
            print("\n" + "=" * 60)
            print("✅ Database cleaned and test accounts created!")
            print("\n🔑 Test Account Credentials:")
            print("-" * 60)
            print("1️⃣  ADMIN ACCOUNT:")
            print("   Email:    admin@test.com")
            print("   Password: admin123")
            print("   Type:     Premium (Admin-like)")
            print("-" * 60)
            print("2️⃣  HR ACCOUNT:")
            print("   Email:    hr@testcompany.com")
            print("   Password: hr123")
            print("   Type:     Domain (HR Access)")
            print("-" * 60)
            print("3️⃣  REGULAR USER ACCOUNT:")
            print("   Email:    user@test.com")
            print("   Password: user123")
            print("   Type:     Normal")
            print("-" * 60)
            print("\n🚀 Next Steps:")
            print("   1. Restart your app: python start.py")
            print("   2. Visit: http://localhost:8000")
            print("   3. Login with any of the test credentials above")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"\n❌ Failed to create test accounts: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ Database operation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("⚠️  WARNING: This will delete ALL existing data!")
    print()
    confirm = input("Are you sure you want to clean the database and create test accounts? (yes/no): ")
    if confirm.lower() in ['yes', 'y']:
        if clean_and_create_test_accounts():
            print("\n🎉 Success!")
        else:
            print("\n❌ Failed!")
            sys.exit(1)
    else:
        print("\nOperation cancelled.")

