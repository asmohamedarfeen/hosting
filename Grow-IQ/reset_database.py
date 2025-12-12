#!/usr/bin/env python3
"""
Script to reset database and create fresh working users
"""
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def reset_database():
    """Reset database and create fresh users"""
    print("🗑️ Resetting Qrow IQ Database...")
    print("=" * 50)
    
    try:
        # Import required modules
        from database import engine, init_database
        from models import Base, User
        from werkzeug.security import generate_password_hash
        from datetime import datetime
        
        print("✅ Modules imported successfully")
        
        # Drop all tables
        print("\n1️⃣ Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped")
        
        # Recreate tables
        print("\n2️⃣ Recreating tables...")
        if init_database():
            print("✅ Tables recreated successfully")
        else:
            print("❌ Failed to recreate tables")
            return False
        
        # Create fresh users
        print("\n3️⃣ Creating fresh users...")
        
        # Test user 1
        user1 = User(
            username="admin",
            email="admin@qrowiq.com",
            full_name="Admin User",
            company="Qrow IQ",
            password_hash=generate_password_hash("Admin123!"),
            profile_image="default-avatar.svg",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Test user 2
        user2 = User(
            username="demo",
            email="demo@qrowiq.com",
            full_name="Demo User",
            company="Demo Company",
            password_hash=generate_password_hash("Demo123!"),
            profile_image="default-avatar.svg",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Test user 3
        user3 = User(
            username="testuser",
            email="test@qrowiq.com",
            full_name="Test User",
            company="Test Company",
            password_hash=generate_password_hash("Test123!"),
            profile_image="default-avatar.svg",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Add users to database
        from sqlalchemy.orm import Session
        db = Session(engine)
        
        try:
            db.add(user1)
            db.add(user2)
            db.add(user3)
            db.commit()
            print("✅ 3 fresh users created successfully")
            
            # Verify users
            users = db.query(User).all()
            print(f"   Total users in database: {len(users)}")
            for user in users:
                print(f"   - {user.username} ({user.email})")
                
        except Exception as e:
            db.rollback()
            print(f"❌ Failed to create users: {e}")
            return False
        finally:
            db.close()
        
        print("\n✅ Database reset completed successfully!")
        print("\n🔑 Test Credentials:")
        print("   Username: admin, Password: Admin123!")
        print("   Username: demo, Password: Demo123!")
        print("   Username: testuser, Password: Test123!")
        print("\n🚀 Next steps:")
        print("1. Restart your app: python start.py")
        print("2. Visit: http://localhost:8000")
        print("3. Login with any of the test credentials above")
        print("4. Should work perfectly now!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting Database Reset...")
    print("⚠️  WARNING: This will delete ALL existing data!")
    print()
    
    confirm = input("Are you sure you want to reset the database? (yes/no): ")
    if confirm.lower() in ['yes', 'y']:
        reset_database()
    else:
        print("Database reset cancelled.")
