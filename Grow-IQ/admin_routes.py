import os
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_, or_

from database import get_db
from auth_utils import get_current_user
from models import User, Workshop, Job, WorkshopRegistration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/admin", tags=["Admin"])

def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin privileges"""
    if current_user.user_type != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

@router.get("/", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Admin page - redirect to React frontend"""
    return RedirectResponse(url="/", status_code=307)

@router.get("/api/users")
async def get_all_users(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    user_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users with optional filtering (admin only)"""
    try:
        query = db.query(User)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%")
                )
            )
        
        if user_type:
            query = query.filter(User.user_type == user_type)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # Order by creation date
        query = query.order_by(desc(User.created_at))
        
        # Apply pagination
        users = query.offset(offset).limit(limit).all()
        total_count = query.count()
        
        return {
            "users": [user.to_dict() for user in users],
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@router.get("/api/users/{user_id}")
async def get_user_details(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed user information (admin only)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user")

@router.post("/api/users/{user_id}/toggle_active")
async def toggle_user_active(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Toggle user active status (admin only)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Don't allow deactivating other admins
        if user.user_type == 'admin' and user.id != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Cannot deactivate other admin users"
            )
        
        user.is_active = not user.is_active
        user.updated_at = datetime.now()
        
        db.commit()
        
        logger.info(f"User {user_id} active status toggled to {user.is_active} by admin {current_user.id}")
        return {"message": f"User {'activated' if user.is_active else 'deactivated'} successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error toggling user {user_id} active status: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle user status")

@router.post("/api/users/{user_id}/verify")
async def verify_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Verify a user (admin only)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_verified = True
        user.updated_at = datetime.now()
        
        db.commit()
        
        logger.info(f"User {user_id} verified by admin {current_user.id}")
        return {"message": "User verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error verifying user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify user")

@router.delete("/api/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Don't allow deleting other admins
        if user.user_type == 'admin':
            raise HTTPException(
                status_code=403, 
                detail="Cannot delete admin users"
            )
        
        # Don't allow deleting yourself
        if user.id == current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Cannot delete your own account"
            )
        
        db.delete(user)
        db.commit()
        
        logger.info(f"User {user_id} deleted by admin {current_user.id}")
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

@router.get("/api/stats")
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics (admin only)"""
    try:
        # User statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        verified_users = db.query(User).filter(User.is_verified == True).count()
        admin_users = db.query(User).filter(User.user_type == 'admin').count()
        
        # Workshop statistics
        total_workshops = db.query(Workshop).count()
        published_workshops = db.query(Workshop).filter(Workshop.status == 'published').count()
        draft_workshops = db.query(Workshop).filter(Workshop.status == 'draft').count()
        
        # Job statistics
        total_jobs = db.query(Job).count()
        
        # Registration statistics
        total_registrations = db.query(WorkshopRegistration).count()
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "verified": verified_users,
                "admins": admin_users
            },
            "workshops": {
                "total": total_workshops,
                "published": published_workshops,
                "draft": draft_workshops
            },
            "jobs": {
                "total": total_jobs
            },
            "registrations": {
                "total": total_registrations
            }
        }
    except Exception as e:
        logger.error(f"Error fetching admin stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@router.get("/api/workshops")
async def get_all_workshops_admin(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    approval_status: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all workshops for admin management (admin only)"""
    try:
        query = db.query(Workshop)
        
        if status:
            query = query.filter(Workshop.status == status)
        
        if approval_status:
            query = query.filter(Workshop.approval_status == approval_status)
        
        query = query.order_by(desc(Workshop.created_at))
        
        workshops = query.offset(offset).limit(limit).all()
        total_count = query.count()
        
        return {
            "workshops": [workshop.to_dict() for workshop in workshops],
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching workshops for admin: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch workshops")

@router.get("/api/workshops/pending")
async def get_pending_workshops(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get pending workshops for approval (admin only)"""
    try:
        query = db.query(Workshop).filter(Workshop.approval_status == 'pending')
        query = query.order_by(asc(Workshop.created_at))
        
        workshops = query.offset(offset).limit(limit).all()
        total_count = query.count()
        
        return {
            "workshops": [workshop.to_dict() for workshop in workshops],
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching pending workshops: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch pending workshops")

@router.post("/api/workshops/{workshop_id}/approve")
async def approve_workshop(
    workshop_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve a workshop (admin only)"""
    try:
        workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
        if not workshop:
            raise HTTPException(status_code=404, detail="Workshop not found")
        
        if workshop.approval_status != 'pending':
            raise HTTPException(
                status_code=400, 
                detail=f"Workshop is already {workshop.approval_status}"
            )
        
        workshop.approval_status = 'approved'
        workshop.status = 'published'
        workshop.approved_by = current_user.id
        workshop.approved_at = datetime.now()
        workshop.updated_at = datetime.now()
        
        db.commit()
        
        logger.info(f"Workshop {workshop_id} approved by admin {current_user.id}")
        return {"message": "Workshop approved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error approving workshop {workshop_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to approve workshop")

@router.post("/api/workshops/{workshop_id}/reject")
async def reject_workshop(
    workshop_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reject a workshop (admin only)"""
    try:
        # Parse JSON body for rejection reason
        body = await request.json()
        rejection_reason = body.get('rejection_reason', 'No reason provided')
        
        workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
        if not workshop:
            raise HTTPException(status_code=404, detail="Workshop not found")
        
        if workshop.approval_status != 'pending':
            raise HTTPException(
                status_code=400, 
                detail=f"Workshop is already {workshop.approval_status}"
            )
        
        workshop.approval_status = 'rejected'
        workshop.status = 'draft'
        workshop.rejection_reason = rejection_reason
        workshop.approved_by = current_user.id
        workshop.approved_at = datetime.now()
        workshop.updated_at = datetime.now()
        
        db.commit()
        
        logger.info(f"Workshop {workshop_id} rejected by admin {current_user.id}")
        return {"message": "Workshop rejected successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error rejecting workshop {workshop_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject workshop")

@router.get("/api/jobs")
async def get_all_jobs_admin(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all jobs for admin management (admin only)"""
    try:
        query = db.query(Job)
        query = query.order_by(desc(Job.created_at))
        
        jobs = query.offset(offset).limit(limit).all()
        total_count = query.count()
        
        return {
            "jobs": [job.to_dict() for job in jobs],
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching jobs for admin: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch jobs")
