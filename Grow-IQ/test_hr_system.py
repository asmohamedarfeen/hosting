#!/usr/bin/env python3
"""
HR Dashboard System Test
========================

This script tests the complete HR dashboard workflow including:
1. Creating HR users
2. Job posting
3. Job applications
4. HR dashboard functionality
"""

import json
from database import get_db
from models import User, Job, JobApplication
from auth_utils import create_session_token
from datetime import datetime

def create_test_hr_user():
    """Create a test HR user"""
    print("🏢 Creating HR User...")
    
    db = next(get_db())
    
    # Create HR user
    hr_user = User(
        username="hr_manager",
        email="hr@company.com",
        full_name="HR Manager",
        title="Human Resources Manager",
        company="Test Company Inc",
        location="San Francisco, CA",
        bio="Experienced HR professional managing recruitment and talent acquisition.",
        user_type="domain",
        domain="company.com",
        is_verified=True,
        is_active=True
    )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == hr_user.email).first()
    if existing_user:
        print(f"✅ HR User already exists: {existing_user.email}")
        db.close()
        return existing_user
    
    db.add(hr_user)
    db.commit()
    
    print(f"✅ HR User created: {hr_user.email}")
    print(f"   Name: {hr_user.full_name}")
    print(f"   Type: {hr_user.user_type}")
    print(f"   Can manage applications: {hr_user.can_manage_applications()}")
    
    db.close()
    return hr_user

def create_test_candidates():
    """Create test candidate users"""
    print("\n👥 Creating Test Candidates...")
    
    db = next(get_db())
    
    candidates = [
        {
            "username": "john_doe",
            "email": "john.doe@email.com",
            "full_name": "John Doe",
            "title": "Software Engineer",
            "company": "Tech Startup",
            "location": "New York, NY",
            "bio": "Experienced full-stack developer with 5 years of experience.",
            "skills": json.dumps(["Python", "JavaScript", "React", "Node.js", "PostgreSQL"])
        },
        {
            "username": "jane_smith",
            "email": "jane.smith@email.com",
            "full_name": "Jane Smith",
            "title": "Product Manager",
            "company": "Digital Agency",
            "location": "Los Angeles, CA",
            "bio": "Product manager with experience in agile development and user research.",
            "skills": json.dumps(["Product Management", "Agile", "User Research", "Data Analysis"])
        },
        {
            "username": "mike_johnson",
            "email": "mike.johnson@email.com",
            "full_name": "Mike Johnson",
            "title": "UX Designer",
            "company": "Design Studio",
            "location": "Seattle, WA",
            "bio": "Creative UX designer passionate about user-centered design.",
            "skills": json.dumps(["UI/UX Design", "Figma", "Prototyping", "User Testing"])
        }
    ]
    
    created_candidates = []
    
    for candidate_data in candidates:
        # Check if candidate already exists
        existing_candidate = db.query(User).filter(User.email == candidate_data["email"]).first()
        if existing_candidate:
            print(f"✅ Candidate already exists: {existing_candidate.email}")
            created_candidates.append(existing_candidate)
            continue
        
        candidate = User(
            username=candidate_data["username"],
            email=candidate_data["email"],
            full_name=candidate_data["full_name"],
            title=candidate_data["title"],
            company=candidate_data["company"],
            location=candidate_data["location"],
            bio=candidate_data["bio"],
            skills=candidate_data["skills"],
            user_type="normal",
            is_verified=True,
            is_active=True
        )
        
        db.add(candidate)
        created_candidates.append(candidate)
        print(f"✅ Candidate created: {candidate.full_name} ({candidate.email})")
    
    db.commit()
    db.close()
    
    return created_candidates

