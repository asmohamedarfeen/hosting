#!/usr/bin/env python3
"""
Migration script to add enhanced AI report fields to MockInterviewSession table
"""

import sqlite3
import os
from datetime import datetime

def migrate_mock_interview_enhanced():
    """Add enhanced AI report fields to mock_interview_sessions table"""
    
    db_path = "dashboard.db"
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(mock_interview_sessions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = [
            ("strengths_json", "TEXT"),
            ("areas_for_improvement_json", "TEXT"),
            ("detailed_analysis_json", "TEXT")
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                print(f"Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE mock_interview_sessions ADD COLUMN {column_name} {column_type}")
            else:
                print(f"Column {column_name} already exists, skipping...")
        
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
    print("🔄 Starting Mock Interview Enhanced Report Migration...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    success = migrate_mock_interview_enhanced()
    
    if success:
        print("🎉 Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        exit(1)
