import os
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Query, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
import re
from database_enhanced import get_db
from models import User, Job, JobApplication
from auth_utils import get_current_user, get_user_from_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(tags=["Jobs"])

# Get templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ==================== TEST ROUTE ====================

@router.get("/debug/test", response_class=HTMLResponse)
async def test_route(request: Request):
    """Simple test route to check if routing is working"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head><title>Test Route</title></head>
    <body>
        <h1>Test Route Working!</h1>
        <p>If you can see this, the job routes are working correctly.</p>
        <a href="/home">Back to Home</a>
    </body>
    </html>
    """)

# ==================== JOB POSTING (Domain Users Only) ====================

@router.get("/jobs/post", response_class=HTMLResponse)
async def job_posting_page(request: Request, db: Session = Depends(get_db)):
    """Display job posting form (domain users only)"""
    try:
        # Check if user is authenticated
        session_token = request.cookies.get("session_token")
        if not session_token:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        session_data = get_user_from_session(session_token, db)
        if not session_data:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        # Get user from database
        current_user = db.query(User).filter(User.id == session_data['user_id']).first()
        if not current_user:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        # Check if user can post jobs
        if not current_user.can_post_jobs():
            return templates.TemplateResponse("job_posting.html", {
                "request": request,
                "error": "Only verified domain users can post jobs. Please use a company email address."
            })
        
        return templates.TemplateResponse("job_posting.html", {
            "request": request,
            "user": current_user
        })
        
    except Exception as e:
        logger.error(f"Error accessing job posting page: {e}")
        return RedirectResponse(url="/auth/login", status_code=302)

@router.get("/jobs/hr-demo", response_class=HTMLResponse)
async def hr_demo_page(request: Request):
    """Display HR demo page showing company features"""
    return templates.TemplateResponse("hr_demo.html", {"request": request})

