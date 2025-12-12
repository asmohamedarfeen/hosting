


#!/usr/bin/env python3
"""
Test script to verify database connectivity and User model
"""
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """Test database connectivity and User model"""
    print("🧪 Testing Database and User Model...")
    print("=" * 50)
    
    try:
        # Test 1: Import database module
        print("\n1️⃣ Testing database imports...")
        from database import get_db, test_db_connection, init_database
        print("✅ Database module imported successfully")
        
        # Test 2: Test database connection
        print("\n2️⃣ Testing database connection...")
        if test_db_connection():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False
        
        # Test 3: Test database initialization
        print("\n3️⃣ Testing database initialization...")
        if init_database():
            print("✅ Database tables created/verified successfully")
        else:
            print("❌ Database initialization failed")
            return False
        
        # Test 4: Test User model import
        print("\n4️⃣ Testing User model import...")
        from models import User
        print("✅ User model imported successfully")
        
        # Test 5: Test database session
        print("\n5️⃣ Testing database session...")
        db = next(get_db())
        print("✅ Database session created successfully")
        
        # Test 6: Test User table query
        print("\n6️⃣ Testing User table query...")
        try:
            users = db.query(User).all()
            print(f"✅ User table query successful. Found {len(users)} users")
            
            # Test 7: Test User model methods
            if users:
                user = users[0]
                print(f"   First user: {user.username} ({user.email})")
                print(f"   Profile image URL: {user.get_profile_image_url()}")
                print(f"   Is external image: {user.is_external_profile_image()}")
            else:
                print("   No users found in database (this is normal for a new database)")
                
        except Exception as e:
            print(f"❌ User table query failed: {e}")
            return False
        
        # Test 8: Test password hashing
        print("\n8️⃣ Testing password hashing...")
        try:
            from werkzeug.security import generate_password_hash, check_password_hash
            
            test_password = "TestPassword123!"
            hashed = generate_password_hash(test_password)
            print("✅ Password hashing successful")
            
            if check_password_hash(hashed, test_password):
                print("✅ Password verification successful")
            else:
                print("❌ Password verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Password hashing test failed: {e}")
            return False
        
        db.close()
        print("\n✅ All database tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_auth_utils():
    """Test authentication utilities"""
    print("\n🧪 Testing Authentication Utilities...")
    print("=" * 50)
    
    try:
        # Test 1: Import auth_utils
        print("\n1️⃣ Testing auth_utils import...")
        from auth_utils import create_session_token, get_user_from_session, cleanup_expired_sessions
        print("✅ auth_utils imported successfully")
        
        # Test 2: Test session token creation
        print("\n2️⃣ Testing session token creation...")
        token = create_session_token(1)
        print(f"✅ Session token created: {token[:20]}...")
        
        # Test 3: Test session retrieval
        print("\n3️⃣ Testing session retrieval...")
        session_data = get_user_from_session(token)
        if session_data and session_data['user_id'] == 1:
            print("✅ Session retrieval successful")
        else:
            print("❌ Session retrieval failed")
            return False
        
        # Test 4: Test session cleanup
        print("\n4️⃣ Testing session cleanup...")
        cleanup_expired_sessions()
        print("✅ Session cleanup successful")
        
        print("\n✅ All authentication utility tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Authentication utility test failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting CareerConnect Database Tests...")
    print()
    
    db_success = test_database()
    auth_success = test_auth_utils()
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    
    if db_success and auth_success:
        print("✅ All tests passed! Your database and authentication are working correctly.")
        print("\n🚀 Next steps:")
        print("1. Start your app: python start.py")
        print("2. Visit: http://localhost:8000")
        print("3. Should redirect to login page")
        print("4. Test signup and login")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure all dependencies are installed")
        print("2. Check database configuration")
        print("3. Verify file permissions")
