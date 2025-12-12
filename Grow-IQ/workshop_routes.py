import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_, or_
from pydantic import BaseModel

from database import get_db
from auth_utils import get_current_user
from models import User, Workshop, WorkshopRegistration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/workshops", tags=["Workshops"])

# ========== DATA MODELS ==========
class WorkshopCreate(BaseModel):
    title: str
    description: str
    instructor: str
    instructor_email: Optional[str] = None
    instructor_bio: Optional[str] = None
    category: str
    level: str
    duration_hours: int
    max_participants: Optional[int] = None
    price: int = 0
    currency: str = "USD"
    start_date: datetime
    end_date: datetime
    location: Optional[str] = None
    is_online: bool = False
    meeting_link: Optional[str] = None
    materials: Optional[List[str]] = []
    prerequisites: Optional[List[str]] = []
    learning_objectives: Optional[List[str]] = []
    status: str = "draft"

class WorkshopUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructor: Optional[str] = None
    instructor_email: Optional[str] = None
    instructor_bio: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    duration_hours: Optional[int] = None
    max_participants: Optional[int] = None
    price: Optional[int] = None
    currency: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    is_online: Optional[bool] = None
    meeting_link: Optional[str] = None
    materials: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    status: Optional[str] = None

class WorkshopRegistrationCreate(BaseModel):
    workshop_id: int
    notes: Optional[str] = None

# ========== WORKSHOP ROUTES ==========

@router.get("/", response_class=HTMLResponse)
async def workshops_page(request: Request):
    """Workshops page - redirect to React frontend"""
    return RedirectResponse(url="/", status_code=307)

