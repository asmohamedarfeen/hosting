"""
HR Dashboard Routes
==================

This module contains routes for HR functionality including:
- Job application management
- Candidate profile viewing
- Application status updates
- HR-only access control
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Query, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from database_enhanced import get_db
from models import User, Job, JobApplication
from auth_utils import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router instance
router = APIRouter(prefix="/hr", tags=["HR Management"])

# Templates
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# HR Authentication Dependency
def get_hr_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify that current user has HR privileges - for domain email, domain ID, or HR ID users"""
    logger.info(f"HR access check for user: {current_user.email}")
    logger.info(f"User type: {current_user.user_type}")
    logger.info(f"Is verified: {current_user.is_verified}")
    logger.info(f"Domain ID: {current_user.domain_id}")
    logger.info(f"HR ID: {current_user.hr_id}")
    logger.info(f"Access type: {current_user.get_access_type()}")
    logger.info(f"Can manage applications: {current_user.can_manage_applications()}")
    
    # Check for development mode override
    if os.path.exists('.hr_dev_mode'):
        logger.info(f"Development mode detected - bypassing HR restrictions for {current_user.email}")
        return current_user
    
    # Check if user has HR privileges (domain email, domain ID, or HR ID)
    if not current_user.can_manage_applications():
        logger.warning(f"HR access denied for {current_user.email} - insufficient privileges")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. HR dashboard is only available for users with company email addresses, domain IDs, or HR IDs."
        )
    
    logger.info(f"HR access granted for {current_user.email} with access type: {current_user.get_access_type()}")
    return current_user

# ==================== HR DASHBOARD ====================

