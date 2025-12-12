#!/usr/bin/env python3
"""
Migration script to add keywords_json field to MockInterviewSession table
"""

import sqlite3
import os
from datetime import datetime

def migrate_keywords_json():
    """Add keywords_json field to mock_interview_sessions table"""
    
    db_path = "dashboard.db"
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(mock_interview_sessions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if "keywords_json" not in columns:
            print("Adding column: keywords_json")
            cursor.execute("ALTER TABLE mock_interview_sessions ADD COLUMN keywords_json TEXT")
        else:
            print("Column keywords_json already exists, skipping...")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔄 Starting Keywords JSON Migration...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    success = migrate_keywords_json()
    
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        exit(1)
