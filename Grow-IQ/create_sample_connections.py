#!/usr/bin/env python3
"""
Script to create sample connections for Qrow IQ
"""
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models import User, Connection
from datetime import datetime

def create_sample_connections():
    """Create sample connections between users"""
    print("🔗 Creating Sample Connections...")
    print("=" * 50)
    
    try:
        # Get database session
        print("1️⃣ Getting database session...")
        db = next(get_db())
        print("✅ Database session obtained")
        
        # Get users
        print("2️⃣ Getting users...")
        users = db.query(User).all()
        if not users:
            print("❌ No users found in database")
            return False
        
        print(f"✅ Found {len(users)} users")
        
        # Check if connections already exist
        print("3️⃣ Checking if connections already exist...")
        existing_connections = db.query(Connection).count()
        if existing_connections > 0:
            print(f"✅ {existing_connections} connections already exist")
            return True
        
        # Create sample connections
        print("4️⃣ Creating sample connections...")
        
        # Get the main test users (skip the old ones)
        test_users = [user for user in users if user.username in ['testuser', 'john_developer', 'sarah_manager', 'mike_designer']]
        
        if len(test_users) < 4:
            print("❌ Not enough test users found")
            return False
        
        # Create connections between test users
        connections_data = [
            {
                "user_id": test_users[0].id,  # Test User
                "connected_user_id": test_users[1].id,  # John Developer
                "status": "accepted"
            },
            {
                "user_id": test_users[0].id,  # Test User
                "connected_user_id": test_users[2].id,  # Sarah Manager
                "status": "accepted"
            },
            {
                "user_id": test_users[1].id,  # John Developer
                "connected_user_id": test_users[2].id,  # Sarah Manager
                "status": "accepted"
            },
            {
                "user_id": test_users[1].id,  # John Developer
                "connected_user_id": test_users[3].id,  # Mike Designer
                "status": "accepted"
            },
            {
                "user_id": test_users[2].id,  # Sarah Manager
                "connected_user_id": test_users[3].id,  # Mike Designer
                "status": "accepted"
            }
        ]
        
        for conn_data in connections_data:
            connection = Connection(
                user_id=conn_data["user_id"],
                connected_user_id=conn_data["connected_user_id"],
                status=conn_data["status"],
                created_at=datetime.now()
            )
            db.add(connection)
        
        db.commit()
        print("✅ Sample connections created successfully!")
        
        # Show the connections
        print("5️⃣ Displaying created connections...")
        all_connections = db.query(Connection).all()
        for conn in all_connections:
            user1 = db.query(User).filter(User.id == conn.user_id).first()
            user2 = db.query(User).filter(User.id == conn.connected_user_id).first()
            if user1 and user2:
                print(f"   {user1.full_name} ↔ {user2.full_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample connections: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("Starting Sample Connections Creation...")
    print()
    
    success = create_sample_connections()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Sample connections created successfully!")
        print("\n🔗 Now your network will have:")
        print("   - 5 connections between test users")
        print("   - A real professional network to explore")
        print("   - Suggested connections to discover")
        print("\n🌐 Next steps:")
        print("1. Login with: test@qrowiq.com / TestPass123!")
        print("2. Go to: http://localhost:8000/home")
        print("3. See your connections and network!")
    else:
        print("❌ Failed to create sample connections")
        print("Check the error messages above")