@router.post("/jobs/create")
async def create_job(
    request: Request,
    title: str = Form(...),
    company: str = Form(...),
    location: str = Form(...),
    job_type: str = Form(...),
    salary_range: str = Form(...),
    description: str = Form(...),
    requirements: str = Form(...),
    benefits: str = Form(...),
    required_skills: str = Form("") ,
    application_deadline: str = Form(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Job creation request received: {title} at {company}")
    logger.info(f"Form data: title={title}, company={company}, location={location}, job_type={job_type}")
    try:
        # Get current user from session
        session_token = request.cookies.get("session_token")
        logger.info(f"Session token from cookies: {session_token[:20] if session_token else 'None'}...")
        
        if not session_token:
            raise HTTPException(status_code=401, detail="Please log in.")
        
        session_data = get_user_from_session(session_token, db)
        logger.info(f"Session data: {session_data}")
        
        if not session_data:
            raise HTTPException(status_code=401, detail="Not authenticated. Please log in again.")
        
        # Get user from database
        current_user = db.query(User).filter(User.id == session_data['user_id']).first()
        logger.info(f"Current user: {current_user.username if current_user else 'None'}, user_type: {current_user.user_type if current_user else 'None'}, is_verified: {current_user.is_verified if current_user else 'None'}")
        
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found.")
        
        # Check if user can post jobs
        can_post = current_user.can_post_jobs()
        logger.info(f"Can post jobs: {can_post}")
        
        if not can_post:
            # Provide more helpful error message based on user status
            if current_user.user_type == 'normal':
                detail = "Only verified company users can post jobs. Please contact support to upgrade your account or use a company email address."
            elif current_user.user_type == 'domain' and not current_user.is_verified:
                detail = "Your company email needs to be verified before you can post jobs. Please check your email for verification instructions."
            else:
                detail = "Only verified domain users can post jobs. Please use a company email address."
            
            raise HTTPException(status_code=403, detail=detail)
        
        # Parse application deadline
        try:
            deadline = datetime.fromisoformat(application_deadline.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid deadline format")
        
        # Normalize required skills (comma/line separated)
        skills_section = ""
        if required_skills:
            try:
                # Split by commas or newlines, trim
                import re as _re
                skills_list = [_s.strip() for _s in _re.split(r"[,\n;]+", required_skills) if _s.strip()]
                if skills_list:
                    skills_section = "\n[SKILLS] " + ", ".join(skills_list)
            except Exception:
                skills_section = "\n[SKILLS] " + required_skills.strip()

        # Create job (embed skills in requirements for recommendation engine)
        job = Job(
            title=title,
            company=company,
            location=location,
            job_type=job_type,
            salary_range=salary_range,
            description=description,
            requirements=(requirements or "") + skills_section,
            benefits=benefits,
            application_deadline=deadline,
            posted_by=current_user.id,
            posted_at=datetime.now(),
            is_active=True
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        logger.info(f"Job '{title}' posted successfully by user {current_user.username}")
        
        return JSONResponse({
            "message": "Job posted successfully!", 
            "job_id": job.id, 
            "status": "success"
        })
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating job: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception details: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating job: {str(e)}")

@router.get("/jobs", response_class=HTMLResponse)
async def jobs_listing_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Display active jobs. If the user has profile skills, show only matching jobs."""
    try:
        # Load active jobs (limit to recent for performance)
        jobs = db.query(Job).filter(Job.is_active == True).order_by(Job.posted_at.desc()).limit(300).all()

        # Get current user from session
        session_token = request.cookies.get("session_token")
        current_user = None
        if session_token:
            session_data = get_user_from_session(session_token, db)
            if session_data:
                current_user = db.query(User).filter(User.id == session_data['user_id']).first()

        # If user has skills, filter jobs by overlap - ONLY show matching jobs
        if current_user and current_user.skills:
            user_tokens = _parse_user_skills(current_user.skills)
            # Also include title and industry for better matching
            if current_user.title:
                user_tokens |= _normalize_tokens(current_user.title)
            if current_user.industry:
                user_tokens |= _normalize_tokens(current_user.industry)
            
            if user_tokens:
                logger.info(f"Filtering jobs for user {current_user.email} with {len(user_tokens)} skill tokens")
                filtered = []
                for j in jobs:
                    jt = _job_token_set(j)
                    # Only include jobs where at least one skill matches
                    if user_tokens.intersection(jt):
                        filtered.append(j)
                logger.info(f"Found {len(filtered)} matching jobs out of {len(jobs)} total jobs")
                # Only show matching jobs - no fallback to all jobs
                jobs = filtered

        return templates.TemplateResponse("jobs.html", {
            "request": request,
            "jobs": jobs,
            "current_user": current_user
        })

    except Exception as e:
        logger.error(f"Jobs listing error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while loading jobs"
        )

@router.get("/jobs/search")
async def search_jobs(
    request: Request,
    query: Optional[str] = Query(None, description="Search term"),
    location: Optional[str] = Query(None, description="Filter by location"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    db: Session = Depends(get_db)
):
    """Search for jobs by title, company, or description"""
    try:
        search_query = db.query(Job).filter(Job.is_active == True)
        
        if query:
            search_terms = query.split()
            for term in search_terms:
                search_query = search_query.filter(
                    (Job.title.ilike(f'%{term}%')) |
                    (Job.company.ilike(f'%{term}%')) |
                    (Job.description.ilike(f'%{term}%'))
                )
        
        if location:
            search_query = search_query.filter(Job.location.ilike(f'%{location}%'))
            
        if job_type:
            search_query = search_query.filter(Job.job_type == job_type)
        
        jobs = search_query.order_by(Job.posted_at.desc()).limit(20).all()
        
        # Get poster information for each job
        jobs_data = []
        for job in jobs:
            posted_by = db.query(User).get(job.posted_by)
            jobs_data.append({
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "job_type": job.job_type,
                "salary_range": job.salary_range,
                "description": job.description,
                "posted_at": job.posted_at,
                "posted_by": posted_by.full_name if posted_by else "Unknown",
                "application_deadline": job.application_deadline
            })
        
        return {"jobs": jobs_data, "total": len(jobs_data)}
        
    except Exception as e:
        logging.error(f"Error searching jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")

# ==================== JOB RECOMMENDATIONS ====================

def _normalize_tokens(text: str) -> set:
    """Normalize text into tokens for skill matching"""
    if not text:
        return set()
    text = text.lower()
    # Split on non-alphanumeric characters, keep +, #, . for technologies like C++, C#, etc.
    tokens = re.split(r"[^a-z0-9+.#]+", text)
    stop = {
        "the","a","an","and","or","of","for","to","in","on","with","at","by","from",
        "is","are","be","this","that","as","it","your","you","we","our","their","they",
        "job","role","position","responsibilities","requirements","skills","preferred","must",
        "will","have","has","about","what","who","how","years","year","experience","exp"
    }
    # Filter out stop words and very short tokens (less than 2 chars)
    normalized = {t for t in tokens if t and len(t) >= 2 and t not in stop}
    return normalized

def _parse_user_skills(skills_field: Optional[str]) -> set:
    if not skills_field:
        return set()
    # Try JSON first
    try:
        import json
        data = json.loads(skills_field)
        if isinstance(data, list):
            items = [s for s in data if isinstance(s, str)]
            return _normalize_tokens(",".join(items))
        if isinstance(data, dict):
            keys = [k for k, v in data.items() if v]
            return _normalize_tokens(",".join(keys))
    except Exception:
        pass
    # Fallback: comma/semicolon/newline separated string
    parts = re.split(r"[,;\n]+", skills_field)
    return _normalize_tokens(",".join([p.strip() for p in parts if p.strip()]))

def _job_token_set(job: Job) -> set:
    parts: List[str] = []
    if job.title:
        parts.append(job.title)
    if job.description:
        parts.append(job.description)
    if job.requirements:
        parts.append(job.requirements)
    if job.location:
        parts.append(job.location)
    if job.job_type:
        parts.append(job.job_type)
    return _normalize_tokens("\n".join(parts))

def _score_job(user_tokens: set, job_tokens: set) -> float:
    if not user_tokens or not job_tokens:
        return 0.0
    overlap = user_tokens.intersection(job_tokens)
    # Weighted score: precision and recall style harmonic mean to favor overlap without huge bias
    precision = len(overlap) / max(len(job_tokens), 1)
    recall = len(overlap) / max(len(user_tokens), 1)
    if precision + recall == 0:
        return 0.0
    f1 = 2 * precision * recall / (precision + recall)
    # Small bonus for exact skill string hits inside requirements/description length
    return f1

@router.get("/api/jobs/recommendations")
async def recommend_jobs(
    limit: int = Query(10, ge=1, le=50, description="Number of jobs to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Recommend jobs based on the current user's skills (from profile)."""
    try:
        # Parse user skills tokens
        user_tokens = _parse_user_skills(current_user.skills)

        # If no skills, just return latest active jobs
        base_query = db.query(Job).filter(Job.is_active == True)
        jobs: List[Job] = base_query.order_by(Job.posted_at.desc()).limit(200).all()

        if not user_tokens:
            jobs_simple = [
                {
                    "id": j.id,
                    "title": j.title,
                    "company": j.company,
                    "location": j.location,
                    "job_type": j.job_type,
                    "posted_at": j.posted_at.isoformat() if j.posted_at else None,
                    "score": 0.0
                }
                for j in jobs[:limit]
            ]
            return {"jobs": jobs_simple, "total": len(jobs_simple)}

        # Score jobs by overlap
        scored: List[Tuple[float, Job]] = []
        for job in jobs:
            jt = _job_token_set(job)
            score = _score_job(user_tokens, jt)
            if score > 0:
                scored.append((score, job))

        # Fallback to recent jobs if no matches
        if not scored:
            jobs_simple = [
                {
                    "id": j.id,
                    "title": j.title,
                    "company": j.company,
                    "location": j.location,
                    "job_type": j.job_type,
                    "posted_at": j.posted_at.isoformat() if j.posted_at else None,
                    "score": 0.0
                }
                for j in jobs[:limit]
            ]
            return {"jobs": jobs_simple, "total": len(jobs_simple)}

        # Sort and trim
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:limit]
        results = []
        for score, j in top:
            results.append({
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "job_type": j.job_type,
                "salary_range": j.salary_range,
                "description": j.description,
                "posted_at": j.posted_at.isoformat() if j.posted_at else None,
                "score": round(float(score), 4)
            })

        return {"jobs": results, "total": len(results)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

# ==================== JOB APPLICATIONS ====================

@router.post("/jobs/apply", response_class=JSONResponse)
async def apply_for_job(
    request: Request,
    db: Session = Depends(get_db)
):
    """Users can apply for jobs - handles both form data and JSON requests"""
    try:
        # Determine content type and parse data accordingly
        content_type = request.headers.get("content-type", "").lower()
        
        if "application/json" in content_type:
            # Handle JSON request
            try:
                json_data = await request.json()
                job_id = json_data.get("job_id")
                cover_letter = json_data.get("cover_letter", "")
                resume_path = json_data.get("resume_path", "")
            except Exception as e:
                logger.error(f"Error parsing JSON: {e}")
                raise HTTPException(status_code=400, detail="Invalid JSON format")
        else:
            # Handle form data (multipart/form-data or application/x-www-form-urlencoded)
            try:
                form_data = await request.form()
                job_id = form_data.get("job_id")
                cover_letter = form_data.get("cover_letter", "")
                resume_path = form_data.get("resume_path", "")
            except Exception as e:
                logger.error(f"Error parsing form data: {e}")
                raise HTTPException(status_code=400, detail="Invalid form data")
        
        # Validate required fields
        if not job_id:
            raise HTTPException(status_code=400, detail="Job ID is required")
        
        # Convert job_id to integer
        try:
            job_id = int(job_id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Job ID must be a valid integer")
        
        # Get current user from session
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(status_code=401, detail="Please log in.")
        
        session_data = get_user_from_session(session_token, db)
        if not session_data:
            raise HTTPException(status_code=401, detail="Not authenticated.")
        
        current_user = db.query(User).filter(User.id == session_data['user_id']).first()
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if job exists and is active
        job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found or not active")
        
        # Check if user has already applied for this job
        existing_application = db.query(JobApplication).filter(
            JobApplication.job_id == job_id,
            JobApplication.applicant_id == current_user.id
        ).first()
        
        if existing_application:
            raise HTTPException(status_code=400, detail="You have already applied for this job")
        
        # Create new job application
        new_application = JobApplication(
            job_id=job_id,
            applicant_id=current_user.id,
            cover_letter=cover_letter or "",
            resume_path=resume_path or "",
            status='pending',
            applied_at=datetime.now()
        )
        
        db.add(new_application)
        
        # Update job applications count
        job.applications_count = (job.applications_count or 0) + 1
        
        db.commit()
        db.refresh(new_application)
        
        logger.info(f"New job application submitted by {current_user.email} for job {job_id} (Application ID: {new_application.id})")
        
        return {
            "success": True,
            "message": "Application submitted successfully",
            "application_id": new_application.id,
            "job_id": job_id,
            "job_title": job.title,
            "company": job.company
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting job application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting application: {str(e)}")

@router.get("/jobs/{job_id}", response_class=HTMLResponse)
async def job_detail_page(
    request: Request,
    job_id: int,
    db: Session = Depends(get_db)
):
    """Display job details page"""
    try:
        job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get poster information
        poster = db.query(User).get(job.posted_by)
        
        return templates.TemplateResponse("job_detail.html", {
            "request": request,
            "job": job,
            "poster": poster
        })
        
    except Exception as e:
        logger.error(f"Job detail error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while loading job details"
        )



@router.delete("/jobs/{job_id}")
async def delete_job(
    request: Request,
    job_id: int,
    db: Session = Depends(get_db)
):
    """Delete a job (only the poster can delete)"""
    try:
        # Get current user from session
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(status_code=401, detail="Please log in.")
        
        session_data = get_user_from_session(session_token, db)
        if not session_data:
            raise HTTPException(status_code=401, detail="Not authenticated. Please log in again.")
        
        # Get user from database
        current_user = db.query(User).filter(User.id == session_data['user_id']).first()
        if not current_user:
            raise HTTPException(status_code=401, detail="User not found.")
        
        # Check if job exists
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if user is the poster
        if job.posted_by != current_user.id:
            raise HTTPException(status_code=403, detail="Only the job poster can delete this job")
        
        # Soft delete by setting is_active to False
        job.is_active = False
        db.commit()
        
        logger.info(f"Job '{job.title}' deleted by user {current_user.username}")
        
        return {"message": "Job deleted successfully!", "status": "success"}
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error deleting job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting job: {str(e)}")

# ==================== ADMIN/DEV FEATURES ====================

@router.post("/admin/enable-dev-mode")
async def enable_dev_mode():
    """Enable development mode to allow all users to post jobs"""
    try:
        # Create the .dev_mode file
        with open('.dev_mode', 'w') as f:
            f.write('ALLOW_ALL_USERS_TO_POST_JOBS=True\n')
            f.write('DEV_MODE=True\n')
            f.write('# This file enables development mode where all users can post jobs\n')
        
        logger.info("Development mode enabled - all users can now post jobs")
        
        return {
            "message": "Development mode enabled successfully! All users can now post jobs.",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error enabling dev mode: {e}")
        raise HTTPException(status_code=500, detail=f"Error enabling dev mode: {str(e)}")

@router.get("/admin/job-stats")
async def get_job_stats(db: Session = Depends(get_db)):
    """Get job posting statistics for debugging"""
    try:
        total_jobs = db.query(Job).count()
        active_jobs = db.query(Job).filter(Job.is_active == True).count()
        total_users = db.query(User).count()
        domain_users = db.query(User).filter(User.user_type == 'domain').count()
        verified_users = db.query(User).filter(User.is_verified == True).count()
        can_post_jobs = db.query(User).filter(User.user_type == 'domain', User.is_verified == True).count()
        
        import os
        dev_mode_enabled = os.path.exists('.dev_mode')
        
        # Session info
        from auth_utils import user_sessions
        active_sessions = len(user_sessions)
        
        return {
            "jobs": {
                "total": total_jobs,
                "active": active_jobs
            },
            "users": {
                "total": total_users,
                "domain": domain_users,
                "verified": verified_users,
                "can_post_jobs": can_post_jobs
            },
            "sessions": {
                "active": active_sessions
            },
            "dev_mode_enabled": dev_mode_enabled,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error getting job stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting job stats: {str(e)}")

@router.post("/admin/create-debug-session")
async def create_debug_session(response: Response, db: Session = Depends(get_db)):
    """Create a debug session for testing (development only)"""
    try:
        import os
        if not os.path.exists('.dev_mode'):
            raise HTTPException(status_code=403, detail="Debug features only available in development mode")
        
        # Get first user
        user = db.query(User).first()
        if not user:
            raise HTTPException(status_code=404, detail="No users found")
        
        # Create session
        from auth_utils import create_session_token
        session_token = create_session_token(user.id)
        
        # Set cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=86400,  # 1 day
            httponly=True,
            secure=False,
            samesite="lax"
        )
        
        logger.info(f"Debug session created for user {user.email}")
        
        return {
            "message": f"Debug session created for user {user.email}",
            "user_id": user.id,
            "session_token": session_token[:20] + "...",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error creating debug session: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating debug session: {str(e)}")

# ==================== JOB SEARCH API ====================

@router.get("/api/jobs/search")
async def search_jobs(
    request: Request,
    q: Optional[str] = Query(None, description="Search query"),
    location: Optional[str] = Query(None, description="Location filter"),
    job_type: Optional[str] = Query(None, description="Job type filter"),
    db: Session = Depends(get_db)
):
    """Search jobs with filters, personalized by user skills"""
    try:
        from auth_utils import get_user_from_session
        
        query = db.query(Job).filter(Job.is_active == True)
        
        # Apply search filters
        if q:
            search_term = f"%{q}%"
            query = query.filter(
                (Job.title.ilike(search_term)) |
                (Job.company.ilike(search_term)) |
                (Job.description.ilike(search_term))
            )
        
        if location:
            location_term = f"%{location}%"
            query = query.filter(Job.location.ilike(location_term))
        
        if job_type:
            query = query.filter(Job.job_type == job_type)
        
        # Get all matching jobs
        jobs = query.order_by(Job.posted_at.desc()).all()
        
        # Get current user and their skills for personalization
        current_user = None
        user_skill_tokens = set()
        
        session_token = request.cookies.get("session_token")
        if session_token:
            try:
                session_data = get_user_from_session(session_token, db)
                if session_data and session_data.get("user_id"):
                    current_user = db.query(User).filter(User.id == session_data['user_id']).first()
                    if current_user and current_user.skills:
                        # Parse user skills
                        user_skill_tokens = _parse_user_skills(current_user.skills)
                        # Also include title and industry for better matching
                        if current_user.title:
                            user_skill_tokens |= _normalize_tokens(current_user.title)
                        if current_user.industry:
                            user_skill_tokens |= _normalize_tokens(current_user.industry)
            except Exception as e:
                logger.debug(f"Could not get user for personalization: {e}")
        
        # Score and rank jobs based on user skills if available
        if user_skill_tokens:
            logger.info(f"User has {len(user_skill_tokens)} skill tokens. Filtering jobs to show only matching ones.")
            scored_jobs = []
            for job in jobs:
                job_tokens = _job_token_set(job)
                # Check if there's at least one skill match (intersection)
                overlap = user_skill_tokens.intersection(job_tokens)
                if overlap:
                    match_score = _score_job(user_skill_tokens, job_tokens)
                    # Only include jobs with at least one matching skill (score > 0)
                    if match_score > 0:
                        scored_jobs.append((match_score, job))
                        logger.debug(f"Job '{job.title}' matches with skills: {overlap} (score: {match_score:.4f})")
            
            logger.info(f"Found {len(scored_jobs)} jobs matching user skills out of {len(jobs)} total jobs")
            
            # Sort by match score (descending), then by posted_at (descending)
            scored_jobs.sort(key=lambda x: (x[0], x[1].posted_at or datetime.min), reverse=True)
            
            # Convert to dict with match scores - only jobs with matching skills
            job_list = []
            for score, job in scored_jobs:
                job_dict = {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "job_type": job.job_type,
                    "salary_range": job.salary_range,
                    "description": job.description,
                    "posted_at": job.posted_at.isoformat() if job.posted_at else None,
                    "is_active": job.is_active,
                    "match_score": round(score, 4)  # Add match score for frontend display
                }
                job_list.append(job_dict)
        else:
            # No user skills, return jobs ordered by recency
            # Note: If user is not authenticated or has no skills, show all jobs
            job_list = []
            for job in jobs:
                job_dict = {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "job_type": job.job_type,
                    "salary_range": job.salary_range,
                    "description": job.description,
                    "posted_at": job.posted_at.isoformat() if job.posted_at else None,
                    "is_active": job.is_active,
                    "match_score": 0.0  # No match score for unauthenticated users
                }
                job_list.append(job_dict)
        
        return {"jobs": job_list, "total": len(job_list)}
        
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")

# ==================== HR JOB MANAGEMENT API ====================

@router.get("/api/hr/jobs")
async def get_hr_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get jobs posted by the current HR user"""
    try:
        # Check if user is HR/domain user
        if current_user.user_type not in ['domain', 'hr', 'hr_user']:
            raise HTTPException(status_code=403, detail="Access denied. HR privileges required.")
        
        jobs = db.query(Job).filter(
            Job.posted_by == current_user.id,
            Job.is_active == True
        ).order_by(Job.posted_at.desc()).all()
        
        job_list = []
        for job in jobs:
            job_dict = {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "job_type": job.job_type,
                "salary_range": job.salary_range,
                "description": job.description,
                "requirements": job.requirements,
                "benefits": job.benefits,
                "application_deadline": job.application_deadline.isoformat() if job.application_deadline else None,
                "posted_at": job.posted_at.isoformat() if job.posted_at else None,
                "is_active": job.is_active
            }
            job_list.append(job_dict)
        
        return {"jobs": job_list, "total": len(job_list)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting HR jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving jobs: {str(e)}")

@router.post("/api/hr/jobs/create")
async def create_hr_job(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job posting (HR only)"""
    try:
        # Check if user is HR/domain user
        if current_user.user_type not in ['domain', 'hr', 'hr_user']:
            raise HTTPException(status_code=403, detail="Access denied. HR privileges required.")
        
        form_data = await request.form()
        
        # Extract form data
        title = form_data.get("title", "").strip()
        company = form_data.get("company", "").strip()
        location = form_data.get("location", "").strip()
        job_type = form_data.get("job_type", "full-time").strip()
        salary_range = form_data.get("salary_range", "").strip()
        description = form_data.get("description", "").strip()
        requirements = form_data.get("requirements", "").strip()
        benefits = form_data.get("benefits", "").strip()
        application_deadline_str = form_data.get("application_deadline", "").strip()
        
        # Validation
        if not all([title, company, location, description]):
            raise HTTPException(
                status_code=400,
                detail="Title, company, location, and description are required"
            )
        
        # Parse application deadline
        application_deadline = None
        if application_deadline_str:
            try:
                application_deadline = datetime.fromisoformat(application_deadline_str)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid application deadline format"
                )
        
        # Create job
        job = Job(
            title=title,
            company=company,
            location=location,
            job_type=job_type,
            salary_range=salary_range,
            description=description,
            requirements=requirements,
            benefits=benefits,
            application_deadline=application_deadline,
            posted_by=current_user.id,
            is_active=True,
            posted_at=datetime.now()
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        return {
            "message": "Job created successfully",
            "job_id": job.id,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating HR job: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating job: {str(e)}")

@router.get("/api/hr/applications")
async def get_hr_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get applications for jobs posted by the current HR user"""
    try:
        # Check if user is HR/domain user
        if current_user.user_type not in ['domain', 'hr', 'hr_user']:
            raise HTTPException(status_code=403, detail="Access denied. HR privileges required.")
        
        # Get applications for jobs posted by this HR user
        applications = db.query(JobApplication).join(Job).filter(
            Job.posted_by == current_user.id
        ).order_by(JobApplication.applied_at.desc()).all()
        
        application_list = []
        for app in applications:
            app_dict = {
                "id": app.id,
                "job_id": app.job_id,
                "applicant_id": app.applicant_id,
                "applicant_name": app.applicant.full_name,
                "applicant_email": app.applicant.email,
                "applied_at": app.applied_at.isoformat(),
                "status": app.status,
                "cover_letter": app.cover_letter,
                "resume_path": app.resume_path,
                "job_title": app.job.title,
                "job_company": app.job.company
            }
            application_list.append(app_dict)
        
        return {"applications": application_list, "total": len(application_list)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting HR applications: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving applications: {str(e)}")

@router.put("/api/hr/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update application status (HR only)"""
    try:
        # Check if user is HR/domain user
        if current_user.user_type not in ['domain', 'hr', 'hr_user']:
            raise HTTPException(status_code=403, detail="Access denied. HR privileges required.")
        
        data = await request.json()
        new_status = data.get("status", "").strip()
        
        if not new_status:
            raise HTTPException(status_code=400, detail="Status is required")
        
        # Get application and verify ownership
        application = db.query(JobApplication).join(Job).filter(
            JobApplication.id == application_id,
            Job.posted_by == current_user.id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Update status
        application.status = new_status
        application.reviewed_at = datetime.now()
        
        db.commit()
        
        return {
            "message": "Application status updated successfully",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating application status: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating status: {str(e)}")

# ==================== JOB BOOKMARKING API ====================

@router.post("/api/jobs/bookmark")
async def bookmark_job(
    request: Request,
    job_data: dict,
    db: Session = Depends(get_db)
):
    """Add a job to user's bookmarks"""
    try:
        # Get current user from session
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(status_code=401, detail="Please log in.")
        
        session_data = get_user_from_session(session_token, db)
        if not session_data:
            raise HTTPException(status_code=401, detail="Not authenticated.")
        
        user_id = session_data['user_id']
        job_id = job_data.get('job_id')
        
        if not job_id:
            raise HTTPException(status_code=400, detail="Job ID is required")
        
        # Check if job exists and is active
        job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found or inactive")
        
        # For now, just return success (bookmark system can be implemented later)
        # TODO: Implement actual bookmark storage in database
        
        return {"message": "Job bookmarked successfully", "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bookmarking job: {e}")
        raise HTTPException(status_code=500, detail=f"Error bookmarking job: {str(e)}")

@router.delete("/api/jobs/bookmark/{job_id}")
async def remove_bookmark(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Remove a job from user's bookmarks"""
    try:
        # Get current user from session
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(status_code=401, detail="Not authenticated.")
        
        session_data = get_user_from_session(session_token, db)
        if not session_data:
            raise HTTPException(status_code=401, detail="Not authenticated.")
        
        user_id = session_data['user_id']
        
        # Check if job exists
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # For now, just return success (bookmark system can be implemented later)
        # TODO: Implement actual bookmark storage in database
        
        return {"message": "Bookmark removed successfully", "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing bookmark: {e}")
        raise HTTPException(status_code=500, detail=f"Error removing bookmark: {str(e)}")

        raise
    except Exception as e:
        logger.error(f"Error submitting job application: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting application: {str(e)}")

@router.get("/apply-form/{job_id}", response_class=HTMLResponse)
async def get_job_application_form(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get the job application form for a specific job"""
    try:
        # Check if user is authenticated
        session_token = request.cookies.get("session_token")
        if not session_token:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        session_data = get_user_from_session(session_token, db)
        if not session_data:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        current_user = db.query(User).filter(User.id == session_data['user_id']).first()
        if not current_user:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        # Get job details
        job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found or not active")
        
        # Check if user has already applied
        existing_application = db.query(JobApplication).filter(
            JobApplication.job_id == job_id,
            JobApplication.applicant_id == current_user.id
        ).first()
        
        if existing_application:
            return templates.TemplateResponse("job_already_applied.html", {
                "request": request,
                "user": current_user,
                "job": job,
                "application": existing_application
            })
        
        return templates.TemplateResponse("job_application_form.html", {
            "request": request,
            "user": current_user,
            "job": job
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job application form: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading application form: {str(e)}")

@router.get("/api/user/applications")
async def get_user_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's job applications"""
    try:
        # Get applications for the current user
        applications = db.query(JobApplication).join(Job).filter(
            JobApplication.applicant_id == current_user.id
        ).order_by(JobApplication.applied_at.desc()).all()
        
        application_list = []
        for app in applications:
            # Get status color based on status
            status_colors = {
                'pending': 'bg-yellow-100 text-yellow-800',
                'reviewed': 'bg-blue-100 text-blue-800',
                'interview': 'bg-green-100 text-green-800',
                'accepted': 'bg-green-100 text-green-800',
                'rejected': 'bg-red-100 text-red-800',
                'withdrawn': 'bg-gray-100 text-gray-800'
            }
            
            app_dict = {
                "id": app.id,
                "job_id": app.job_id,
                "position": app.job.title,
                "company": app.job.company,
                "location": app.job.location,
                "job_type": app.job.job_type,
                "status": app.status.replace('_', ' ').title(),
                "statusColor": status_colors.get(app.status, 'bg-gray-100 text-gray-800'),
                "appliedDate": app.applied_at.isoformat(),
                "applied_at": app.applied_at.isoformat(),
                "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None,
                "cover_letter": app.cover_letter,
                "resume_path": app.resume_path,
                "interview_scheduled": app.interview_scheduled.isoformat() if app.interview_scheduled else None,
                "hr_rating": app.hr_rating,
                "notes": app.notes
            }
            application_list.append(app_dict)
        
        return {
            "applications": application_list,
            "total": len(application_list),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user applications: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving applications: {str(e)}")


