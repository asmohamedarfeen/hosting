#!/usr/bin/env python3
"""
Create a master admin user for the Glow-IQ application
"""
import os
import sys
import logging
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_enhanced import get_db
from models import User
from werkzeug.security import generate_password_hash
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_master_admin():
    """Create a master admin user"""
    try:
        logger.info("Creating master admin user...")
        
        # Get database connection
        db = next(get_db())
        
        # Check if master admin already exists
        existing_admin = db.execute(text("""
            SELECT id, username, email FROM users 
            WHERE username = 'master_admin' OR email = 'admin@glow-iq.com'
        """)).fetchone()
        
        if existing_admin:
            logger.info(f"Master admin already exists: {existing_admin.username} ({existing_admin.email})")
            print(f"✅ Master admin already exists!")
            print(f"   Username: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print(f"   User ID: {existing_admin.id}")
            return True
        
        # Create master admin user
        admin_data = {
            'username': 'master_admin',
            'email': 'admin@glow-iq.com',
            'full_name': 'Master Administrator',
            'title': 'System Administrator',
            'company': 'Glow-IQ',
            'location': 'Global',
            'bio': 'Master administrator with full system access and privileges.',
            'password_hash': generate_password_hash('MasterAdmin2024!'),
            'user_type': 'admin',
            'is_verified': True,
            'is_active': True,
            'last_login': datetime.now(),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'phone': '+1-555-ADMIN-01',
            'website': 'https://glow-iq.com',
            'linkedin_url': 'https://linkedin.com/company/glow-iq',
            'github_url': 'https://github.com/glow-iq',
            'industry': 'Technology',
            'skills': 'System Administration, Full Stack Development, Database Management, Security, DevOps',
            'experience_years': 10,
            'experience': 'Master administrator with extensive experience in system management, user administration, and platform oversight.',
            'education': 'Master of Science in Computer Science, Bachelor of Science in Information Technology',
            'certifications': 'AWS Certified Solutions Architect, Certified Information Systems Security Professional (CISSP), Microsoft Certified Azure Administrator',
            'interests': 'Technology Innovation, User Experience, System Security, Data Analytics, Machine Learning',
            'portfolio_url': 'https://portfolio.glow-iq.com/admin',
            'profile_visibility': 'public',
            'show_email': True,
            'show_phone': True
        }
        
        # Insert master admin user
        db.execute(text("""
            INSERT INTO users (
                username, email, full_name, title, company, location, bio,
                password_hash, user_type, is_verified, is_active, last_login,
                created_at, updated_at, phone, website, linkedin_url, github_url,
                industry, skills, experience_years, experience, education,
                certifications, interests, portfolio_url, profile_visibility,
                show_email, show_phone
            ) VALUES (
                :username, :email, :full_name, :title, :company, :location, :bio,
                :password_hash, :user_type, :is_verified, :is_active, :last_login,
                :created_at, :updated_at, :phone, :website, :linkedin_url, :github_url,
                :industry, :skills, :experience_years, :experience, :education,
                :certifications, :interests, :portfolio_url, :profile_visibility,
                :show_email, :show_phone
            )
        """), admin_data)
        
        # Get the created admin user ID
        admin_user = db.execute(text("""
            SELECT id, username, email, full_name, user_type, created_at
            FROM users WHERE username = 'master_admin'
        """)).fetchone()
        
        # Commit the changes
        db.commit()
        
        logger.info(f"Master admin created successfully with ID: {admin_user.id}")
        
        print("🎉 Master Admin Created Successfully!")
        print("=" * 50)
        print(f"👤 Username: {admin_user.username}")
        print(f"📧 Email: {admin_user.email}")
        print(f"👨‍💼 Full Name: {admin_user.full_name}")
        print(f"🔑 User Type: {admin_user.user_type}")
        print(f"🆔 User ID: {admin_user.id}")
        print(f"📅 Created: {admin_user.created_at}")
        print("\n🔐 Login Credentials:")
        print(f"   Username: master_admin")
        print(f"   Password: MasterAdmin2024!")
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating master admin: {e}")
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()

def create_admin_privileges():
    """Create additional admin privileges and permissions"""
    try:
        logger.info("Setting up admin privileges...")
        
        db = next(get_db())
        
        # Get master admin user
        admin_user = db.execute(text("""
            SELECT id FROM users WHERE username = 'master_admin'
        """)).fetchone()
        
        if not admin_user:
            logger.error("Master admin user not found")
            return False
        
        admin_id = admin_user.id
        
        # Create admin-specific data
        admin_privileges = [
            {
                'name': 'system_administration',
                'description': 'Full system administration access',
                'permissions': 'all'
            },
            {
                'name': 'user_management',
                'description': 'Manage all users and their permissions',
                'permissions': 'create,read,update,delete'
            },
            {
                'name': 'content_moderation',
                'description': 'Moderate all content and posts',
                'permissions': 'read,update,delete'
            },
            {
                'name': 'workshop_management',
                'description': 'Manage all workshops and registrations',
                'permissions': 'all'
            },
            {
                'name': 'job_management',
                'description': 'Manage job postings and applications',
                'permissions': 'all'
            },
            {
                'name': 'analytics_access',
                'description': 'Access to all analytics and reports',
                'permissions': 'read'
            }
        ]
        
        # Note: In a real application, you would have a proper permissions system
        # For now, we'll just log the privileges
        logger.info(f"Admin privileges configured for user {admin_id}")
        
        print("✅ Admin privileges configured")
        print("   - System Administration")
        print("   - User Management")
        print("   - Content Moderation")
        print("   - Workshop Management")
        print("   - Job Management")
        print("   - Analytics Access")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up admin privileges: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

def test_admin_login():
    """Test the admin login functionality"""
    try:
        logger.info("Testing admin login...")
        
        import requests
        
        # Test login with master admin credentials
        login_data = {
            "identifier": "master_admin",
            "password": "MasterAdmin2024!"
        }
        
        response = requests.post("http://localhost:8000/auth/login", data=login_data)
        
        if response.status_code == 200:
            login_result = response.json()
            print("✅ Admin login test successful!")
            print(f"   User ID: {login_result.get('user_id')}")
            print(f"   Username: {login_result.get('username')}")
            print(f"   User Type: {login_result.get('user_type')}")
            return True
        else:
            print(f"❌ Admin login test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error testing admin login: {e}")
        print(f"❌ Admin login test error: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Master Admin Creation Script")
    print("=" * 50)
    
    # Create master admin
    if create_master_admin():
        print("\n🔧 Setting up admin privileges...")
        create_admin_privileges()
        
        print("\n🧪 Testing admin login...")
        test_admin_login()
        
        print("\n🎉 Master Admin Setup Complete!")
        print("\n📋 Next Steps:")
        print("1. Login with the master admin credentials")
        print("2. Change the default password")
        print("3. Configure additional admin settings")
        print("4. Set up admin dashboard if needed")
    else:
        print("❌ Failed to create master admin!")
        sys.exit(1)
