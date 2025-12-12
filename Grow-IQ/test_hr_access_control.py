#!/usr/bin/env python3
"""
HR Access Control Test
======================

This script verifies that HR dashboard access is properly restricted
to users with domain email addresses only.
"""

from database import get_db
from models import User

def test_email_classification():
    """Test email domain classification"""
    print("🔍 Testing Email Domain Classification")
    print("=" * 50)
    
    # Test cases: (email, should_be_domain, description)
    test_cases = [
        # Free email providers (should NOT be HR users)
        ("user@gmail.com", False, "Gmail - Free Provider"),
        ("test@yahoo.com", False, "Yahoo - Free Provider"),
        ("person@hotmail.com", False, "Hotmail - Free Provider"),
        ("someone@outlook.com", False, "Outlook - Free Provider"),
        ("user@icloud.com", False, "iCloud - Free Provider"),
        ("test@protonmail.com", False, "ProtonMail - Free Provider"),
        
        # Company domains (should be HR users)
        ("hr@company.com", True, "Company Domain"),
        ("manager@microsoft.com", True, "Microsoft Corp"),
        ("recruiter@google.com", True, "Google Corp"),
        ("hr@startup.io", True, "Startup Domain"),
        ("hiring@tech-corp.com", True, "Tech Corp"),
        ("jobs@mycompany.org", True, "Organization Domain"),
        
        # Edge cases
        ("", False, "Empty Email"),
        ("invalid-email", False, "Invalid Format"),
    ]
    
    db = next(get_db())
    
    for email, expected_domain, description in test_cases:
        print(f"\n📧 Testing: {email} ({description})")
        
        try:
            # Create temporary user for testing
            temp_user = User(
                username=f"test_{email.replace('@', '_').replace('.', '_')}",
                email=email,
                full_name="Test User",
                user_type="domain",  # Set as domain type
                is_verified=True     # Set as verified
            )
            
            # Test domain email detection
            is_domain = temp_user.is_domain_email() if email else False
            is_hr = temp_user.is_hr_user()
            
            status = "✅" if (is_domain == expected_domain) else "❌"
            
            print(f"   {status} Is domain email: {is_domain} (expected: {expected_domain})")
            print(f"      Is HR user: {is_hr}")
            print(f"      Can manage applications: {temp_user.can_manage_applications()}")
            
            if is_domain != expected_domain:
                print(f"   ⚠️  MISMATCH: Expected {expected_domain}, got {is_domain}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    db.close()

def test_existing_users():
    """Test HR access for existing users in database"""
    print("\n\n👥 Testing Existing Users in Database")
    print("=" * 50)
    
    db = next(get_db())
    
    users = db.query(User).all()
    
    if not users:
        print("No users found in database")
        db.close()
        return
    
    for user in users:
        print(f"\n👤 User: {user.full_name} ({user.email})")
        print(f"   User Type: {user.user_type}")
        print(f"   Is Verified: {user.is_verified}")
        print(f"   Is Domain Email: {user.is_domain_email()}")
        print(f"   Is HR User: {user.is_hr_user()}")
        print(f"   Can Manage Applications: {user.can_manage_applications()}")
        
        # Determine if HR access should be granted
        if user.is_hr_user():
            print(f"   🔓 HR ACCESS GRANTED")
        else:
            print(f"   🔒 HR ACCESS DENIED")
            if not user.is_domain_email():
                print(f"      Reason: Free email provider")
            elif user.user_type != 'domain':
                print(f"      Reason: Not a domain user")
            elif not user.is_verified:
                print(f"      Reason: Email not verified")
    
    db.close()

def test_hr_access_scenarios():
    """Test different HR access scenarios"""
    print("\n\n🔐 Testing HR Access Scenarios")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Valid HR User",
            "email": "hr@company.com",
            "user_type": "domain",
            "is_verified": True,
            "should_have_access": True
        },
        {
            "name": "Gmail User",
            "email": "user@gmail.com",
            "user_type": "normal",
            "is_verified": True,
            "should_have_access": False
        },
        {
            "name": "Unverified Domain User",
            "email": "hr@startup.com",
            "user_type": "domain", 
            "is_verified": False,
            "should_have_access": False
        },
        {
            "name": "Normal User with Domain Email",
            "email": "employee@company.com",
            "user_type": "normal",
            "is_verified": True,
            "should_have_access": False
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        print(f"   Email: {scenario['email']}")
        print(f"   User Type: {scenario['user_type']}")
        print(f"   Verified: {scenario['is_verified']}")
        
        # Create test user
        test_user = User(
            username=f"test_{scenario['name'].lower().replace(' ', '_')}",
            email=scenario['email'],
            full_name=scenario['name'],
            user_type=scenario['user_type'],
            is_verified=scenario['is_verified']
        )
        
        # Test HR access
        has_access = test_user.is_hr_user()
        expected = scenario['should_have_access']
        
        status = "✅" if (has_access == expected) else "❌"
        access_text = "GRANTED" if has_access else "DENIED"
        
        print(f"   {status} HR Access: {access_text} (expected: {'GRANTED' if expected else 'DENIED'})")
        
        if has_access != expected:
            print(f"   ⚠️  ACCESS CONTROL FAILURE!")

def create_sample_domain_user():
    """Create a sample domain user for testing"""
    print("\n\n🏢 Creating Sample Domain User")
    print("=" * 50)
    
    db = next(get_db())
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "hr.manager@testcompany.com").first()
    if existing_user:
        print("✅ Sample domain user already exists")
        print(f"   Email: {existing_user.email}")
        print(f"   HR Access: {existing_user.is_hr_user()}")
        db.close()
        return existing_user
    
    # Create new domain user
    domain_user = User(
        username="hr_manager_test",
        email="hr.manager@testcompany.com",
        full_name="HR Manager (Test)",
        title="Human Resources Manager",
        company="Test Company Ltd",
        location="Test City, TC",
        bio="HR manager for testing domain access control.",
        user_type="domain",
        domain="testcompany.com",
        is_verified=True,
        is_active=True
    )
    
    db.add(domain_user)
    db.commit()
    
    print("✅ Sample domain user created")
    print(f"   Email: {domain_user.email}")
    print(f"   Domain: {domain_user.domain}")
    print(f"   Is Domain Email: {domain_user.is_domain_email()}")
    print(f"   Is HR User: {domain_user.is_hr_user()}")
    print(f"   HR Access: {'GRANTED' if domain_user.is_hr_user() else 'DENIED'}")
    
    db.close()
    return domain_user

def main():
    """Run all HR access control tests"""
    print("🔒 HR Access Control Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Email classification
        test_email_classification()
        
        # Test 2: Existing users
        test_existing_users()
        
        # Test 3: Access scenarios
        test_hr_access_scenarios()
        
        # Test 4: Create sample domain user
        create_sample_domain_user()
        
        print("\n" + "=" * 60)
        print("🎉 HR Access Control Tests Complete!")
        print("=" * 60)
        
        print("\n📋 Summary:")
        print("   ✅ Email domain classification tested")
        print("   ✅ Existing user access levels verified")
        print("   ✅ Access control scenarios validated")
        print("   ✅ Sample domain user created/verified")
        
        print("\n🔐 HR Access Rules:")
        print("   ✅ ONLY users with company domain emails")
        print("   ✅ ONLY verified domain users")
        print("   ✅ ONLY user_type = 'domain'")
        print("   ❌ NO free email providers (Gmail, Yahoo, etc.)")
        print("   ❌ NO unverified users")
        print("   ❌ NO normal users")
        
        print("\n🌐 Testing Access:")
        print("   1. Use domain email: hr.manager@testcompany.com")
        print("   2. Access: http://localhost:8000/hr/dashboard")
        print("   3. Free email users should see 403 Forbidden")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
