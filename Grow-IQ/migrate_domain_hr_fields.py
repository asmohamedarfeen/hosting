#!/usr/bin/env python3
"""
Database Migration Script: Add domain_id and hr_id fields to User table

This script adds new fields for domain ID and HR ID management to the existing User table.
Run this script after updating the models.py file to ensure database schema compatibility.
"""

import os
import sys
import sqlite3
from datetime import datetime

def migrate_database():
    """Add domain_id and hr_id fields to the users table"""
    
    # Database file path
    db_path = "dashboard.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking current database schema...")
        
        # Check if fields already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns in users table: {columns}")
        
        # Add domain_id field if it doesn't exist
        if 'domain_id' not in columns:
            print("➕ Adding domain_id field...")
            cursor.execute("ALTER TABLE users ADD COLUMN domain_id TEXT")
            print("✅ domain_id field added successfully")
        else:
            print("ℹ️  domain_id field already exists")
        
        # Add hr_id field if it doesn't exist
        if 'hr_id' not in columns:
            print("➕ Adding hr_id field...")
            cursor.execute("ALTER TABLE users ADD COLUMN hr_id TEXT")
            print("✅ hr_id field added successfully")
        else:
            print("ℹ️  hr_id field already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the new schema
        cursor.execute("PRAGMA table_info(users)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns in users table: {new_columns}")
        
        # Create some sample data for testing
        print("\n🔧 Creating sample domain and HR users for testing...")
        
        # Sample domain ID user
        cursor.execute("""
            INSERT OR REPLACE INTO users 
            (username, email, full_name, password_hash, user_type, domain_id, is_verified, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'domain_user',
            'user@company.com',
            'Domain User',
            'sample_hash',  # In production, use proper password hash
            'domain',
            'COMPANY_DOMAIN_001',
            True,
            True,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # Sample HR ID user
        cursor.execute("""
            INSERT OR REPLACE INTO users 
            (username, email, full_name, password_hash, user_type, hr_id, is_verified, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'hr_user',
            'hr@company.com',
            'HR Manager',
            'sample_hash',  # In production, use proper password hash
            'domain',
            'HR_DEPT_001',
            True,
            True,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # Sample user with both domain_id and hr_id
        cursor.execute("""
            INSERT OR REPLACE INTO users 
            (username, email, full_name, password_hash, user_type, domain_id, hr_id, is_verified, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'senior_hr',
            'senior.hr@company.com',
            'Senior HR Director',
            'sample_hash',  # In production, use proper password hash
            'domain',
            'COMPANY_DOMAIN_001',
            'HR_DEPT_001',
            True,
            True,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        print("✅ Sample users created successfully")
        
        # Display migration summary
        print("\n📊 Migration Summary:")
        print("=" * 50)
        
        # Count users by type
        cursor.execute("SELECT user_type, COUNT(*) FROM users GROUP BY user_type")
        user_counts = cursor.fetchall()
        for user_type, count in user_counts:
            print(f"Users with type '{user_type}': {count}")
        
        # Count users with domain_id
        cursor.execute("SELECT COUNT(*) FROM users WHERE domain_id IS NOT NULL")
        domain_id_count = cursor.fetchone()[0]
        print(f"Users with domain_id: {domain_id_count}")
        
        # Count users with hr_id
        cursor.execute("SELECT COUNT(*) FROM users WHERE hr_id IS NOT NULL")
        hr_id_count = cursor.fetchone()[0]
        print(f"Users with hr_id: {hr_id_count}")
        
        # Count users with both
        cursor.execute("SELECT COUNT(*) FROM users WHERE domain_id IS NOT NULL AND hr_id IS NOT NULL")
        both_count = cursor.fetchone()[0]
        print(f"Users with both domain_id and hr_id: {both_count}")
        
        print("=" * 50)
        
        conn.close()
        print("\n🎉 Database migration completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_migration():
    """Test the migration by checking if new fields are accessible"""
    
    try:
        import models
        from database import get_db
        from sqlalchemy.orm import Session
        
        print("\n🧪 Testing migration with models...")
        
        # Test database connection
        db = next(get_db())
        
        # Test creating a user with new fields
        test_user = models.User(
            username='test_migration',
            email='test@migration.com',
            full_name='Test Migration User',
            user_type='domain',
            domain_id='TEST_DOMAIN_001',
            hr_id='TEST_HR_001',
            is_verified=True,
            is_active=True
        )
        
        # Test the new methods
        print(f"User access type: {test_user.get_access_type()}")
        print(f"Has domain access: {test_user.has_domain_access()}")
        print(f"Is HR user: {test_user.is_hr_user()}")
        print(f"Can manage applications: {test_user.can_manage_applications()}")
        
        print("✅ Model tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration for domain_id and hr_id fields...")
    print("=" * 60)
    
    # Run migration
    if migrate_database():
        print("\n🔍 Running post-migration tests...")
        test_migration()
        
        print("\n📝 Migration Instructions:")
        print("1. The database has been updated with new fields")
        print("2. Sample users have been created for testing")
        print("3. You can now use the enhanced HR dashboard features")
        print("4. Access the enhanced dashboard at /hr/enhanced-dashboard")
        print("5. Regular HR dashboard remains at /hr/dashboard")
        
        print("\n🎯 Next Steps:")
        print("- Test the enhanced HR dashboard with domain_id or hr_id users")
        print("- Update existing users with domain_id or hr_id as needed")
        print("- Configure access control for your organization")
        
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