def create_test_jobs():
    """Create test job postings"""
    print("\n💼 Creating Test Jobs...")
    
    db = next(get_db())
    
    # Get HR user
    hr_user = db.query(User).filter(User.email == "hr@company.com").first()
    if not hr_user:
        print("❌ HR user not found")
        db.close()
        return []
    
    jobs_data = [
        {
            "title": "Senior Software Engineer",
            "company": "Test Company Inc",
            "location": "San Francisco, CA",
            "job_type": "full-time",
            "salary_range": "$120,000 - $160,000",
            "description": "We are looking for a senior software engineer to join our growing team. You will be responsible for designing and implementing scalable web applications.",
            "requirements": "5+ years of experience in full-stack development, proficiency in Python and JavaScript, experience with cloud platforms."
        },
        {
            "title": "Product Manager",
            "company": "Test Company Inc",
            "location": "Remote",
            "job_type": "full-time",
            "salary_range": "$100,000 - $140,000",
            "description": "Join our product team to drive the development of innovative solutions. You will work closely with engineering and design teams.",
            "requirements": "3+ years of product management experience, strong analytical skills, experience with agile methodologies."
        },
        {
            "title": "UX Designer",
            "company": "Test Company Inc",
            "location": "Los Angeles, CA",
            "job_type": "contract",
            "salary_range": "$80,000 - $110,000",
            "description": "Create amazing user experiences for our digital products. You will be responsible for user research, wireframing, and prototyping.",
            "requirements": "3+ years of UX design experience, proficiency in Figma, experience with user research methods."
        }
    ]
    
    created_jobs = []
    
    for job_data in jobs_data:
        # Check if job already exists
        existing_job = db.query(Job).filter(
            Job.title == job_data["title"],
            Job.posted_by == hr_user.id
        ).first()
        
        if existing_job:
            print(f"✅ Job already exists: {existing_job.title}")
            created_jobs.append(existing_job)
            continue
        
        job = Job(
            title=job_data["title"],
            company=job_data["company"],
            location=job_data["location"],
            job_type=job_data["job_type"],
            salary_range=job_data["salary_range"],
            description=job_data["description"],
            requirements=job_data["requirements"],
            posted_by=hr_user.id,
            is_active=True,
            posted_at=datetime.now()
        )
        
        db.add(job)
        created_jobs.append(job)
        print(f"✅ Job created: {job.title} at {job.company}")
    
    db.commit()
    db.close()
    
    return created_jobs

def create_test_applications():
    """Create test job applications"""
    print("\n📝 Creating Test Applications...")
    
    db = next(get_db())
    
    # Get candidates and jobs
    candidates = db.query(User).filter(User.user_type == 'normal').all()
    jobs = db.query(Job).filter(Job.is_active == True).all()
    
    if not candidates or not jobs:
        print("❌ No candidates or jobs found")
        db.close()
        return []
    
    created_applications = []
    
    # Create applications for each candidate to different jobs
    for i, candidate in enumerate(candidates[:3]):  # Limit to first 3 candidates
        for j, job in enumerate(jobs):
            # Skip if already applied
            existing_app = db.query(JobApplication).filter(
                JobApplication.applicant_id == candidate.id,
                JobApplication.job_id == job.id
            ).first()
            
            if existing_app:
                print(f"✅ Application already exists: {candidate.full_name} -> {job.title}")
                created_applications.append(existing_app)
                continue
            
            # Create cover letter based on candidate and job
            cover_letter = f"Dear Hiring Manager,\n\nI am excited to apply for the {job.title} position at {job.company}. With my background in {candidate.title}, I believe I would be a great fit for this role.\n\n{candidate.bio}\n\nI look forward to discussing how I can contribute to your team.\n\nBest regards,\n{candidate.full_name}"
            
            application = JobApplication(
                job_id=job.id,
                applicant_id=candidate.id,
                cover_letter=cover_letter,
                status='pending',
                applied_at=datetime.now()
            )
            
            db.add(application)
            created_applications.append(application)
            
            # Update job application count
            job.applications_count += 1
            
            print(f"✅ Application created: {candidate.full_name} -> {job.title}")
    
    db.commit()
    db.close()
    
    return created_applications

