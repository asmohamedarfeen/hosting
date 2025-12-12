#!/usr/bin/env python3
"""
Test script to debug HR dashboard button visibility
"""

import os
import sys
from sqlalchemy.orm import Session

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database import get_db
    from models import User
    
    print("✅ Successfully imported database and models")
    
    # Get database session
    db = next(get_db())
    
    # Get all users
    users = db.query(User).all()
    print(f"\n📊 Found {len(users)} users in database")
    
    for user in users:
        print(f"\n👤 User: {user.username} ({user.email})")
        print(f"   User Type: {user.user_type}")
        print(f"   Is Verified: {user.is_verified}")
        print(f"   Domain ID: {user.domain_id}")
        print(f"   HR ID: {user.hr_id}")
        
        try:
            is_hr = user.is_hr_user()
            print(f"   Is HR User: {is_hr}")
        except Exception as e:
            print(f"   ❌ Error checking is_hr_user(): {e}")
        
        try:
            access_type = user.get_access_type()
            print(f"   Access Type: {access_type}")
        except Exception as e:
            print(f"   ❌ Error checking get_access_type(): {e}")
        
        try:
            has_domain = user.has_domain_access()
            print(f"   Has Domain Access: {has_domain}")
        except Exception as e:
            print(f"   ❌ Error checking has_domain_access(): {e}")
        
        try:
            can_manage = user.can_manage_applications()
            print(f"   Can Manage Applications: {can_manage}")
        except Exception as e:
            print(f"   ❌ Error checking can_manage_applications(): {e}")
    
    # Test specific user types
    print("\n🔍 Testing specific user scenarios:")
    
    # Test domain email user
    domain_email_user = db.query(User).filter(User.user_type == 'domain').first()
    if domain_email_user:
        print(f"\n📧 Domain Email User Test:")
        print(f"   Email: {domain_email_user.email}")
        print(f"   Is Domain Email: {domain_email_user.is_domain_email()}")
        print(f"   Is HR User: {domain_email_user.is_hr_user()}")
    
    # Test domain ID user
    domain_id_user = db.query(User).filter(User.domain_id.isnot(None)).first()
    if domain_id_user:
        print(f"\n🆔 Domain ID User Test:")
        print(f"   Domain ID: {domain_id_user.domain_id}")
        print(f"   Is HR User: {domain_id_user.is_hr_user()}")
    
    # Test HR ID user
    hr_id_user = db.query(User).filter(User.hr_id.isnot(None)).first()
    if hr_id_user:
        print(f"\n👔 HR ID User Test:")
        print(f"   HR ID: {hr_id_user.hr_id}")
        print(f"   Is HR User: {hr_id_user.is_hr_user()}")
    
    db.close()
    print("\n✅ Test completed successfully")
    
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()
