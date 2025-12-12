#!/usr/bin/env python3
"""
Create two test accounts:
- Normal user (can log in, cannot post jobs)
- HR/domain user (verified company email, can access HR dashboard and post jobs)
"""

from database import get_db, init_database
from models import User
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError


def upsert_user(db, *, username: str, email: str, full_name: str, title: str,
                company: str, location: str, user_type: str, is_verified: bool,
                password: str, domain: str | None = None) -> User | None:
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
            existing.password_hash = generate_password_hash(password)
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
            password_hash=generate_password_hash(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        return None


def main():
    init_database()
    db = next(get_db())
    try:
        # Normal user
        normal_user = upsert_user(
            db,
            username="testuser",
            email="testuser@example.com",
            full_name="Test User",
            title="Software Developer",
            company="Test Company",
            location="Test City",
            user_type="normal",
            is_verified=True,
            password="testpass123",
        )

        # HR/domain user
        hr_user = upsert_user(
            db,
            username="hr_test",
            email="hr@testcompany.com",
            full_name="HR Test",
            title="HR Manager",
            company="Test Company Inc",
            location="San Francisco, CA",
            user_type="domain",
            is_verified=True,
            password="hrpass123",
            domain="testcompany.com",
        )

        print("\n=== Test Accounts ===")
        if normal_user:
            print("Normal User:")
            print("  Email: testuser@example.com")
            print("  Username: testuser")
            print("  Password: testpass123")
            print(f"  ID: {normal_user.id}")
        else:
            print("Failed to create/update normal user")

        if hr_user:
            print("\nHR User:")
            print("  Email: hr@testcompany.com")
            print("  Username: hr_test")
            print("  Password: hrpass123")
            print("  Note: Verified domain user (can access HR dashboard)")
            print(f"  ID: {hr_user.id}")
        else:
            print("Failed to create/update HR user")

    finally:
        db.close()


if __name__ == "__main__":
    main()


