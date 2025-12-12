#!/usr/bin/env python3
"""
Database migration script to add workshop approval fields
"""
import os
import sys
import logging
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_enhanced import get_db
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_workshop_approval():
    """Add workshop approval fields to the database"""
    try:
        logger.info("Starting workshop approval migration...")
        
        # Get database connection
        db = next(get_db())
        
        # Check if approval_status column already exists
        result = db.execute(text("""
            PRAGMA table_info(workshops)
        """))
        
        columns = [row[1] for row in result.fetchall()]
        
        if 'approval_status' in columns:
            logger.info("Workshop approval fields already exist, skipping migration")
            return True
        
        # Add approval fields to workshops table
        logger.info("Adding workshop approval fields...")
        
        # Add approval_status column
        db.execute(text("""
            ALTER TABLE workshops ADD COLUMN approval_status VARCHAR(20) NOT NULL DEFAULT 'pending'
        """))
        
        # Add approved_by column
        db.execute(text("""
            ALTER TABLE workshops ADD COLUMN approved_by INTEGER
        """))
        
        # Add approved_at column
        db.execute(text("""
            ALTER TABLE workshops ADD COLUMN approved_at DATETIME
        """))
        
        # Add rejection_reason column
        db.execute(text("""
            ALTER TABLE workshops ADD COLUMN rejection_reason TEXT
        """))
        
        # Add foreign key constraint for approved_by
        db.execute(text("""
            CREATE INDEX idx_workshops_approved_by ON workshops (approved_by)
        """))
        
        # Add index for approval_status
        db.execute(text("""
            CREATE INDEX idx_workshops_approval_status ON workshops (approval_status)
        """))
        
        # Update existing published workshops to approved status
        db.execute(text("""
            UPDATE workshops 
            SET approval_status = 'approved', 
                approved_by = created_by,
                approved_at = created_at
            WHERE status = 'published'
        """))
        
        # Commit the changes
        db.commit()
        logger.info("Workshop approval migration completed successfully!")
        
        # Verify the changes
        result = db.execute(text("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN approval_status = 'pending' THEN 1 ELSE 0 END) as pending,
                   SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) as approved,
                   SUM(CASE WHEN approval_status = 'rejected' THEN 1 ELSE 0 END) as rejected
            FROM workshops
        """))
        
        stats = result.fetchone()
        logger.info(f"Workshop approval stats: Total={stats[0]}, Pending={stats[1]}, Approved={stats[2]}, Rejected={stats[3]}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during workshop approval migration: {e}")
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    print("🔧 Workshop Approval Migration")
    print("=" * 40)
    
    if migrate_workshop_approval():
        print("✅ Workshop approval fields added successfully!")
        print("\n📋 New Fields Added:")
        print("   - approval_status (pending, approved, rejected)")
        print("   - approved_by (admin user ID)")
        print("   - approved_at (approval timestamp)")
        print("   - rejection_reason (reason for rejection)")
        print("\n🎉 Workshop approval system is ready!")
    else:
        print("❌ Workshop approval migration failed!")
        sys.exit(1)
