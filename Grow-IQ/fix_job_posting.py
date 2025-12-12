#!/usr/bin/env python3
"""
Job Posting Fix Script
======================

This script provides multiple solutions to fix job posting issues in Qrow IQ.
The main issue is that most users are classified as 'normal' users (with free email addresses)
and cannot post jobs, which requires 'domain' users with company emails.

Solutions provided:
1. Upgrade existing users to domain users (for testing/demo purposes)
2. Create sample domain users who can post jobs
3. Temporarily relax job posting restrictions (development mode)
4. Fix user classification for specific domains

Usage:
    python fix_job_posting.py --solution [1|2|3|4]
"""

import argparse
import sys
from database import get_db, init_database
from models import User, Job
from datetime import datetime, timedelta

def solution_1_upgrade_users():
    """Solution 1: Upgrade existing users to domain users for testing"""
    print("🔧 Solution 1: Upgrading existing users to domain users...")
    
    db = next(get_db())
    
    # Get some existing users with non-company emails
    users_to_upgrade = db.query(User).filter(
        User.user_type == 'normal',
        User.email.like('%@gmail.com')
    ).limit(5).all()
    
    if not users_to_upgrade:
        print("No users found to upgrade")
        return
    
    for user in users_to_upgrade:
        print(f"Upgrading user: {user.email}")
        
        # Change their email domain to a company domain for demo
        company_email = user.email.replace('@gmail.com', '@techcorp.com')
        user.email = company_email
        user.user_type = 'domain'
        user.domain = 'techcorp.com'
        user.company = 'Tech Corp'
        user.is_verified = True
        
        print(f"  New email: {user.email}")
        print(f"  Can post jobs: {user.can_post_jobs()}")
    
    db.commit()
    db.close()
    print("✅ Users upgraded successfully!")

def solution_2_create_sample_users():
    """Solution 2: Create sample domain users who can post jobs"""
    print("🔧 Solution 2: Creating sample domain users...")
    
    db = next(get_db())
    
    sample_companies = [
        {'domain': 'microsoft.com', 'company': 'Microsoft'},
        {'domain': 'google.com', 'company': 'Google'},
        {'domain': 'amazon.com', 'company': 'Amazon'},
        {'domain': 'apple.com', 'company': 'Apple'},
        {'domain': 'netflix.com', 'company': 'Netflix'},
    ]
    
    for i, company_info in enumerate(sample_companies, 1):
        email = f"hr{i}@{company_info['domain']}"
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User {email} already exists, skipping...")
            continue
        
        user = User(
            username=f"hr{i}_{company_info['company'].lower()}",
            email=email,
            full_name=f"HR Manager {i}",
            title="Human Resources Manager",
            company=company_info['company'],
            location="San Francisco, CA",
            bio=f"HR Manager at {company_info['company']} - Looking for talented professionals to join our team!",
            user_type='domain',
            domain=company_info['domain'],
            is_verified=True,
            is_active=True,
            password_hash="dummy_hash_for_demo"  # In real app, use proper password hashing
        )
        
        db.add(user)
        print(f"Created user: {email} (can post jobs: {user.can_post_jobs()})")
    
    db.commit()
    db.close()
    print("✅ Sample domain users created successfully!")

def solution_3_create_dev_mode():
    """Solution 3: Create a development mode toggle for job posting"""
    print("🔧 Solution 3: Creating development mode for job posting...")
    
    # Create a simple flag file for development mode
    with open('.dev_mode', 'w') as f:
        f.write('ALLOW_ALL_USERS_TO_POST_JOBS=True\n')
        f.write('DEV_MODE=True\n')
        f.write('# This file enables development mode where all users can post jobs\n')
    
    print("✅ Development mode enabled!")
    print("📝 To use this, modify the can_post_jobs() method in models.py to check for this flag")

def solution_4_fix_domain_classification():
    """Solution 4: Fix domain classification for specific domains"""
    print("🔧 Solution 4: Fixing domain classification...")
    
    db = next(get_db())
    
    # Domains that should be considered company domains but might be misclassified
    company_domains = [
        'company.com',
        'startup.io', 
        'business.org',
        'enterprise.net',
        'corp.com'
    ]
    
    updated_count = 0
    for domain in company_domains:
        users = db.query(User).filter(
            User.email.like(f'%@{domain}'),
            User.user_type == 'normal'
        ).all()
        
        for user in users:
            user.user_type = 'domain'
            user.domain = domain
            user.is_verified = True
            updated_count += 1
            print(f"Fixed user: {user.email}")
    
    db.commit()
    db.close()
    print(f"✅ Fixed {updated_count} users' domain classification!")

