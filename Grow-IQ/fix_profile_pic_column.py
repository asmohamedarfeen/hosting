#!/usr/bin/env python3
"""
Database Migration Script: Add profile_pic column to users table

This script fixes the login error by adding the missing profile_pic column
that was added to the User model but not yet in the database.
"""

import sqlite3
import os
import sys
from pathlib import Path

def get_database_path():
    """Get the database file path"""
    # Look for database files in common locations
    possible_paths = [
        "dashboard.db",
        "qrowiq.db", 
        "glow_iq.db",
        "../dashboard.db",
        "../qrowiq.db",
        "../glow_iq.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If not found, ask user
    print("❌ Database file not found automatically.")
    print("Please enter the path to your database file:")
    db_path = input("Database path: ").strip()
    
    if os.path.exists(db_path):
        return db_path
    else:
        print(f"❌ File not found: {db_path}")
        return None

def check_database_schema(db_path):
    """Check the current database schema"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info for users table
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print(f"📋 Current users table schema:")
        print(f"{'Column':<20} {'Type':<15} {'Not Null':<10} {'Default':<15}")
        print("-" * 70)
        
        profile_pic_exists = False
        for col in columns:
            col_id, name, type_name, not_null, default_val, pk = col
            print(f"{name:<20} {type_name:<15} {'Yes' if not_null else 'No':<10} {str(default_val):<15}")
            
            if name == 'profile_pic':
                profile_pic_exists = True
        
        conn.close()
        return profile_pic_exists
        
    except Exception as e:
        print(f"❌ Error checking database schema: {e}")
        return False

def add_profile_pic_column(db_path):
    """Add the profile_pic column to the users table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"\n🔧 Adding profile_pic column to users table...")
        
        # Add the profile_pic column
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN profile_pic VARCHAR(500)
        """)
        
        # Commit the changes
        conn.commit()
        
        print("✅ profile_pic column added successfully!")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        profile_pic_exists = False
        for col in columns:
            if col[1] == 'profile_pic':
                profile_pic_exists = True
                break
        
        if profile_pic_exists:
            print("✅ Column verification successful!")
        else:
            print("❌ Column verification failed!")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding profile_pic column: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def backup_database(db_path):
    """Create a backup of the database before making changes"""
    try:
        backup_path = f"{db_path}.backup.{int(time.time())}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not create backup: {e}")
        print("   Proceeding without backup...")
        return False

def main():
    """Main migration function"""
    print("🔧 Profile Picture Database Migration Tool")
    print("=" * 50)
    
    # Get database path
    db_path = get_database_path()
    if not db_path:
        print("❌ Could not determine database path. Exiting.")
        sys.exit(1)
    
    print(f"📁 Using database: {db_path}")
    
    # Check if profile_pic column already exists
    if check_database_schema(db_path):
        print("\n✅ profile_pic column already exists!")
        print("   No migration needed.")
        return
    
    print(f"\n❌ profile_pic column is missing!")
    print("   This is causing the login errors.")
    
    # Ask for confirmation
    print(f"\n⚠️  This will modify your database structure.")
    response = input("   Do you want to continue? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print("❌ Migration cancelled.")
        return
    
    # Create backup
    backup_database(db_path)
    
    # Add the column
    if add_profile_pic_column(db_path):
        print(f"\n🎉 Migration completed successfully!")
        print(f"   You should now be able to log in and use profile pictures.")
        
        # Final verification
        print(f"\n🔍 Final verification:")
        check_database_schema(db_path)
        
    else:
        print(f"\n❌ Migration failed!")
        print(f"   Please check the error messages above.")

if __name__ == "__main__":
    import time
    main()
