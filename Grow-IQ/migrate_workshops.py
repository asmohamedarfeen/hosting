#!/usr/bin/env python3
"""
Database migration script to add workshop tables
"""
import os
import sys
import logging
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_enhanced import get_db, init_database
from models import Workshop, WorkshopRegistration
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_workshops():
    """Add workshop tables to the database"""
    try:
        logger.info("Starting workshop migration...")
        
        # Get database connection
        db = next(get_db())
        
        # Check if workshops table already exists
        result = db.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='workshops'
        """))
        
        if result.fetchone():
            logger.info("Workshops table already exists, skipping migration")
            return True
        
        # Create workshops table
        logger.info("Creating workshops table...")
        db.execute(text("""
            CREATE TABLE workshops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                instructor VARCHAR(100) NOT NULL,
                instructor_email VARCHAR(120),
                instructor_bio TEXT,
                category VARCHAR(50) NOT NULL,
                level VARCHAR(20) NOT NULL,
                duration_hours INTEGER NOT NULL,
                max_participants INTEGER,
                price INTEGER NOT NULL DEFAULT 0,
                currency VARCHAR(3) NOT NULL DEFAULT 'USD',
                start_date DATETIME NOT NULL,
                end_date DATETIME NOT NULL,
                location VARCHAR(200),
                is_online BOOLEAN NOT NULL DEFAULT 0,
                meeting_link VARCHAR(500),
                materials TEXT,
                prerequisites TEXT,
                learning_objectives TEXT,
                status VARCHAR(20) NOT NULL DEFAULT 'draft',
                created_by INTEGER NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        """))
        
        # Create workshop_registrations table
        logger.info("Creating workshop_registrations table...")
        db.execute(text("""
            CREATE TABLE workshop_registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workshop_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                registration_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) NOT NULL DEFAULT 'registered',
                payment_status VARCHAR(20) NOT NULL DEFAULT 'pending',
                payment_amount INTEGER,
                notes TEXT,
                FOREIGN KEY (workshop_id) REFERENCES workshops (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """))
        
        # Create indexes for better performance
        logger.info("Creating indexes...")
        db.execute(text("CREATE INDEX idx_workshops_category ON workshops (category)"))
        db.execute(text("CREATE INDEX idx_workshops_level ON workshops (level)"))
        db.execute(text("CREATE INDEX idx_workshops_status ON workshops (status)"))
        db.execute(text("CREATE INDEX idx_workshops_start_date ON workshops (start_date)"))
        db.execute(text("CREATE INDEX idx_workshops_created_by ON workshops (created_by)"))
        db.execute(text("CREATE INDEX idx_workshop_registrations_workshop_id ON workshop_registrations (workshop_id)"))
        db.execute(text("CREATE INDEX idx_workshop_registrations_user_id ON workshop_registrations (user_id)"))
        
        # Commit the changes
        db.commit()
        logger.info("Workshop migration completed successfully!")
        
        # Verify tables were created
        result = db.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('workshops', 'workshop_registrations')
        """))
        
        tables = [row[0] for row in result.fetchall()]
        logger.info(f"Created tables: {tables}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during workshop migration: {e}")
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()

