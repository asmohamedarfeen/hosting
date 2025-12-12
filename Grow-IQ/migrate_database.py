#!/usr/bin/env python3
"""
Database migration script to add missing columns for the updated connection system.
This script will add the updated_at columns to the connections and friend_requests tables.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate the database to add new messaging fields"""
    db_path = "dashboard.db"
    
    if not os.path.exists(db_path):
        print("Database not found. Please run the application first to create it.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting database migration for LinkedIn-style messaging...")
    
    try:
        # Check if new fields already exist
        cursor.execute("PRAGMA table_info(messages)")
        message_columns = [column[1] for column in cursor.fetchall()]
        
        cursor.execute("PRAGMA table_info(conversations)")
        conversation_columns = [column[1] for column in cursor.fetchall()]
        
        # Add new fields to messages table
        new_message_fields = [
            ("file_name", "TEXT"),
            ("file_size", "INTEGER"),
            ("file_type", "TEXT"),
            ("is_edited", "BOOLEAN DEFAULT 0"),
            ("edited_at", "DATETIME"),
            ("parent_message_id", "INTEGER"),
            ("reactions", "TEXT DEFAULT '{}'")
        ]
        
        for field_name, field_type in new_message_fields:
            if field_name not in message_columns:
                print(f"Adding {field_name} to messages table...")
                cursor.execute(f"ALTER TABLE messages ADD COLUMN {field_name} {field_type}")
                print(f"✓ Added {field_name}")
            else:
                print(f"✓ {field_name} already exists")
        
        # Add new fields to conversations table
        new_conversation_fields = [
            ("last_message_content", "TEXT"),
            ("last_message_sender_id", "INTEGER"),
            ("updated_at", "DATETIME"),
            ("is_archived_user1", "BOOLEAN DEFAULT 0"),
            ("is_archived_user2", "BOOLEAN DEFAULT 0"),
            ("is_muted_user1", "BOOLEAN DEFAULT 0"),
            ("is_muted_user2", "BOOLEAN DEFAULT 0")
        ]
        
        for field_name, field_type in new_conversation_fields:
            if field_name not in conversation_columns:
                print(f"Adding {field_name} to conversations table...")
                cursor.execute(f"ALTER TABLE conversations ADD COLUMN {field_name} {field_type}")
                print(f"✓ Added {field_name}")
            else:
                print(f"✓ {field_name} already exists")
        
        # Update existing conversations with default values
        print("Updating existing conversations...")
        cursor.execute("""
            UPDATE conversations 
            SET last_message_content = 'Start a conversation!',
                last_message_sender_id = user1_id,
                updated_at = created_at
            WHERE last_message_content IS NULL
        """)
        
        # Create messages upload directory
        messages_upload_dir = "static/uploads/messages"
        if not os.path.exists(messages_upload_dir):
            os.makedirs(messages_upload_dir)
            print(f"✓ Created messages upload directory: {messages_upload_dir}")
        
        # Commit changes
        conn.commit()
        print("\n✓ Database migration completed successfully!")
        
        # Show current table structure
        print("\nCurrent messages table structure:")
        cursor.execute("PRAGMA table_info(messages)")
        for column in cursor.fetchall():
            print(f"  {column[1]} ({column[2]})")
        
        print("\nCurrent conversations table structure:")
        cursor.execute("PRAGMA table_info(conversations)")
        for column in cursor.fetchall():
            print(f"  {column[1]} ({column[2]})")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
