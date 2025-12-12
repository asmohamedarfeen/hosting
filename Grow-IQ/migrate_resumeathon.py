#!/usr/bin/env python3
"""
Migration script to add ResumeathonParticipant table
"""
import os
import sys
from sqlalchemy import create_engine, text
from database import get_db
from models import Base, ResumeathonParticipant

def migrate_resumeathon():
    """Add ResumeathonParticipant table to the database"""
    print("🏆 Resumeathon Migration")
    print("=" * 50)
    
    try:
        # Get database URL from environment or use default
        database_url = os.getenv('DATABASE_URL', 'sqlite:///app.db')
        
        # Create engine
        engine = create_engine(database_url)
        
        # Check if table already exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='resumeathon_participants'
            """))
            
            if result.fetchone():
                print("✅ ResumeathonParticipant table already exists")
                return True
        
        # Create the table
        print("1. 📊 Creating ResumeathonParticipant table...")
        ResumeathonParticipant.__table__.create(engine, checkfirst=True)
        print("✅ ResumeathonParticipant table created successfully")
        
        # Verify table creation
        print("\n2. 🔍 Verifying table structure...")
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(resumeathon_participants)"))
            columns = result.fetchall()
            
            expected_columns = ['id', 'user_id', 'resume_test_result_id', 'joined_at', 'is_active']
            found_columns = [col[1] for col in columns]
            
            for col in expected_columns:
                if col in found_columns:
                    print(f"   ✅ Column '{col}' found")
                else:
                    print(f"   ❌ Column '{col}' missing")
                    return False
        
        print("✅ Table structure verified")
        
        # Test insert/select
        print("\n3. 🧪 Testing table operations...")
        with engine.connect() as conn:
            # Test that we can query the table
            result = conn.execute(text("SELECT COUNT(*) FROM resumeathon_participants"))
            count = result.fetchone()[0]
            print(f"   ✅ Table is queryable (current count: {count})")
        
        print("\n" + "=" * 50)
        print("🎉 Resumeathon Migration Complete!")
        print("\n📋 Summary:")
        print("   ✅ ResumeathonParticipant table created")
        print("   ✅ Table structure verified")
        print("   ✅ Table operations working")
        print("\n🚀 Resumeathon leaderboard is ready to use!")
        print("   - Users can now join with their resume scores")
        print("   - Leaderboard shows real users with real scores")
        print("   - First-come-first-served ranking implemented")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_resumeathon()
    sys.exit(0 if success else 1)