@router.get("/dashboard", response_class=HTMLResponse)
async def hr_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    hr_user: User = Depends(get_hr_user)
):
    """HR Dashboard - Main overview page"""
    try:
        # Get HR user's posted jobs
        posted_jobs = db.query(Job).filter(
            Job.posted_by == hr_user.id,
            Job.is_active == True
        ).order_by(desc(Job.posted_at)).all()
        
        # Get applications for HR user's jobs
        job_ids = [job.id for job in posted_jobs]
        applications = []
        
        if job_ids:
            try:
                applications = db.query(JobApplication).join(Job).filter(
                    Job.posted_by == hr_user.id
                ).order_by(desc(JobApplication.applied_at)).all()
                logger.info(f"Retrieved {len(applications)} applications for {len(job_ids)} jobs")
            except Exception as e:
                logger.error(f"Error retrieving applications: {e}")
                applications = []
        
        # Calculate statistics with safe defaults
        total_jobs = len(posted_jobs)
        total_applications = len(applications)
        pending_applications = sum(1 for app in applications if app.status == 'pending')
        reviewed_applications = sum(1 for app in applications if app.status == 'reviewed')
        interviews_scheduled = sum(1 for app in applications if app.status == 'interview')
        
        # Recent applications (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_applications = [app for app in applications if app.applied_at and app.applied_at >= week_ago]
        
        # Helper function to safely convert objects for templates
        def safe_convert_for_template(obj):
            """Convert database objects to template-safe format"""
            if hasattr(obj, '__dict__'):
                safe_dict = {}
                for key, value in obj.__dict__.items():
                    if key.startswith('_'):
                        continue
                    if isinstance(value, datetime):
                        safe_dict[key] = value.isoformat()
                    elif hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool, type(None))):
                        # Recursively convert nested objects
                        safe_dict[key] = safe_convert_for_template(value)
                    else:
                        safe_dict[key] = value
                
                # Add computed properties for User objects
                if hasattr(obj, 'is_hr_user'):
                    try:
                        safe_dict['is_hr_user'] = obj.is_hr_user()
                    except:
                        safe_dict['is_hr_user'] = False
                        
                if hasattr(obj, 'is_domain_user'):
                    try:
                        safe_dict['is_domain_user'] = obj.is_domain_user()
                    except:
                        safe_dict['is_domain_user'] = False
                        
                if hasattr(obj, 'can_post_jobs'):
                    try:
                        safe_dict['can_post_jobs'] = obj.can_post_jobs()
                    except:
                        safe_dict['can_post_jobs'] = False
                        
                if hasattr(obj, 'is_domain_email'):
                    try:
                        safe_dict['is_domain_email'] = obj.is_domain_email()
                    except:
                        safe_dict['is_domain_email'] = False
                        
                if hasattr(obj, 'get_profile_image_url'):
                    try:
                        safe_dict['get_profile_image_url'] = obj.get_profile_image_url()
                    except:
                        safe_dict['get_profile_image_url'] = '/static/uploads/default-avatar.svg'
                
                return safe_dict
            return obj
        
        # Prepare context with safe data
        context = {
            "request": request,
            "hr_user": {
                "id": hr_user.id,
                "username": hr_user.username,
                "email": hr_user.email,
                "full_name": hr_user.full_name,
                "title": hr_user.title,
                "company": hr_user.company,
                "location": hr_user.location,
                "profile_image": hr_user.profile_image,
                "get_profile_image_url": hr_user.get_profile_image_url(),
                "domain_id": hr_user.domain_id,
                "hr_id": hr_user.hr_id,
                "access_type": hr_user.get_access_type(),
                "has_domain_access": hr_user.has_domain_access()
            },
            "posted_jobs": [{
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "job_type": job.job_type,
                "posted_at": job.posted_at,
                "is_active": job.is_active,
                "applications_count": job.applications_count or 0,
                "views_count": job.views_count or 0
            } for job in posted_jobs],
            "applications": [{
                "id": app.id,
                "status": app.status,
                "applied_at": app.applied_at,
                "hr_rating": app.hr_rating,
                "notes": app.notes,
                "cover_letter": app.cover_letter,
                "resume_path": app.resume_path,
                "interview_scheduled": app.interview_scheduled,
                "interview_notes": app.interview_notes,
                "applicant": {
                    "id": app.applicant.id,
                    "username": app.applicant.username,
                    "email": app.applicant.email,
                    "full_name": app.applicant.full_name,
                    "title": app.applicant.title,
                    "company": app.applicant.company,
                    "location": app.applicant.location,
                    "profile_image": app.applicant.profile_image,
                    "get_profile_image_url": app.applicant.get_profile_image_url()
                },
                "job": {
                    "id": app.job.id,
                    "title": app.job.title,
                    "company": app.job.company,
                    "location": app.job.location
                }
            } for app in applications[:10]],  # Latest 10 applications
            "stats": {
                "total_jobs": total_jobs,
                "total_applications": total_applications,
                "pending_applications": pending_applications,
                "reviewed_applications": reviewed_applications,
                "interviews_scheduled": interviews_scheduled,
                "recent_applications": len(recent_applications)
            }
        }
        
        logger.info(f"HR Dashboard context prepared successfully for user {hr_user.email}")
        logger.info(f"Jobs: {total_jobs}, Applications: {total_applications}")
        
        return templates.TemplateResponse("hr_dashboard.html", context)
        
    except Exception as e:
        logger.error(f"Error loading HR dashboard: {e}")
        logger.error(f"Error details: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error loading HR dashboard: {str(e)}")

# ==================== JOB APPLICATION MANAGEMENT ====================

