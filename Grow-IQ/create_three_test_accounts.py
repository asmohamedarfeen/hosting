#!/usr/bin/env python3
"""
Create three test accounts for testing:
1. Normal user (can log in, cannot post jobs)
2. HR/domain user (verified company email, can access HR dashboard and post jobs)
3. Premium user (all features access)
"""

from database_enhanced import get_db, init_database
from models import User
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from typing import Optional

def upsert_user(db, *, username: str, email: str, full_name: str, title: str,
                company: str, location: str, user_type: str, is_verified: bool,
                password: str, domain: Optional[str] = None, industry: Optional[str] = None, 
                skills: Optional[str] = None) -> Optional[User]:
    """Create or update a user account"""
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            existing.username = username
            existing.full_name = full_name
            existing.title = title
            existing.company = company
            existing.location = location
            existing.user_type = user_type
            existing.is_verified = is_verified
            existing.is_active = True
            existing.domain = domain
            existing.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            if industry:
                existing.industry = industry
            if skills:
                existing.skills = skills
            db.commit()
            db.refresh(existing)
            return existing

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            title=title,
            company=company,
            location=location,
            user_type=user_type,
            is_verified=is_verified,
            is_active=True,
            domain=domain,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
            industry=industry,
            skills=skills,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        return None


def main():
    print("🚀 Creating three test accounts...")
    print("-" * 60)
    
    init_database()
    db = next(get_db())
    try:
        # Account 1: Normal User
        normal_user = upsert_user(
            db,
            username="testuser",
            email="testuser@example.com",
            full_name="John Doe",
            title="Software Developer",
            company="Tech Solutions Inc",
            location="New York, NY",
            user_type="normal",
            is_verified=True,
            password="test123",
            industry="Technology",
            skills='["Python", "JavaScript", "React", "Node.js"]',
        )

        # Account 2: HR/Domain User
        hr_user = upsert_user(
            db,
            username="hr_manager",
            email="hr@techcorp.com",
            full_name="Jane Smith",
            title="HR Manager",
            company="Tech Corp",
            location="San Francisco, CA",
            user_type="domain",
            is_verified=True,
            password="hr123",
            domain="techcorp.com",
            industry="Human Resources",
            skills='["Recruitment", "Talent Management", "HR Analytics"]',
        )

        # Account 3: Premium User
        premium_user = upsert_user(
            db,
            username="premium_user",
            email="premium@example.com",
            full_name="Alex Johnson",
            title="Senior Software Engineer",
            company="Innovation Labs",
            location="Seattle, WA",
            user_type="premium",
            is_verified=True,
            password="premium123",
            industry="Technology",
            skills='["Python", "Django", "FastAPI", "AWS", "Docker", "Kubernetes"]',
        )

        print("\n" + "=" * 60)
        print("✅ TEST ACCOUNTS CREATED SUCCESSFULLY")
        print("=" * 60)
        
        if normal_user:
            print("\n📌 ACCOUNT 1 - NORMAL USER")
            print("   Email:    testuser@example.com")
            print("   Username: testuser")
            print("   Password: test123")
            print("   Type:     Normal User")
            print("   Features: Basic features, job browsing, connections")
            print(f"   User ID:  {normal_user.id}")
        else:
            print("\n❌ Failed to create/update normal user")

        if hr_user:
            print("\n📌 ACCOUNT 2 - HR/DOMAIN USER")
            print("   Email:    hr@techcorp.com")
            print("   Username: hr_manager")
            print("   Password: hr123")
            print("   Type:     HR/Domain User")
            print("   Features: HR Dashboard, job posting, candidate management")
            print(f"   User ID:  {hr_user.id}")
        else:
            print("\n❌ Failed to create/update HR user")

        if premium_user:
            print("\n📌 ACCOUNT 3 - PREMIUM USER")
            print("   Email:    premium@example.com")
            print("   Username: premium_user")
            print("   Password: premium123")
            print("   Type:     Premium User")
            print("   Features: All features, unlimited AI tools, advanced analytics")
            print(f"   User ID:  {premium_user.id}")
        else:
            print("\n❌ Failed to create/update premium user")

        print("\n" + "=" * 60)
        print("🌐 Login URL: http://localhost:8000/login")
        print("=" * 60)
        print("\n")

    except Exception as e:
        print(f"\n❌ Error creating test accounts: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()