def create_sample_jobs():
    """Create some sample job postings for testing"""
    print("📝 Creating sample job postings...")
    
    db = next(get_db())
    
    # Get domain users who can post jobs
    domain_users = db.query(User).filter(
        User.user_type == 'domain',
        User.is_verified == True
    ).all()
    
    if not domain_users:
        print("❌ No domain users found to post jobs!")
        return
    
    sample_jobs = [
        {
            'title': 'Senior Software Engineer',
            'company': 'Tech Innovations Inc',
            'location': 'San Francisco, CA',
            'job_type': 'full-time',
            'salary_range': '$120,000 - $180,000',
            'description': 'Join our dynamic team building next-generation software solutions. You will work on scalable web applications using modern technologies.',
            'requirements': 'Bachelor\'s degree in Computer Science, 5+ years experience in Python/JavaScript, experience with cloud platforms.',
            'benefits': 'Health insurance, 401k matching, flexible work hours, remote work options, professional development budget.'
        },
        {
            'title': 'Product Manager',
            'company': 'Digital Ventures',
            'location': 'Remote',
            'job_type': 'full-time',
            'salary_range': '$100,000 - $150,000',
            'description': 'Lead product strategy and development for our flagship products. Work closely with engineering and design teams.',
            'requirements': 'MBA or equivalent experience, 3+ years in product management, experience with agile methodologies.',
            'benefits': 'Comprehensive health coverage, stock options, unlimited PTO, home office stipend.'
        },
        {
            'title': 'UX Designer',
            'company': 'Creative Solutions',
            'location': 'New York, NY',
            'job_type': 'contract',
            'salary_range': '$75 - $100/hour',
            'description': 'Design intuitive user experiences for mobile and web applications. Collaborate with product and engineering teams.',
            'requirements': 'Portfolio demonstrating UX/UI skills, proficiency in Figma/Sketch, understanding of user research methods.',
            'benefits': 'Flexible schedule, opportunity to work on diverse projects, potential for full-time conversion.'
        }
    ]
    
    for i, job_data in enumerate(sample_jobs):
        user = domain_users[i % len(domain_users)]  # Rotate through available users
        
        job = Job(
            title=job_data['title'],
            company=job_data['company'],
            location=job_data['location'],
            job_type=job_data['job_type'],
            salary_range=job_data['salary_range'],
            description=job_data['description'],
            requirements=job_data['requirements'],
            benefits=job_data['benefits'],
            application_deadline=datetime.now() + timedelta(days=30),
            posted_by=user.id,
            is_active=True
        )
        
        db.add(job)
        print(f"Created job: {job_data['title']} posted by {user.email}")
    
    db.commit()
    db.close()
    print("✅ Sample jobs created successfully!")

def show_status():
    """Show current status of users and jobs"""
    print("\n📊 Current Status:")
    print("=" * 50)
    
    db = next(get_db())
    
    # User statistics
    total_users = db.query(User).count()
    domain_users = db.query(User).filter(User.user_type == 'domain').count()
    verified_users = db.query(User).filter(User.is_verified == True).count()
    can_post = db.query(User).filter(User.user_type == 'domain', User.is_verified == True).count()
    
    print(f"👥 Users:")
    print(f"   Total: {total_users}")
    print(f"   Domain users: {domain_users}")
    print(f"   Verified: {verified_users}")
    print(f"   Can post jobs: {can_post}")
    
    # Job statistics
    total_jobs = db.query(Job).count()
    active_jobs = db.query(Job).filter(Job.is_active == True).count()
    
    print(f"\n💼 Jobs:")
    print(f"   Total: {total_jobs}")
    print(f"   Active: {active_jobs}")
    
    # Recent domain users
    print(f"\n👨‍💼 Domain Users (who can post jobs):")
    domain_users_list = db.query(User).filter(
        User.user_type == 'domain',
        User.is_verified == True
    ).limit(5).all()
    
    for user in domain_users_list:
        print(f"   📧 {user.email} ({user.company}) - {user.full_name}")
    
    db.close()

def main():
    parser = argparse.ArgumentParser(description='Fix Job Posting Issues')
    parser.add_argument('--solution', type=int, choices=[1,2,3,4], 
                       help='Choose solution: 1=Upgrade users, 2=Create sample users, 3=Dev mode, 4=Fix domains')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--create-jobs', action='store_true', help='Create sample jobs')
    parser.add_argument('--all', action='store_true', help='Run all solutions')
    
    args = parser.parse_args()
    
    # Initialize database
    init_database()
    
    if args.status:
        show_status()
        return
    
    if args.create_jobs:
        create_sample_jobs()
        return
    
    if args.all:
        print("🚀 Running all solutions...")
        solution_2_create_sample_users()
        solution_4_fix_domain_classification()
        create_sample_jobs()
        show_status()
        return
    
    if args.solution == 1:
        solution_1_upgrade_users()
    elif args.solution == 2:
        solution_2_create_sample_users()
    elif args.solution == 3:
        solution_3_create_dev_mode()
    elif args.solution == 4:
        solution_4_fix_domain_classification()
    else:
        print("🤔 Usage examples:")
        print("  python fix_job_posting.py --status          # Show current status")
        print("  python fix_job_posting.py --solution 2      # Create sample domain users")
        print("  python fix_job_posting.py --create-jobs     # Create sample jobs")
        print("  python fix_job_posting.py --all             # Run all solutions")
        print("\nSolutions:")
        print("  1: Upgrade existing users to domain users")
        print("  2: Create new sample domain users")
        print("  3: Enable development mode")
        print("  4: Fix domain classification")

if __name__ == '__main__':
    main()
