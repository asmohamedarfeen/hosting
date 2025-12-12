#!/usr/bin/env python3
"""
Simple script to check jobs in the database
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database_enhanced import get_db
    from models import Job, JobApplication, User
    
    print("✅ Successfully imported database modules")
    
    # Get database session
    db = next(get_db())
    
    # Check jobs
    jobs = db.query(Job).all()
    print(f"\n📋 Jobs in database: {len(jobs)}")
    
    for job in jobs:
        print(f"  - ID: {job.id}, Title: {job.title}, Company: {job.company}, Active: {job.is_active}")
    
    # Check job applications
    applications = db.query(JobApplication).all()
    print(f"\n📝 Job applications in database: {len(applications)}")
    
    for app in applications:
        print(f"  - ID: {app.id}, Job ID: {app.job_id}, Applicant ID: {app.applicant_id}, Status: {app.status}")
    
    # Check users
    users = db.query(User).limit(5).all()
    print(f"\n👥 Users in database (first 5): {len(users)}")
    
    for user in users:
        print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}")
    
    db.close()
    print("\n✅ Database check completed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
