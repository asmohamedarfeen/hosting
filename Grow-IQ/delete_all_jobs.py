#!/usr/bin/env python3
"""
Script to delete all existing jobs from the database.
This will also delete all related job applications due to cascade delete.
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_enhanced import get_db, init_database
from models import Job, JobApplication
from sqlalchemy.orm import Session

def delete_all_jobs():
    """Delete all jobs and related applications from the database"""
    try:
        # Initialize database
        init_database()
        
        # Get database session
        db: Session = next(get_db())
        
        try:
            # Count jobs before deletion
            job_count = db.query(Job).count()
            application_count = db.query(JobApplication).count()
            
            print(f"Found {job_count} jobs and {application_count} job applications in the database.")
            
            if job_count == 0:
                print("No jobs to delete. Database is already clean.")
                return
            
            # Confirm deletion
            print(f"\n⚠️  WARNING: This will delete ALL {job_count} jobs and {application_count} applications!")
            response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
            
            if response != 'yes':
                print("Deletion cancelled.")
                return
            
            # Delete all job applications first (though cascade should handle this)
            deleted_applications = db.query(JobApplication).delete()
            print(f"Deleted {deleted_applications} job applications.")
            
            # Delete all jobs
            deleted_jobs = db.query(Job).delete()
            print(f"Deleted {deleted_jobs} jobs.")
            
            # Commit the changes
            db.commit()
            
            print(f"\n✅ Successfully deleted all jobs and applications!")
            print(f"   - Jobs deleted: {deleted_jobs}")
            print(f"   - Applications deleted: {deleted_applications}")
            print("\nThe database is now clean. Only newly added jobs will be shown.")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error deleting jobs: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    delete_all_jobs()