def create_sample_workshops():
    """Create some sample workshops for testing"""
    try:
        logger.info("Creating sample workshops...")
        
        db = next(get_db())
        
        # Check if we have any users to create workshops for
        result = db.execute(text("SELECT id FROM users LIMIT 1"))
        user = result.fetchone()
        
        if not user:
            logger.warning("No users found, skipping sample workshop creation")
            return True
        
        user_id = user[0]
        
        # Check if workshops already exist
        result = db.execute(text("SELECT COUNT(*) FROM workshops"))
        count = result.fetchone()[0]
        
        if count > 0:
            logger.info("Workshops already exist, skipping sample creation")
            return True
        
        # Create sample workshops
        sample_workshops = [
            {
                'title': 'Introduction to Python Programming',
                'description': 'Learn the fundamentals of Python programming language including variables, functions, loops, and data structures.',
                'instructor': 'Dr. Sarah Johnson',
                'instructor_email': 'sarah.johnson@example.com',
                'instructor_bio': 'Senior Software Engineer with 10+ years of experience in Python development.',
                'category': 'technical',
                'level': 'beginner',
                'duration_hours': 4,
                'max_participants': 25,
                'price': 0,
                'currency': 'USD',
                'start_date': '2024-02-15 10:00:00',
                'end_date': '2024-02-15 14:00:00',
                'location': 'Online',
                'is_online': True,
                'meeting_link': 'https://meet.google.com/abc-defg-hij',
                'materials': '["Laptop", "Python 3.8+", "Text Editor"]',
                'prerequisites': '["Basic computer skills", "No programming experience required"]',
                'learning_objectives': '["Understand Python syntax", "Write basic Python programs", "Use Python data structures"]',
                'status': 'published',
                'created_by': user_id
            },
            {
                'title': 'Advanced React Development',
                'description': 'Master advanced React concepts including hooks, context, performance optimization, and testing.',
                'instructor': 'Mike Chen',
                'instructor_email': 'mike.chen@example.com',
                'instructor_bio': 'Full-stack developer specializing in React and Node.js with 8 years of experience.',
                'category': 'technical',
                'level': 'advanced',
                'duration_hours': 6,
                'max_participants': 20,
                'price': 15000,  # $150.00
                'currency': 'USD',
                'start_date': '2024-02-20 09:00:00',
                'end_date': '2024-02-20 15:00:00',
                'location': 'Tech Hub, 123 Main St',
                'is_online': False,
                'meeting_link': None,
                'materials': '["Laptop", "Node.js", "VS Code", "Git"]',
                'prerequisites': '["Basic React knowledge", "JavaScript ES6+", "HTML/CSS"]',
                'learning_objectives': '["Master React hooks", "Implement performance optimization", "Write comprehensive tests"]',
                'status': 'published',
                'created_by': user_id
            },
            {
                'title': 'Effective Communication Skills',
                'description': 'Improve your professional communication skills including presentations, emails, and team collaboration.',
                'instructor': 'Lisa Rodriguez',
                'instructor_email': 'lisa.rodriguez@example.com',
                'instructor_bio': 'Communication coach and former corporate trainer with 15 years of experience.',
                'category': 'soft-skills',
                'level': 'intermediate',
                'duration_hours': 3,
                'max_participants': 30,
                'price': 5000,  # $50.00
                'currency': 'USD',
                'start_date': '2024-02-25 14:00:00',
                'end_date': '2024-02-25 17:00:00',
                'location': 'Online',
                'is_online': True,
                'meeting_link': 'https://zoom.us/j/123456789',
                'materials': '["Notebook", "Pen", "Camera (optional)"]',
                'prerequisites': '["Basic English proficiency", "Willingness to participate"]',
                'learning_objectives': '["Improve presentation skills", "Write effective emails", "Enhance team communication"]',
                'status': 'published',
                'created_by': user_id
            }
        ]
        
        for workshop_data in sample_workshops:
            # Add current timestamp
            workshop_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            workshop_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            db.execute(text("""
                INSERT INTO workshops (
                    title, description, instructor, instructor_email, instructor_bio,
                    category, level, duration_hours, max_participants, price, currency,
                    start_date, end_date, location, is_online, meeting_link,
                    materials, prerequisites, learning_objectives, status, created_by,
                    created_at, updated_at
                ) VALUES (
                    :title, :description, :instructor, :instructor_email, :instructor_bio,
                    :category, :level, :duration_hours, :max_participants, :price, :currency,
                    :start_date, :end_date, :location, :is_online, :meeting_link,
                    :materials, :prerequisites, :learning_objectives, :status, :created_by,
                    :created_at, :updated_at
                )
            """), workshop_data)
        
        db.commit()
        logger.info("Sample workshops created successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating sample workshops: {e}")
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("🔧 Workshop Database Migration")
    print("=" * 40)
    
    # Run migration
    if migrate_workshops():
        print("✅ Workshop tables created successfully!")
        
        # Create sample data
        if create_sample_workshops():
            print("✅ Sample workshops created successfully!")
        else:
            print("❌ Failed to create sample workshops")
    else:
        print("❌ Workshop migration failed!")
        sys.exit(1)
    
    print("\n🎉 Workshop system is ready!")