@router.get("/api/workshops")
async def get_workshops(
    request: Request,
    category: Optional[str] = None,
    level: Optional[str] = None,
    status: Optional[str] = "published",
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all workshops with optional filtering"""
    try:
        query = db.query(Workshop)
        
        # Apply filters
        if category:
            query = query.filter(Workshop.category == category)
        if level:
            query = query.filter(Workshop.level == level)
        if status:
            query = query.filter(Workshop.status == status)
        
        # For regular users, only show approved workshops
        # For admins, show all workshops
        if current_user.user_type != 'admin':
            query = query.filter(Workshop.approval_status == 'approved')
        
        # Order by start date
        query = query.order_by(asc(Workshop.start_date))
        
        # Apply pagination
        workshops = query.offset(offset).limit(limit).all()
        total_count = query.count()
        
        return {
            "workshops": [workshop.to_dict() for workshop in workshops],
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching workshops: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch workshops")

@router.get("/api/workshops/{workshop_id}")
async def get_workshop(
    workshop_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific workshop by ID"""
    try:
        workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
        if not workshop:
            raise HTTPException(status_code=404, detail="Workshop not found")
        
        return workshop.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching workshop {workshop_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch workshop")

@router.post("/api/workshops")
async def create_workshop(
    workshop_data: WorkshopCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workshop"""
    try:
        # Validate dates
        if workshop_data.start_date >= workshop_data.end_date:
            raise HTTPException(
                status_code=400, 
                detail="End date must be after start date"
            )
        
        # Create workshop
        workshop = Workshop(
            title=workshop_data.title,
            description=workshop_data.description,
            instructor=workshop_data.instructor,
            instructor_email=workshop_data.instructor_email,
            instructor_bio=workshop_data.instructor_bio,
            category=workshop_data.category,
            level=workshop_data.level,
            duration_hours=workshop_data.duration_hours,
            max_participants=workshop_data.max_participants,
            price=workshop_data.price,
            currency=workshop_data.currency,
            start_date=workshop_data.start_date,
            end_date=workshop_data.end_date,
            location=workshop_data.location,
            is_online=workshop_data.is_online,
            meeting_link=workshop_data.meeting_link,
            materials=json.dumps(workshop_data.materials) if workshop_data.materials else None,
            prerequisites=json.dumps(workshop_data.prerequisites) if workshop_data.prerequisites else None,
            learning_objectives=json.dumps(workshop_data.learning_objectives) if workshop_data.learning_objectives else None,
            status='draft',  # Always start as draft
            approval_status='pending',  # Require admin approval
            created_by=current_user.id
        )
        
        db.add(workshop)
        db.commit()
        db.refresh(workshop)
        
        logger.info(f"Created workshop {workshop.id} by user {current_user.id}")
        return workshop.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating workshop: {e}")
        raise HTTPException(status_code=500, detail="Failed to create workshop")

@router.put("/api/workshops/{workshop_id}")
async def update_workshop(
    workshop_id: int,
    workshop_data: WorkshopUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a workshop"""
    try:
        workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
        if not workshop:
            raise HTTPException(status_code=404, detail="Workshop not found")
        
        # Check if user can update (creator or admin)
        if workshop.created_by != current_user.id and current_user.user_type != 'admin':
            raise HTTPException(status_code=403, detail="Not authorized to update this workshop")
        
        # Update fields
        update_data = workshop_data.dict(exclude_unset=True)
        
        # Handle JSON fields
        if 'materials' in update_data and update_data['materials'] is not None:
            update_data['materials'] = json.dumps(update_data['materials'])
        if 'prerequisites' in update_data and update_data['prerequisites'] is not None:
            update_data['prerequisites'] = json.dumps(update_data['prerequisites'])
        if 'learning_objectives' in update_data and update_data['learning_objectives'] is not None:
            update_data['learning_objectives'] = json.dumps(update_data['learning_objectives'])
        
        # Validate dates if both are provided
        if 'start_date' in update_data and 'end_date' in update_data:
            if update_data['start_date'] >= update_data['end_date']:
                raise HTTPException(
                    status_code=400, 
                    detail="End date must be after start date"
                )
        
        for field, value in update_data.items():
            setattr(workshop, field, value)
        
        workshop.updated_at = datetime.now()
        
        db.commit()
        db.refresh(workshop)
        
        logger.info(f"Updated workshop {workshop.id} by user {current_user.id}")
        return workshop.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating workshop {workshop_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update workshop")

@router.delete("/api/workshops/{workshop_id}")
async def delete_workshop(
    workshop_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workshop"""
    try:
        workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
        if not workshop:
            raise HTTPException(status_code=404, detail="Workshop not found")
        
        # Check if user can delete (creator or admin)
        if workshop.created_by != current_user.id and current_user.user_type != 'admin':
            raise HTTPException(status_code=403, detail="Not authorized to delete this workshop")
        
        # Check if there are registrations
        registrations_count = db.query(WorkshopRegistration).filter(
            WorkshopRegistration.workshop_id == workshop_id
        ).count()
        
        if registrations_count > 0:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete workshop with existing registrations"
            )
        
        db.delete(workshop)
        db.commit()
        
        logger.info(f"Deleted workshop {workshop_id} by user {current_user.id}")
        return {"message": "Workshop deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting workshop {workshop_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete workshop")

# ========== REGISTRATION ROUTES ==========

@router.post("/api/registrations")
async def register_for_workshop(
    registration_data: WorkshopRegistrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register for a workshop"""
    try:
        # Check if workshop exists and is published
        workshop = db.query(Workshop).filter(Workshop.id == registration_data.workshop_id).first()
        if not workshop:
            raise HTTPException(status_code=404, detail="Workshop not found")
        
        if workshop.status != "published":
            raise HTTPException(status_code=400, detail="Workshop is not available for registration")
        
        # Check if user is already registered
        existing_registration = db.query(WorkshopRegistration).filter(
            and_(
                WorkshopRegistration.workshop_id == registration_data.workshop_id,
                WorkshopRegistration.user_id == current_user.id,
                WorkshopRegistration.status.in_(["registered", "completed"])
            )
        ).first()
        
        if existing_registration:
            raise HTTPException(status_code=400, detail="Already registered for this workshop")
        
        # Check capacity
        if workshop.max_participants:
            current_registrations = db.query(WorkshopRegistration).filter(
                and_(
                    WorkshopRegistration.workshop_id == registration_data.workshop_id,
                    WorkshopRegistration.status.in_(["registered", "completed"])
                )
            ).count()
            
            if current_registrations >= workshop.max_participants:
                raise HTTPException(status_code=400, detail="Workshop is full")
        
        # Create registration
        registration = WorkshopRegistration(
            workshop_id=registration_data.workshop_id,
            user_id=current_user.id,
            notes=registration_data.notes,
            payment_amount=workshop.price
        )
        
        db.add(registration)
        db.commit()
        db.refresh(registration)
        
        logger.info(f"User {current_user.id} registered for workshop {registration_data.workshop_id}")
        return registration.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering for workshop: {e}")
        raise HTTPException(status_code=500, detail="Failed to register for workshop")

@router.get("/api/registrations")
async def get_user_registrations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's workshop registrations"""
    try:
        registrations = db.query(WorkshopRegistration).filter(
            WorkshopRegistration.user_id == current_user.id
        ).order_by(desc(WorkshopRegistration.registration_date)).all()
        
        return [registration.to_dict() for registration in registrations]
    except Exception as e:
        logger.error(f"Error fetching user registrations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch registrations")

@router.get("/api/workshops/{workshop_id}/participants")
async def get_workshop_participants(
    workshop_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List participants for a workshop. Only the creator (HR) or admin can view."""
    try:
        workshop = db.query(Workshop).filter(Workshop.id == workshop_id).first()
        if not workshop:
            raise HTTPException(status_code=404, detail="Workshop not found")

        # Only creator or admin can view participants
        if workshop.created_by != current_user.id and getattr(current_user, 'user_type', '') != 'admin':
            raise HTTPException(status_code=403, detail="Not authorized to view participants")

        regs = db.query(WorkshopRegistration).filter(
            and_(
                WorkshopRegistration.workshop_id == workshop_id,
                WorkshopRegistration.status.in_(["registered", "completed"]) 
            )
        ).all()

        participant_ids = [r.user_id for r in regs]
        users = []
        if participant_ids:
            users = db.query(User).filter(User.id.in_(participant_ids)).all()

        data = [
            {
                "id": u.id,
                "full_name": getattr(u, 'full_name', None) or f"{getattr(u, 'first_name', '')} {getattr(u, 'last_name', '')}".strip(),
                "email": getattr(u, 'email', None),
                "username": getattr(u, 'username', None)
            }
            for u in users
        ]

        return {"participants": data, "count": len(data)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching workshop participants for {workshop_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch workshop participants")

@router.delete("/api/registrations/{registration_id}")
async def cancel_registration(
    registration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a workshop registration"""
    try:
        registration = db.query(WorkshopRegistration).filter(
            and_(
                WorkshopRegistration.id == registration_id,
                WorkshopRegistration.user_id == current_user.id
            )
        ).first()
        
        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        if registration.status == "cancelled":
            raise HTTPException(status_code=400, detail="Registration already cancelled")
        
        registration.status = "cancelled"
        db.commit()
        
        logger.info(f"User {current_user.id} cancelled registration {registration_id}")
        return {"message": "Registration cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error cancelling registration: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel registration")

# ========== UTILITY ROUTES ==========

@router.get("/api/categories")
async def get_categories():
    """Get available workshop categories"""
    return {
        "categories": [
            "technical",
            "soft-skills",
            "career",
            "leadership",
            "communication",
            "project-management",
            "data-science",
            "web-development",
            "mobile-development",
            "devops",
            "cybersecurity",
            "design",
            "marketing",
            "sales",
            "finance",
            "other"
        ]
    }

@router.get("/api/levels")
async def get_levels():
    """Get available workshop levels"""
    return {
        "levels": [
            "beginner",
            "intermediate",
            "advanced",
            "expert"
        ]
    }
