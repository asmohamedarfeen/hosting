#!/usr/bin/env python3
"""
Database migration script to add streak tracking tables
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database_enhanced import init_database
from models import Streak, StreakLog

def migrate_streaks():
    """Add streak tracking tables to the database"""
    try:
        print("🔄 Starting streak tables migration...")
        
        # Initialize database (this will create new tables)
        init_database()
        
        print("✅ Streak tables migration completed successfully!")
        print("📊 New tables created:")
        print("   - streaks: User activity streaks")
        print("   - streak_logs: Daily activity logs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

def verify_migration():
    """Verify that streak tables were created successfully"""
    try:
        from database import get_db
        from models import Streak, StreakLog
        
        # Try to create a session and query the tables
        engine = create_engine("sqlite:///dashboard.db")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if tables exist
        result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('streaks', 'streak_logs')"))
        tables = [row[0] for row in result]
        
        if 'streaks' in tables and 'streak_logs' in tables:
            print("✅ Verification successful: Both streak tables exist")
            return True
        else:
            print(f"❌ Verification failed: Found tables: {tables}")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CareerConnect Streak Tables Migration")
    print("=" * 50)
    
    # Run migration
    success = migrate_streaks()
    
    if success:
        print("\n🔍 Verifying migration...")
        verify_migration()
        print("\n🎉 Migration completed! You can now use the streak calendar feature.")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")
        sys.exit(1)