@router.get("/applications")
async def get_applications(
    job_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    hr_user: User = Depends(get_hr_user)
):
    """Get job applications for HR user's job postings"""
    try:
        # Base query for applications to HR user's jobs
        query = db.query(JobApplication).join(Job).filter(
            Job.posted_by == hr_user.id
        )
        
        # Apply filters
        if job_id:
            query = query.filter(JobApplication.job_id == job_id)
        
        if status:
            query = query.filter(JobApplication.status == status)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        applications = query.order_by(desc(JobApplication.applied_at)).offset(offset).limit(limit).all()
        
        # Format response
        applications_data = []
        for app in applications:
            applications_data.append({
                "id": app.id,
                "job": {
                    "id": app.job.id,
                    "title": app.job.title,
                    "company": app.job.company
                },
                "applicant": {
                    "id": app.applicant.id,
                    "name": app.applicant.full_name,
                    "email": app.applicant.email,
                    "profile_image": app.applicant.get_profile_image_url(),
                    "title": app.applicant.title,
                    "company": app.applicant.company,
                    "location": app.applicant.location,
                    "experience_years": app.applicant.experience_years,
                    "skills": app.applicant.skills
                },
                "status": app.status,
                "applied_at": app.applied_at.isoformat(),
                "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None,
                "hr_rating": app.hr_rating,
                "notes": app.notes,
                "cover_letter": app.cover_letter,
                "resume_path": app.resume_path,
                "interview_scheduled": app.interview_scheduled.isoformat() if app.interview_scheduled else None
            })
        
        return {
            "applications": applications_data,
            "total_count": total_count,
            "offset": offset,
            "limit": limit,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error getting applications: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving applications")

@router.get("/applications/{application_id}")
async def get_application_detail(
    application_id: int,
    db: Session = Depends(get_db),
    hr_user: User = Depends(get_hr_user)
):
    """Get detailed information about a specific application"""
    try:
        # Get application with ownership check
        application = db.query(JobApplication).join(Job).filter(
            JobApplication.id == application_id,
            Job.posted_by == hr_user.id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Get applicant's full profile
        applicant = application.applicant
        
        return {
            "application": {
                "id": application.id,
                "status": application.status,
                "applied_at": application.applied_at.isoformat(),
                "reviewed_at": application.reviewed_at.isoformat() if application.reviewed_at else None,
                "hr_rating": application.hr_rating,
                "notes": application.notes,
                "cover_letter": application.cover_letter,
                "resume_path": application.resume_path,
                "interview_scheduled": application.interview_scheduled.isoformat() if application.interview_scheduled else None,
                "interview_notes": application.interview_notes
            },
            "job": {
                "id": application.job.id,
                "title": application.job.title,
                "company": application.job.company,
                "location": application.job.location,
                "job_type": application.job.job_type
            },
            "applicant": {
                "id": applicant.id,
                "username": applicant.username,
                "email": applicant.email,
                "full_name": applicant.full_name,
                "title": applicant.title,
                "company": applicant.company,
                "location": applicant.location,
                "bio": applicant.bio,
                "profile_image": applicant.get_profile_image_url(),
                "phone": applicant.phone if applicant.show_phone else None,
                "website": applicant.website,
                "linkedin_url": applicant.linkedin_url,
                "github_url": applicant.github_url,
                "industry": applicant.industry,
                "skills": applicant.skills,
                "experience_years": applicant.experience_years,
                "education": applicant.education,
                "certifications": applicant.certifications,
                "created_at": applicant.created_at.isoformat()
            },
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting application detail: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving application details")

@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    request: Request,
    db: Session = Depends(get_db),
    hr_user: User = Depends(get_hr_user)
):
    """Update application status and add HR notes"""
    try:
        # Parse request data
        data = await request.json()
        new_status = data.get("status")
        notes = data.get("notes", "")
        hr_rating = data.get("hr_rating")
        interview_date = data.get("interview_date")
        interview_notes = data.get("interview_notes", "")
        
        # Validate status
        valid_statuses = ['pending', 'reviewed', 'interview', 'rejected', 'hired']
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        # Get application with ownership check
        application = db.query(JobApplication).join(Job).filter(
            JobApplication.id == application_id,
            Job.posted_by == hr_user.id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Update application
        application.status = new_status
        application.notes = notes
        application.reviewed_at = datetime.now()
        
        if hr_rating and 1 <= hr_rating <= 5:
            application.hr_rating = hr_rating
        
        if interview_date:
            application.interview_scheduled = datetime.fromisoformat(interview_date)
        
        if interview_notes:
            application.interview_notes = interview_notes
        
        db.commit()
        
        logger.info(f"HR user {hr_user.id} updated application {application_id} to status: {new_status}")
        
        return {
            "message": "Application status updated successfully",
            "application_id": application_id,
            "new_status": new_status,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating application status: {e}")
        raise HTTPException(status_code=500, detail="Error updating application status")

# ==================== CANDIDATE MANAGEMENT ====================

@router.get("/candidates")
async def get_candidates(
    job_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skills: Optional[str] = Query(None),
    experience_min: Optional[int] = Query(None),
    location: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    hr_user: User = Depends(get_hr_user)
):
    """Search and filter candidates who applied to HR's jobs"""
    try:
        # Base query for applicants to HR user's jobs
        query = db.query(User).join(JobApplication).join(Job).filter(
            Job.posted_by == hr_user.id
        ).distinct()
        
        # Apply filters
        if job_id:
            query = query.filter(JobApplication.job_id == job_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.full_name.ilike(search_term)) |
                (User.email.ilike(search_term)) |
                (User.title.ilike(search_term)) |
                (User.skills.ilike(search_term))
            )
        
        if skills:
            skills_term = f"%{skills}%"
            query = query.filter(User.skills.ilike(skills_term))
        
        if experience_min:
            query = query.filter(User.experience_years >= experience_min)
        
        if location:
            location_term = f"%{location}%"
            query = query.filter(User.location.ilike(location_term))
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        candidates = query.offset(offset).limit(limit).all()
        
        # Format response
        candidates_data = []
        for candidate in candidates:
            # Get applications from this candidate to HR's jobs
            candidate_applications = db.query(JobApplication).join(Job).filter(
                JobApplication.applicant_id == candidate.id,
                Job.posted_by == hr_user.id
            ).all()
            
            candidates_data.append({
                "id": candidate.id,
                "name": candidate.full_name,
                "email": candidate.email,
                "title": candidate.title,
                "company": candidate.company,
                "location": candidate.location,
                "bio": candidate.bio,
                "profile_image": candidate.get_profile_image_url(),
                "experience_years": candidate.experience_years,
                "skills": candidate.skills,
                "applications_count": len(candidate_applications),
                "latest_application": candidate_applications[0].applied_at.isoformat() if candidate_applications else None
            })
        
        return {
            "candidates": candidates_data,
            "total_count": total_count,
            "offset": offset,
            "limit": limit,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error getting candidates: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving candidates")

# ==================== HR STATISTICS ====================

@router.get("/stats")
async def get_hr_stats(
    db: Session = Depends(get_db),
    hr_user: User = Depends(get_hr_user)
):
    """Get comprehensive HR statistics"""
    try:
        # Get HR user's jobs
        jobs = db.query(Job).filter(Job.posted_by == hr_user.id).all()
        job_ids = [job.id for job in jobs]
        
        # Get applications
        applications = []
        if job_ids:
            applications = db.query(JobApplication).filter(
                JobApplication.job_id.in_(job_ids)
            ).all()
        
        # Calculate time-based statistics
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Applications by status
        status_counts = {}
        for status in ['pending', 'reviewed', 'interview', 'rejected', 'hired']:
            status_counts[status] = sum(1 for app in applications if app.status == status)
        
        # Recent activity
        recent_applications = [app for app in applications if app.applied_at >= week_ago]
        monthly_applications = [app for app in applications if app.applied_at >= month_ago]
        
        # Job performance
        job_stats = []
        for job in jobs:
            job_applications = [app for app in applications if app.job_id == job.id]
            job_stats.append({
                "id": job.id,
                "title": job.title,
                "posted_at": job.posted_at.isoformat(),
                "applications_count": len(job_applications),
                "pending_count": sum(1 for app in job_applications if app.status == 'pending'),
                "hired_count": sum(1 for app in job_applications if app.status == 'hired'),
                "avg_rating": round(sum(app.hr_rating for app in job_applications if app.hr_rating) / len([app for app in job_applications if app.hr_rating]), 2) if any(app.hr_rating for app in job_applications) else None
            })
        
        return {
            "overview": {
                "total_jobs": len(jobs),
                "active_jobs": sum(1 for job in jobs if job.is_active),
                "total_applications": len(applications),
                "unique_applicants": len(set(app.applicant_id for app in applications))
            },
            "applications_by_status": status_counts,
            "recent_activity": {
                "week_applications": len(recent_applications),
                "month_applications": len(monthly_applications)
            },
            "job_performance": job_stats,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error getting HR stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving HR statistics")

# ==================== BULK ACTIONS ====================

@router.post("/applications/bulk-action")
async def bulk_action_applications(
    request: Request,
    db: Session = Depends(get_db),
    hr_user: User = Depends(get_hr_user)
):
    """Perform bulk actions on multiple applications"""
    try:
        data = await request.json()
        application_ids = data.get("application_ids", [])
        action = data.get("action")
        new_status = data.get("status")
        notes = data.get("notes", "")
        
        if not application_ids or not action:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Verify ownership of all applications
        applications = db.query(JobApplication).join(Job).filter(
            JobApplication.id.in_(application_ids),
            Job.posted_by == hr_user.id
        ).all()
        
        if len(applications) != len(application_ids):
            raise HTTPException(status_code=404, detail="Some applications not found or access denied")
        
        updated_count = 0
        
        if action == "update_status" and new_status:
            for application in applications:
                application.status = new_status
                application.reviewed_at = datetime.now()
                if notes:
                    application.notes = notes
                updated_count += 1
        
        elif action == "add_notes" and notes:
            for application in applications:
                application.notes = notes
                application.reviewed_at = datetime.now()
                updated_count += 1
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action or missing parameters")
        
        db.commit()
        
        logger.info(f"HR user {hr_user.id} performed bulk action '{action}' on {updated_count} applications")
        
        return {
            "message": f"Bulk action completed successfully",
            "action": action,
            "updated_count": updated_count,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error performing bulk action: {e}")
        raise HTTPException(status_code=500, detail="Error performing bulk action")

# ==================== ENHANCED HR DASHBOARD FOR DOMAIN ID/HR ID USERS ====================

@router.get("/enhanced-dashboard", response_class=HTMLResponse)
async def enhanced_hr_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    hr_user: User = Depends(get_hr_user)
):
    """Enhanced HR Dashboard for domain ID and HR ID users with additional features"""
    try:
        # Check if user has enhanced access (domain ID or HR ID)
        access_type = hr_user.get_access_type()
        has_enhanced_access = access_type in ['domain_id', 'hr_id']
        
        if not has_enhanced_access:
            # Redirect to regular HR dashboard if no enhanced access
            return RedirectResponse(url="/hr/dashboard", status_code=303)
        
        # Get all jobs (not just user's jobs) for enhanced users
        all_jobs = db.query(Job).filter(Job.is_active == True).order_by(desc(Job.posted_at)).all()
        
        # Get all applications for enhanced users
        all_applications = db.query(JobApplication).join(Job).order_by(desc(JobApplication.applied_at)).all()
        
        # Calculate enhanced statistics
        total_jobs = len(all_jobs)
        total_applications = len(all_applications)
        pending_applications = sum(1 for app in all_applications if app.status == 'pending')
        reviewed_applications = sum(1 for app in all_applications if app.status == 'reviewed')
        interviews_scheduled = sum(1 for app in all_applications if app.status == 'interview')
        
        # Recent applications (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_applications = [app for app in all_applications if app.applied_at and app.applied_at >= week_ago]
        
        # Company-wide statistics for enhanced users
        company_stats = {
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "pending_applications": pending_applications,
            "reviewed_applications": reviewed_applications,
            "interviews_scheduled": interviews_scheduled,
            "recent_applications": len(recent_applications),
            "avg_application_time": "2.3 days",  # Placeholder
            "hiring_success_rate": "78%",  # Placeholder
            "top_performing_jobs": 5
        }
        
        # Prepare enhanced context
        context = {
            "request": request,
            "hr_user": {
                "id": hr_user.id,
                "username": hr_user.username,
                "email": hr_user.email,
                "full_name": hr_user.full_name,
                "title": hr_user.title,
                "company": hr_user.company,
                "location": hr_user.location,
                "profile_image": hr_user.profile_image,
                "get_profile_image_url": hr_user.get_profile_image_url(),
                "domain_id": hr_user.domain_id,
                "hr_id": hr_user.hr_id,
                "access_type": access_type,
                "has_enhanced_access": has_enhanced_access
            },
            "all_jobs": [{
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "job_type": job.job_type,
                "posted_at": job.posted_at,
                "is_active": job.is_active,
                "applications_count": job.applications_count or 0,
                "views_count": job.views_count or 0,
                "posted_by": job.posted_by
            } for job in all_jobs],
            "all_applications": [{
                "id": app.id,
                "status": app.status,
                "applied_at": app.applied_at,
                "hr_rating": app.hr_rating,
                "notes": app.notes,
                "cover_letter": app.cover_letter,
                "resume_path": app.resume_path,
                "interview_scheduled": app.interview_scheduled,
                "interview_notes": app.interview_notes,
                "applicant": {
                    "id": app.applicant.id,
                    "username": app.applicant.username,
                    "email": app.applicant.email,
                    "full_name": app.applicant.full_name,
                    "title": app.applicant.title,
                    "company": app.applicant.company,
                    "location": app.applicant.location,
                    "profile_image": app.applicant.profile_image,
                    "get_profile_image_url": app.applicant.get_profile_image_url()
                },
                "job": {
                    "id": app.job.id,
                    "title": app.job.title,
                    "company": app.job.company,
                    "location": app.job.location
                }
            } for app in all_applications[:20]],  # Latest 20 applications
            "company_stats": company_stats,
            "access_type": access_type
        }
        
        logger.info(f"Enhanced HR Dashboard loaded for {hr_user.email} with access type: {access_type}")
        
        return templates.TemplateResponse("hr_enhanced_dashboard.html", context)
        
    except Exception as e:
        logger.error(f"Error loading enhanced HR dashboard: {e}")
        logger.error(f"Error details: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error loading enhanced HR dashboard: {str(e)}")

# ==================== JOB POSTING ====================

@router.post("/jobs/create", response_class=JSONResponse)
async def create_job(
    request: Request,
    db: Session = Depends(get_db),
    hr_user: User = Depends(get_hr_user)
):
    """HR users can create new jobs (for frontend)"""
    try:
        # Get form data
        form_data = await request.form()
        
        # Extract job details
        title = form_data.get("title")
        company = form_data.get("company", hr_user.company or "Company")
        location = form_data.get("location", hr_user.location or "Location")
        job_type = form_data.get("job_type", "full-time")
        salary_range = form_data.get("salary_range", "")
        description = form_data.get("description", "")
        requirements = form_data.get("requirements", "")
        benefits = form_data.get("benefits", "")
        application_deadline = form_data.get("application_deadline", "")
        
        # Extract skills_required from form (can be array or comma-separated)
        skills_required = []
        if "skills_required[0]" in form_data:
            # Handle array format: skills_required[0], skills_required[1], etc.
            index = 0
            while f"skills_required[{index}]" in form_data:
                skill = form_data.get(f"skills_required[{index}]", "").strip()
                if skill:
                    skills_required.append(skill)
                index += 1
        elif "skills_required" in form_data:
            # Handle single value or comma-separated string
            skills_str = form_data.get("skills_required", "").strip()
            if skills_str:
                import re
                skills_required = [s.strip() for s in re.split(r"[,\n;]+", skills_str) if s.strip()]
        
        # Add skills to requirements for matching algorithm
        skills_section = ""
        if skills_required:
            skills_section = "\n[SKILLS] " + ", ".join(skills_required)
        
        # Validate required fields
        if not title:
            raise HTTPException(status_code=400, detail="Job title is required")
        
        # Create new job (embed skills in requirements for recommendation engine)
        new_job = Job(
            title=title,
            company=company,
            location=location,
            job_type=job_type,
            salary_range=salary_range,
            description=description,
            requirements=(requirements or "") + skills_section,
            benefits=benefits,
            posted_by=hr_user.id,
            is_active=True,
            posted_at=datetime.now()
        )
        
        # Add application deadline if provided
        if application_deadline:
            try:
                new_job.application_deadline = datetime.fromisoformat(application_deadline)
            except:
                pass
        
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        logger.info(f"New job created by HR user {hr_user.email}: {title}")
        
        return {
            "success": True,
            "message": "Job created successfully",
            "job_id": new_job.id,
            "job": {
                "id": new_job.id,
                "title": new_job.title,
                "company": new_job.company,
                "location": new_job.location,
                "job_type": new_job.job_type,
                "salary_range": new_job.salary_range,
                "description": new_job.description,
                "posted_at": new_job.posted_at.isoformat() if new_job.posted_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating job: {str(e)}")

@router.post("/jobs/post", response_class=JSONResponse)
async def post_job(
    request: Request,
    db: Session = Depends(get_db),
    hr_user: User = Depends(get_hr_user)
):
    """HR users can post new jobs (legacy endpoint)"""
    try:
        # Get form data
        form_data = await request.form()
        
        # Extract job details
        title = form_data.get("title")
        company = form_data.get("company", hr_user.company or "Company")
        location = form_data.get("location", hr_user.location or "Location")
        job_type = form_data.get("job_type", "full-time")
        salary_range = form_data.get("salary_range", "")
        description = form_data.get("description", "")
        requirements = form_data.get("requirements", "")
        benefits = form_data.get("benefits", "")
        
        # Validate required fields
        if not title:
            raise HTTPException(status_code=400, detail="Job title is required")
        
        # Create new job
        new_job = Job(
            title=title,
            company=company,
            location=location,
            job_type=job_type,
            salary_range=salary_range,
            description=description,
            requirements=requirements,
            benefits=benefits,
            posted_by=hr_user.id,
            is_active=True,
            posted_at=datetime.now()
        )
        
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        logger.info(f"New job posted by HR user {hr_user.email}: {title}")
        
        return {
            "success": True,
            "message": "Job posted successfully",
            "job_id": new_job.id,
            "job": {
                "id": new_job.id,
                "title": new_job.title,
                "company": new_job.company,
                "location": new_job.location,
                "job_type": new_job.job_type,
                "salary_range": new_job.salary_range,
                "description": new_job.description,
                "posted_at": new_job.posted_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error posting job: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error posting job: {str(e)}")

@router.get("/jobs/post-form", response_class=HTMLResponse)
async def get_job_post_form(
    request: Request,
    hr_user: User = Depends(get_hr_user)
):
    """Get the job posting form for HR users"""
    return templates.TemplateResponse("hr_job_post_form.html", {
        "request": request,
        "hr_user": hr_user
    })

# ==================== CANDIDATE FULL PROFILE VIEW ====================

@router.get("/candidate/{user_id}", response_class=HTMLResponse)
async def view_candidate_full_profile(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    hr_user: User = Depends(get_hr_user)
):
    """Show complete candidate profile details for HR users."""
    try:
        candidate = db.query(User).filter(User.id == user_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        # Applications this candidate made to HR user's jobs (contextual history)
        applications = db.query(JobApplication).join(Job).filter(
            JobApplication.applicant_id == candidate.id,
            Job.posted_by == hr_user.id
        ).order_by(desc(JobApplication.applied_at)).all()

        context = {
            "request": request,
            "hr_user": hr_user,
            "candidate": {
                "id": candidate.id,
                "username": candidate.username,
                "email": candidate.email,
                "full_name": candidate.full_name,
                "title": candidate.title,
                "company": candidate.company,
                "location": candidate.location,
                "bio": candidate.bio,
                "profile_image": candidate.get_profile_image_url(),
                "website": candidate.website,
                "linkedin_url": candidate.linkedin_url,
                "twitter_url": candidate.twitter_url,
                "github_url": candidate.github_url,
                "industry": candidate.industry,
                "skills": candidate.skills,
                "experience_years": candidate.experience_years,
                "experience": candidate.experience,
                "education": candidate.education,
                "certifications": candidate.certifications,
                "interests": candidate.interests,
                "portfolio_url": candidate.portfolio_url,
                "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
                "updated_at": candidate.updated_at.isoformat() if candidate.updated_at else None,
                # Respect privacy for phone/email flags
                "phone": candidate.phone if candidate.show_phone else None,
                "show_phone": candidate.show_phone,
                "show_email": candidate.show_email,
                "profile_visibility": candidate.profile_visibility
            },
            "applications": [
                {
                    "id": app.id,
                    "job_id": app.job_id,
                    "job_title": app.job.title,
                    "job_company": app.job.company,
                    "status": app.status,
                    "applied_at": app.applied_at.isoformat() if app.applied_at else None,
                    "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None,
                    "hr_rating": app.hr_rating,
                    "notes": app.notes
                } for app in applications
            ]
        }

        # Render template if exists; else return JSON fallback
        try:
            return templates.TemplateResponse("hr_candidate_profile.html", context)
        except Exception:
            return JSONResponse({"status": "success", **context})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading candidate profile {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error loading candidate profile")

# ==================== API ENDPOINTS ====================

@router.get("/jobs")
async def get_hr_jobs(
    db: Session = Depends(get_db),
    hr_user: User = Depends(get_hr_user)
):
    """Get HR user's posted jobs for the frontend"""
    try:
        # Get HR user's posted jobs
        posted_jobs = db.query(Job).filter(
            Job.posted_by == hr_user.id,
            Job.is_active == True
        ).order_by(desc(Job.posted_at)).all()
        
        # Convert to JSON-serializable format
        jobs_data = []
        for job in posted_jobs:
            jobs_data.append({
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
                "is_active": job.is_active,
                "applications_count": job.applications_count or 0,
                "views_count": job.views_count or 0
            })
        
        logger.info(f"Retrieved {len(jobs_data)} jobs for HR user {hr_user.email}")
        
        return {
            "success": True,
            "jobs": jobs_data,
            "total": len(jobs_data)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving HR jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving jobs: {str(e)}")