def test_hr_permissions():
    """Test HR permissions and access control"""
    print("\n🔐 Testing HR Permissions...")
    
    db = next(get_db())
    
    # Test HR user permissions
    hr_user = db.query(User).filter(User.email == "hr@company.com").first()
    if hr_user:
        print(f"✅ HR User: {hr_user.full_name}")
        print(f"   Can post jobs: {hr_user.can_post_jobs()}")
        print(f"   Is HR user: {hr_user.is_hr_user()}")
        print(f"   Can manage applications: {hr_user.can_manage_applications()}")
    else:
        print("❌ HR user not found")
    
    # Test normal user permissions
    normal_user = db.query(User).filter(User.user_type == 'normal').first()
    if normal_user:
        print(f"✅ Normal User: {normal_user.full_name}")
        print(f"   Can post jobs: {normal_user.can_post_jobs()}")
        print(f"   Is HR user: {normal_user.is_hr_user()}")
        print(f"   Can manage applications: {normal_user.can_manage_applications()}")
    else:
        print("❌ Normal user not found")
    
    db.close()

def test_hr_dashboard_data():
    """Test HR dashboard data retrieval"""
    print("\n📊 Testing HR Dashboard Data...")
    
    db = next(get_db())
    
    # Get HR user
    hr_user = db.query(User).filter(User.email == "hr@company.com").first()
    if not hr_user:
        print("❌ HR user not found")
        db.close()
        return
    
    # Get HR user's jobs
    jobs = db.query(Job).filter(Job.posted_by == hr_user.id).all()
    print(f"✅ HR User has {len(jobs)} job postings")
    
    # Get applications for HR user's jobs
    job_ids = [job.id for job in jobs]
    if job_ids:
        applications = db.query(JobApplication).filter(
            JobApplication.job_id.in_(job_ids)
        ).all()
        print(f"✅ Total applications received: {len(applications)}")
        
        # Application statistics
        status_counts = {}
        for app in applications:
            status_counts[app.status] = status_counts.get(app.status, 0) + 1
        
        print("   Application status breakdown:")
        for status, count in status_counts.items():
            print(f"     {status.title()}: {count}")
        
        # Unique applicants
        unique_applicants = len(set(app.applicant_id for app in applications))
        print(f"✅ Unique applicants: {unique_applicants}")
    else:
        print("✅ No applications yet")
    
    db.close()

def create_hr_session():
    """Create a session for HR user testing"""
    print("\n🔑 Creating HR Session...")
    
    db = next(get_db())
    
    hr_user = db.query(User).filter(User.email == "hr@company.com").first()
    if not hr_user:
        print("❌ HR user not found")
        db.close()
        return None
    
    # Create session token
    session_token = create_session_token(hr_user.id)
    
    print(f"✅ HR session created")
    print(f"   User: {hr_user.full_name} ({hr_user.email})")
    print(f"   Session token: {session_token[:20]}...")
    print(f"   HR Dashboard URL: http://localhost:8000/hr/dashboard")
    
    db.close()
    return session_token

def main():
    """Run complete HR system test"""
    print("🚀 Starting HR Dashboard System Test")
    print("=" * 50)
    
    try:
        # Step 1: Create HR user
        hr_user = create_test_hr_user()
        
        # Step 2: Create test candidates
        candidates = create_test_candidates()
        
        # Step 3: Create test jobs
        jobs = create_test_jobs()
        
        # Step 4: Create test applications
        applications = create_test_applications()
        
        # Step 5: Test HR permissions
        test_hr_permissions()
        
        # Step 6: Test HR dashboard data
        test_hr_dashboard_data()
        
        # Step 7: Create HR session for testing
        session_token = create_hr_session()
        
        print("\n" + "=" * 50)
        print("🎉 HR Dashboard System Test Complete!")
        print("=" * 50)
        
        print("\n📋 Summary:")
        print(f"   ✅ HR User: Created/Verified")
        print(f"   ✅ Candidates: {len(candidates)} users")
        print(f"   ✅ Jobs: {len(jobs)} postings")
        print(f"   ✅ Applications: {len(applications)} submissions")
        print(f"   ✅ Session: Active HR session created")
        
        print("\n🌐 Next Steps:")
        print("   1. Start the server: uvicorn start:app --reload")
        print("   2. Open HR Dashboard: http://localhost:8000/hr/dashboard")
        print("   3. Test application management features")
        print("   4. Review candidate profiles and applications")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
