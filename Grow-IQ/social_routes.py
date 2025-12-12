import os
import time
import logging
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename
from passlib.context import CryptContext
from database_enhanced import get_db
from auth_utils import get_current_user
from models import (
    User, Post, PostLike, Job, Notification, Connection, FriendRequest, 
    Event, EventRegistration, Comment
)
from datetime import datetime, timedelta
import re
from sqlalchemy import or_, and_

# Initialize router
router = APIRouter(prefix="/social", tags=["social"])

# Initialize password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Get upload folder from app context
def get_upload_folder():
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(BASE_DIR, 'static', 'uploads')

def extract_domain(email):
    """Extract domain from email address"""
    if '@' in email:
        return email.split('@')[1].lower()
    return None

def is_company_domain(domain):
    """Check if domain is likely a company domain (not free email provider)"""
    free_domains = {
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
        'icloud.com', 'protonmail.com', 'mail.com', 'yandex.com', 'zoho.com'
    }
    return domain not in free_domains

# ==================== FRIEND REQUESTS ====================

@router.post("/friend-request/send")
async def send_friend_request(
    receiver_id: int = Form(...),
    message: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a friend request to another user"""
    try:
        receiver = db.query(User).get(receiver_id)
        if not receiver:
            raise HTTPException(status_code=404, detail="User not found.")
        
        if current_user.id == receiver.id:
            raise HTTPException(status_code=400, detail="Cannot send friend request to yourself.")
        
        # Check if request already exists
        existing_request = db.query(FriendRequest).filter(
            FriendRequest.sender_id == current_user.id,
            FriendRequest.receiver_id == receiver.id
        ).first()
        
        if existing_request:
            if existing_request.status == 'pending':
                raise HTTPException(status_code=400, detail="Friend request already sent.")
            elif existing_request.status == 'accepted':
                raise HTTPException(status_code=400, detail="You are already friends.")
        
        # Create friend request
        friend_request = FriendRequest(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            message=message
        )
        
        db.add(friend_request)
        
        # Create notification
        notification = Notification(
            user_id=receiver.id,
            title="New Friend Request",
            message=f"{current_user.full_name} sent you a friend request",
            notification_type="friend_request",
            related_id=friend_request.id,
            related_type="friend_request"
        )
        
        db.add(notification)
        db.commit()
        
        return {"message": "Friend request sent successfully!", "status": "success"}
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error sending friend request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending friend request: {str(e)}")

@router.post("/friend-request/{request_id}/respond")
async def respond_to_friend_request(
    request_id: int,
    response: str = Form(...),  # "accept", "decline"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Respond to a friend request (accept/decline)"""
    try:
        friend_request = db.query(FriendRequest).filter(
            FriendRequest.id == request_id,
            FriendRequest.receiver_id == current_user.id
        ).first()
        
        if not friend_request:
            raise HTTPException(status_code=404, detail="Friend request not found.")
        
        if friend_request.status != 'pending':
            raise HTTPException(status_code=400, detail="Friend request already responded to.")
        
        if response == "accept":
            friend_request.status = 'accepted'
            friend_request.responded_at = datetime.utcnow()
            
            # Create professional connection
            connection = Connection(
                user_id=friend_request.sender_id,
                connected_user_id=friend_request.receiver_id,
                status='accepted',
                connection_type='personal',
                accepted_at=datetime.utcnow()
            )
            
            db.add(connection)
            
            # Create notification for sender
            notification = Notification(
                user_id=friend_request.sender_id,
                title="Friend Request Accepted",
                message=f"{current_user.full_name} accepted your friend request",
                notification_type="friend_request",
                related_id=friend_request.id,
                related_type="friend_request"
            )
            
            db.add(notification)
            
        elif response == "decline":
            friend_request.status = 'declined'
            friend_request.responded_at = datetime.utcnow()
            
            # Create notification for sender
            notification = Notification(
                user_id=friend_request.sender_id,
                title="Friend Request Declined",
                message=f"{current_user.full_name} declined your friend request",
                notification_type="friend_request",
                related_id=friend_request.id,
                related_type="friend_request"
            )
            
            db.add(notification)
        
        db.commit()
        return {"message": f"Friend request {response}ed successfully!", "status": "success"}
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error responding to friend request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error responding to friend request: {str(e)}")

@router.get("/friend-requests")
async def get_friend_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending friend requests for current user"""
    try:
        # Get pending friend requests where current user is the receiver
        # Use manual join to avoid relationship issues
        requests = db.query(FriendRequest, User).join(
            User, FriendRequest.sender_id == User.id
        ).filter(
            FriendRequest.receiver_id == current_user.id,
            FriendRequest.status == 'pending'
        ).all()
        
        # Format requests for frontend
        formatted_requests = []
        for request, sender in requests:
            formatted_request = {
                "id": request.id,
                "message": request.message,
                "created_at": request.created_at.isoformat(),
                "sender": {
                    "id": sender.id,
                    "full_name": sender.full_name,
                    "title": sender.title,
                    "company": sender.company,
                    "profile_image": sender.profile_image
                }
            }
            formatted_requests.append(formatted_request)
        
        return formatted_requests
        
    except Exception as e:
        logging.error(f"Error fetching friend requests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching friend requests: {str(e)}")

@router.get("/connection-suggestions")
async def get_connection_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """Get connection suggestions for current user"""
    try:
        # Get users who are not already connected or have pending requests
        subquery = db.query(Connection.connected_user_id).filter(
            Connection.user_id == current_user.id
        ).union(
            db.query(Connection.user_id).filter(
                Connection.connected_user_id == current_user.id
            )
        ).subquery()
        
        friend_request_subquery = db.query(FriendRequest.receiver_id).filter(
            FriendRequest.sender_id == current_user.id
        ).union(
            db.query(FriendRequest.sender_id).filter(
                FriendRequest.receiver_id == current_user.id
            )
        ).subquery()
        
        suggestions = db.query(User).filter(
            User.id != current_user.id,
            ~User.id.in_(subquery),
            ~User.id.in_(friend_request_subquery)
        ).limit(limit).all()
        
        # Format suggestions for frontend
        formatted_suggestions = []
        for suggestion in suggestions:
            formatted_suggestion = {
                "id": suggestion.id,
                "full_name": suggestion.full_name,
                "title": suggestion.title,
                "company": suggestion.company,
                "location": suggestion.location,
                "profile_image": suggestion.profile_image,
                "mutual_connections": 0  # TODO: Implement mutual connections calculation
            }
            formatted_suggestions.append(formatted_suggestion)
        
        return formatted_suggestions
        
    except Exception as e:
        logging.error(f"Error fetching connection suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching connection suggestions: {str(e)}")

@router.get("/search-people")
async def search_people(
    q: str = Query(..., description="Search query"),
    location: Optional[str] = Query(None, description="Location filter"),
    industry: Optional[str] = Query(None, description="Industry filter"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100)
):
    """Search for people to connect with"""
    try:
        # Build search query
        query = db.query(User).filter(User.id != current_user.id)
        
        # Add search filters
        if q:
            search_term = f"%{q}%"
            query = query.filter(or_(
                User.full_name.ilike(search_term),
                User.title.ilike(search_term),
                User.company.ilike(search_term),
                User.skills.ilike(search_term)
            ))
        
        if location:
            query = query.filter(User.location.ilike(f"%{location}%"))
        
        if industry:
            query = query.filter(User.industry.ilike(f"%{industry}%"))
        
        # Exclude already connected users
        subquery = db.query(Connection.connected_user_id).filter(
            Connection.user_id == current_user.id
        ).union(
            db.query(Connection.user_id).filter(
                Connection.connected_user_id == current_user.id
            )
        ).subquery()
        
        query = query.filter(~User.id.in_(subquery))
        
        # Get results
        results = query.limit(limit).all()
        
        # Format results for frontend
        formatted_results = []
        for result in results:
            formatted_result = {
                "id": result.id,
                "full_name": result.full_name,
                "title": result.title,
                "company": result.company,
                "location": result.location,
                "profile_image": result.profile_image,
                "mutual_connections": 0  # TODO: Implement mutual connections calculation
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
        
    except Exception as e:
        logging.error(f"Error searching people: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching people: {str(e)}")

# ==================== EVENTS (Domain Users Only) ====================

@router.post("/events/create")
async def create_event(
    title: str = Form(...),
    description: str = Form(...),
    event_type: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    location: str = Form(...),
    is_virtual: bool = Form(False),
    meeting_link: str = Form(""),
    max_participants: int = Form(None),
    registration_required: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Create a new event (domain users only)"""
    try:
        user = db.query(User).first()
        if not user:
            raise HTTPException(status_code=401, detail="Please log in.")
        
        if not user.can_host_events():
            raise HTTPException(status_code=403, detail="Only verified domain users can host events.")
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if start_dt >= end_dt:
            raise HTTPException(status_code=400, detail="End date must be after start date.")
        
        event = Event(
            title=title,
            description=description,
            event_type=event_type,
            start_date=start_dt,
            end_date=end_dt,
            location=location,
            is_virtual=is_virtual,
            meeting_link=meeting_link,
            max_participants=max_participants,
            registration_required=registration_required,
            organizer_id=user.id
        )
        
        db.add(event)
        db.commit()
        
        return {"message": "Event created successfully!", "event_id": event.id, "status": "success"}
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating event: {str(e)}")

@router.get("/events")
async def get_events(
    event_type: Optional[str] = Query(None),
    is_virtual: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all active events with optional filtering"""
    try:
        query = db.query(Event).filter(Event.is_active == True)
        
        if event_type:
            query = query.filter(Event.event_type == event_type)
        
        if is_virtual is not None:
            query = query.filter(Event.is_virtual == is_virtual)
        
        events = query.order_by(Event.start_date.asc()).all()
        
        events_data = []
        for event in events:
            organizer = db.query(User).get(event.organizer_id)
            events_data.append({
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "event_type": event.event_type,
                "start_date": event.start_date,
                "end_date": event.end_date,
                "location": event.location,
                "is_virtual": event.is_virtual,
                "meeting_link": event.meeting_link,
                "max_participants": event.max_participants,
                "current_participants": event.current_participants,
                "registration_required": event.registration_required,
                "organizer": {
                    "id": organizer.id,
                    "full_name": organizer.full_name,
                    "company": organizer.company
                }
            })
        
        return {"events": events_data}
        
    except Exception as e:
        logging.error(f"Error getting events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting events: {str(e)}")

@router.post("/events/{event_id}/register")
async def register_for_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Register for an event"""
    try:
        user = db.query(User).first()
        if not user:
            raise HTTPException(status_code=401, detail="Please log in.")
        
        event = db.query(Event).get(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found.")
        
        if not event.is_active:
            raise HTTPException(status_code=400, detail="Event is not active.")
        
        # Check if already registered
        existing_registration = db.query(EventRegistration).filter(
            EventRegistration.event_id == event_id,
            EventRegistration.user_id == user.id
        ).first()
        
        if existing_registration:
            raise HTTPException(status_code=400, detail="Already registered for this event.")
        
        # Check if event is full
        if event.max_participants and event.current_participants >= event.max_participants:
            raise HTTPException(status_code=400, detail="Event is full.")
        
        registration = EventRegistration(
            event_id=event_id,
            user_id=user.id
        )
        
        db.add(registration)
        
        # Update participant count
        event.current_participants += 1
        
        db.commit()
        
        return {"message": "Successfully registered for event!", "status": "success"}
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error registering for event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error registering for event: {str(e)}")

# ==================== ENHANCED POSTS ====================

@router.post("/posts/create")
async def create_post(
    content: str = Form(...),
    post_type: str = Form("general"),
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    certificate: Optional[UploadFile] = File(None),
    is_public: bool = Form(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new post with support for images, videos, and certificates"""
    try:
        if not current_user.can_post_content():
            raise HTTPException(status_code=403, detail="You cannot post content.")
        
        # Handle image upload
        image_path = None
        if image and image.filename:
            if allowed_file(image.filename):
                filename = str(uuid.uuid4()) + '.' + image.filename.rsplit('.', 1)[1].lower()
                file_path = os.path.join(get_upload_folder(), filename)
                
                # Save file
                with open(file_path, "wb") as buffer:
                    content_data = await image.read()
                    buffer.write(content_data)
                
                image_path = filename
            else:
                raise HTTPException(status_code=400, detail="Invalid image file type")
        
        # Handle video upload
        video_path = None
        if video and video.filename:
            if video.content_type.startswith('video/'):
                filename = str(uuid.uuid4()) + '.' + video.filename.rsplit('.', 1)[1].lower()
                file_path = os.path.join(get_upload_folder(), filename)
                
                # Save file
                with open(file_path, "wb") as buffer:
                    content_data = await video.read()
                    buffer.write(content_data)
                
                video_path = filename
            else:
                raise HTTPException(status_code=400, detail="Invalid video file type")
        
        # Handle certificate upload
        certificate_path = None
        if certificate and certificate.filename:
            allowed_certificate_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/jpeg',
                'image/png',
                'image/gif'
            ]
            
            if certificate.content_type in allowed_certificate_types:
                filename = str(uuid.uuid4()) + '.' + certificate.filename.rsplit('.', 1)[1].lower()
                file_path = os.path.join(get_upload_folder(), filename)
                
                # Save file
                with open(file_path, "wb") as buffer:
                    content_data = await certificate.read()
                    buffer.write(content_data)
                
                certificate_path = filename
            else:
                raise HTTPException(status_code=400, detail="Invalid certificate file type")
        
        post = Post(
            content=content,
            image_path=image_path,
            video_path=video_path,
            certificate_path=certificate_path,
            post_type=post_type,
            is_public=is_public,
            user_id=current_user.id
        )
        
        db.add(post)
        db.commit()
        
        return {
            "message": "Post created successfully!", 
            "post_id": post.id, 
            "status": "success",
            "has_image": bool(image_path),
            "has_video": bool(video_path),
            "has_certificate": bool(certificate_path)
        }
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating post: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating post: {str(e)}")

@router.get("/posts")
async def get_posts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get posts for the current user's feed"""
    try:
        # Get posts with author information
        posts = db.query(Post).join(User, Post.user_id == User.id).filter(
            Post.is_public == True
        ).order_by(Post.created_at.desc()).offset(offset).limit(limit).all()
        
        # Format posts for frontend (include likes and whether current user liked)
        formatted_posts = []
        for post in posts:
            likes_count = db.query(PostLike).filter(PostLike.post_id == post.id).count()
            comments_count = db.query(Comment).filter(Comment.post_id == post.id).count()
            is_liked = db.query(PostLike).filter(PostLike.post_id == post.id, PostLike.user_id == current_user.id).first() is not None
            author = post.author
            formatted_post = {
                "id": post.id,
                "content": post.content,
                "image_path": post.image_path,
                "video_path": post.video_path,
                "certificate_path": post.certificate_path,
                "post_type": post.post_type,
                "is_public": post.is_public,
                "created_at": post.created_at.isoformat(),
                "author": {
                    "id": author.id,
                    "full_name": author.full_name,
                    "title": author.title,
                    "company": author.company,
                    "profile_image": author.profile_image,
                    "profile_pic": author.profile_pic,
                    "profile_image_url": author.get_profile_pic_url() if hasattr(author, 'get_profile_pic_url') else None
                },
                "likes_count": likes_count,
                "comments_count": comments_count,
                "shares_count": 0,
                "is_liked": is_liked
            }
            formatted_posts.append(formatted_post)
        
        return formatted_posts
        
    except Exception as e:
        logging.error(f"Error fetching posts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {str(e)}")

# ==================== COMMENTS ====================
@router.get("/posts/{post_id}/comments")
async def list_comments(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()
        result = []
        for c in comments:
            author = db.query(User).get(c.user_id)
            result.append({
                "id": c.id,
                "content": c.content,
                "created_at": c.created_at.isoformat(),
                "author": {
                    "id": author.id,
                    "full_name": author.full_name,
                    "profile_image": author.profile_image
                }
            })
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error listing comments: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listing comments")

@router.post("/posts/{post_id}/comments")
async def create_comment(
    post_id: int,
    content: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if not content or not content.strip():
            raise HTTPException(status_code=400, detail="Comment cannot be empty")
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        comment = Comment(content=content.strip(), post_id=post_id, user_id=current_user.id)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        count = db.query(Comment).filter(Comment.post_id == post_id).count()
        return {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at.isoformat(),
            "comments_count": count
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating comment: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating comment")


@router.post("/posts/{post_id}/like")
async def toggle_like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle like for a post; each user can like at most once.
    Returns the new like state and total count."""
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        existing = db.query(PostLike).filter(
            PostLike.post_id == post_id,
            PostLike.user_id == current_user.id
        ).first()

        if existing:
            db.delete(existing)
            db.commit()
            new_state = False
        else:
            like = PostLike(post_id=post_id, user_id=current_user.id)
            db.add(like)
            db.commit()
            new_state = True

        total = db.query(PostLike).filter(PostLike.post_id == post_id).count()
        # Optionally mirror into posts.likes_count for fast lookup
        post.likes_count = total
        db.commit()

        return {"post_id": post_id, "is_liked": new_state, "likes_count": total}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error toggling like: {str(e)}")
        raise HTTPException(status_code=500, detail="Error toggling like")

# ==================== ENHANCED JOBS (Domain Users Only) ====================
# Job functionality moved to job_routes.py to avoid conflicts

# ==================== USER MANAGEMENT & DOMAIN VERIFICATION ====================

@router.post("/users/verify-domain")
async def verify_domain_email(
    email: str = Form(...),
    company_name: str = Form(...),
    verification_code: str = Form(...),
    db: Session = Depends(get_db)
):
    """Verify domain email and upgrade user to domain user"""
    try:
        user = db.query(User).first()
        if not user:
            raise HTTPException(status_code=401, detail="Please log in.")
        
        if user.email != email:
            raise HTTPException(status_code=400, detail="Email does not match your account.")
        
        domain = extract_domain(email)
        if not domain or not is_company_domain(domain):
            raise HTTPException(status_code=400, detail="Please use a company email address.")
        
        # In a real app, you would verify the verification code
        # For demo purposes, we'll just check if it's not empty
        if not verification_code:
            raise HTTPException(status_code=400, detail="Invalid verification code.")
        
        # Upgrade user to domain user
        user.user_type = 'domain'
        user.domain = domain
        user.company = company_name
        user.is_verified = True
        
        db.commit()
        
        return {
            "message": "Domain verified successfully! You can now post jobs and host events.",
            "user_type": user.user_type,
            "status": "success"
        }
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error verifying domain: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error verifying domain: {str(e)}")

@router.get("/users/profile/{user_id}")
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile information"""
    try:
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        
        # Get user's posts
        posts = db.query(Post).filter(
            Post.user_id == user.id,
            Post.is_public == True
        ).order_by(Post.created_at.desc()).limit(5).all()
        
        # Get user's connections count
        connections_count = db.query(Connection).filter(
            Connection.user_id == user.id,
            Connection.status == 'accepted'
        ).count()
        
        profile_data = {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "title": user.title,
            "company": user.company,
            "location": user.location,
            "bio": user.bio,
            "profile_image": user.profile_image,
            "user_type": user.user_type,
            "is_verified": user.is_verified,
            "domain": user.domain,
            "created_at": user.created_at,
            "posts": [
                {
                    "id": post.id,
                    "content": post.content,
                    "post_type": post.post_type,
                    "created_at": post.created_at,
                    "likes_count": post.likes_count
                } for post in posts
            ],
            "connections_count": connections_count
        }
        
        return profile_data
        
    except Exception as e:
        logging.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting user profile: {str(e)}")

# ==================== SEARCH & DISCOVERY ====================

@router.get("/search/users")
async def search_users(
    query: str = Query(...),
    user_type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Search for users by name, title, company, or location"""
    try:
        search_query = db.query(User)
        
        # Basic search in name, title, company, bio
        search_terms = query.split()
        for term in search_terms:
            search_query = search_query.filter(
                (User.full_name.ilike(f'%{term}%')) |
                (User.title.ilike(f'%{term}%')) |
                (User.company.ilike(f'%{term}%')) |
                (User.bio.ilike(f'%{term}%'))
            )
        
        if user_type:
            search_query = search_query.filter(User.user_type == user_type)
        
        if location:
            search_query = search_query.filter(User.location.ilike(f'%{location}%'))
        
        users = search_query.limit(20).all()
        
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "full_name": user.full_name,
                "title": user.title,
                "company": user.company,
                "location": user.location,
                "profile_image": user.profile_image,
                "user_type": user.user_type,
                "is_verified": user.is_verified
            })
        
        return {"users": users_data, "total": len(users_data)}
        
    except Exception as e:
        logging.error(f"Error searching users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching users: {str(e)}")

@router.get("/search/jobs")
async def search_jobs(
    query: str = Query(...),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Search for jobs by title, company, or description"""
    try:
        search_query = db.query(Job).filter(Job.is_active == True)
        
        # Basic search in title, company, description
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
                "posted_by": {
                    "id": posted_by.id,
                    "full_name": posted_by.full_name,
                    "company": posted_by.company
                }
            })
        
        return {"jobs": jobs_data, "total": len(jobs_data)}
        
    except Exception as e:
        logging.error(f"Error searching jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")

@router.get("/connections")
async def get_connections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's connections"""
    try:
        # Get accepted connections
        connections = db.query(User).join(Connection, or_(
            and_(Connection.user_id == current_user.id, Connection.connected_user_id == User.id),
            and_(Connection.connected_user_id == current_user.id, Connection.user_id == User.id)
        )).filter(Connection.status == 'accepted').all()
        
        # Format connections for frontend
        formatted_connections = []
        for connection in connections:
            formatted_connection = {
                "id": connection.id,
                "full_name": connection.full_name,
                "title": connection.title,
                "company": connection.company,
                "location": connection.location,
                "profile_image": connection.profile_image
            }
            formatted_connections.append(formatted_connection)
        
        return formatted_connections
        
    except Exception as e:
        logging.error(f"Error fetching connections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching connections: {str(e)}")

