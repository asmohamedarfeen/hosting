import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from auth_utils import get_current_user
from models import User, Post, Comment, Connection, FriendRequest
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api", tags=["API"])

# Ensure uploads directory exists
UPLOADS_DIR = os.path.join("static", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Import connection-related functions
from connection_routes import get_filtered_connections, get_user_sent_requests

# Users API
@router.get("/v1/users")
async def get_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users with pagination"""
    try:
        users = db.query(User).offset(offset).limit(limit).all()
        
        # Format users for frontend
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "name": user.full_name,  # Add name field for compatibility
                "title": user.title or "Professional",
                "company": user.company or "Company",
                "location": user.location or "Location",
                "bio": user.bio or "",
                "profile_pic": user.profile_pic or "",
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            })
        
        return {"users": users_data}
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Error getting users")

# Posts API
@router.get("/posts")
async def get_posts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all posts for the home feed"""
    try:
        # Get posts from all users, ordered by creation date
        posts = db.query(Post).order_by(Post.created_at.desc()).limit(50).all()
        
        # Format posts for frontend
        formatted_posts = []
        for post in posts:
            # Get user info
            user = db.query(User).filter(User.id == post.user_id).first()
            if not user:
                continue
                
            # Get comments count
            comments_count = db.query(Comment).filter(Comment.post_id == post.id).count()
            
            # Get likes count (placeholder for now)
            likes_count = 0  # Will implement like system later
            shares_count = 0  # Will implement share system later
            
            formatted_post = {
                "id": post.id,
                "content": post.content,
                "post_type": post.post_type,
                "image_path": post.image_path,
                "video_path": post.video_path,
                "certificate_path": post.certificate_path,
                "created_at": post.created_at.isoformat(),
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "username": user.username,
                    "title": user.title,
                    "company": user.company,
                    "profile_image_url": user.get_profile_image_url()
                },
                "likes_count": likes_count,
                "comments_count": comments_count,
                "shares_count": shares_count
            }
            formatted_posts.append(formatted_post)
        
        return {
            "success": True,
            "posts": formatted_posts,
            "user_liked_posts": []  # Will implement like system later
        }
        
    except Exception as e:
        logger.error(f"Error getting posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load posts"
        )

@router.post("/posts")
async def create_post(
    content: str = Form(...),
    post_type: str = Form("general"),
    image: UploadFile = File(None),
    video: UploadFile = File(None),
    certificate: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new post with support for images, videos, and certificates"""
    try:
        # Validate content
        if not content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post content cannot be empty"
            )
        
        # Handle image upload if provided
        image_path = None
        if image:
            # Validate file type
            if not image.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only image files are allowed for image upload"
                )
            
            # Generate unique filename
            file_extension = os.path.splitext(image.filename)[1]
            filename = f"{uuid.uuid4()}{file_extension}"
            image_path = filename
            
            # Save file
            file_path = os.path.join(UPLOADS_DIR, filename)
            with open(file_path, "wb") as buffer:
                content_data = await image.read()
                buffer.write(content_data)
        
        # Handle video upload if provided
        video_path = None
        if video:
            # Validate file type
            if not video.content_type.startswith('video/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only video files are allowed for video upload"
                )
            
            # Generate unique filename
            file_extension = os.path.splitext(video.filename)[1]
            filename = f"{uuid.uuid4()}{file_extension}"
            video_path = filename
            
            # Save file
            file_path = os.path.join(UPLOADS_DIR, filename)
            with open(file_path, "wb") as buffer:
                content_data = await video.read()
                buffer.write(content_data)
        
        # Handle certificate upload if provided
        certificate_path = None
        if certificate:
            # Validate file type (PDF, DOC, DOCX, images)
            allowed_certificate_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/jpeg',
                'image/png',
                'image/gif'
            ]
            
            if certificate.content_type not in allowed_certificate_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only PDF, DOC, DOCX, and image files are allowed for certificates"
                )
            
            # Generate unique filename
            file_extension = os.path.splitext(certificate.filename)[1]
            filename = f"{uuid.uuid4()}{file_extension}"
            certificate_path = filename
            
            # Save file
            file_path = os.path.join(UPLOADS_DIR, filename)
            with open(file_path, "wb") as buffer:
                content_data = await certificate.read()
                buffer.write(content_data)
        
        # Create post
        new_post = Post(
            user_id=current_user.id,
            content=content.strip(),
            post_type=post_type,
            image_path=image_path,
            video_path=video_path,
            certificate_path=certificate_path,
            created_at=datetime.now()
        )
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        logger.info(f"User {current_user.username} created post {new_post.id} with type {post_type}")
        
        return {
            "success": True,
            "message": "Post created successfully",
            "post_id": new_post.id,
            "has_image": bool(image_path),
            "has_video": bool(video_path),
            "has_certificate": bool(certificate_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create post"
        )

@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like a post"""
    try:
        # Check if post exists
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # For now, just return success (like system will be implemented later)
        return {
            "success": True,
            "message": "Post liked successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to like post"
        )

@router.post("/posts/{post_id}/unlike")
async def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unlike a post"""
    try:
        # Check if post exists
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # For now, just return success (like system will be implemented later)
        return {
            "success": True,
            "message": "Post unliked successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unliking post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlike post"
        )

# Comments API
@router.get("/posts/{post_id}/comments")
async def get_post_comments(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comments for a specific post"""
    try:
        # Check if post exists
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Get comments
        comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.desc()).limit(20).all()
        
        # Format comments
        formatted_comments = []
        for comment in comments:
            user = db.query(User).filter(User.id == comment.user_id).first()
            if user:
                formatted_comments.append({
                    "id": comment.id,
                    "content": comment.content,
                    "created_at": comment.created_at.isoformat(),
                    "user": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "username": user.username,
                        "profile_image_url": user.get_profile_image_url()
                    }
                })
        
        return {
            "success": True,
            "comments": formatted_comments
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting comments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load comments"
        )

@router.post("/posts/{post_id}/comments")
async def create_comment(
    post_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a comment on a post"""
    try:
        # Check if post exists
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Get comment content from request body
        body = await request.json()
        content = body.get("content", "").strip()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment content cannot be empty"
            )
        
        # Create comment
        new_comment = Comment(
            post_id=post_id,
            user_id=current_user.id,
            content=content,
            created_at=datetime.now()
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        logger.info(f"User {current_user.username} commented on post {post_id}")
        
        return {
            "success": True,
            "message": "Comment added successfully",
            "comment_id": new_comment.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating comment: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add comment"
        )

# Connections API
@router.post("/connections/request")
async def send_connection_request(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a connection request to another user"""
    try:
        # Get receiver ID from request body
        body = await request.json()
        receiver_id = body.get("receiver_id")
        
        if not receiver_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Receiver ID is required"
            )
        
        # Check if receiver exists
        receiver = db.query(User).filter(User.id == receiver_id).first()
        if not receiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if trying to connect to self
        if receiver_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send connection request to yourself"
            )
        
        # Check if connection request already exists
        existing_request = db.query(FriendRequest).filter(
            (FriendRequest.sender_id == current_user.id) & (FriendRequest.receiver_id == receiver_id)
        ).first()
        
        if existing_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Connection request already sent"
            )
        
        # Check if already connected
        existing_connection = db.query(Connection).filter(
            ((Connection.user_id == current_user.id) & (Connection.connected_user_id == receiver_id)) |
            ((Connection.user_id == receiver_id) & (Connection.connected_user_id == current_user.id))
        ).first()
        
        if existing_connection:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already connected to this user"
            )
        
        # Create connection request
        new_request = FriendRequest(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            status="pending",
            created_at=datetime.now()
        )
        
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
        
        logger.info(f"User {current_user.username} sent connection request to {receiver.username}")
        
        return {
            "success": True,
            "message": "Connection request sent successfully",
            "request_id": new_request.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending connection request: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send connection request"
        )

@router.get("/connections/pending")
async def get_pending_connections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending connection requests for current user"""
    try:
        # Get pending requests where current user is the receiver
        pending_requests = db.query(FriendRequest).filter(
            (FriendRequest.receiver_id == current_user.id) & (FriendRequest.status == "pending")
        ).all()
        
        # Format requests
        formatted_requests = []
        for req in pending_requests:
            sender = db.query(User).filter(User.id == req.sender_id).first()
            if sender:
                formatted_requests.append({
                    "id": req.id,
                    "sender": {
                        "id": sender.id,
                        "full_name": sender.full_name,
                        "username": sender.username,
                        "title": sender.title,
                        "company": sender.company,
                        "profile_image_url": sender.get_profile_image_url()
                    },
                    "created_at": req.created_at.isoformat()
                })
        
        return {
            "success": True,
            "pending_requests": formatted_requests
        }
        
    except Exception as e:
        logger.error(f"Error getting pending connections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load pending connections"
        )

@router.post("/connections/{request_id}/accept")
async def accept_connection_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept a connection request"""
    try:
        # Get the request
        friend_request = db.query(FriendRequest).filter(
            (FriendRequest.id == request_id) & (FriendRequest.receiver_id == current_user.id)
        ).first()
        
        if not friend_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection request not found"
            )
        
        if friend_request.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request is not pending"
            )
        
        # Update request status
        friend_request.status = "accepted"
        friend_request.updated_at = datetime.now()
        
        # Create connection
        new_connection = Connection(
            user_id=friend_request.sender_id,
            connected_user_id=friend_request.receiver_id,
            status="accepted",
            created_at=datetime.now()
        )
        
        db.add(new_connection)
        db.commit()
        
        logger.info(f"User {current_user.username} accepted connection request from {friend_request.sender_id}")
        
        return {
            "success": True,
            "message": "Connection request accepted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting connection request: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept connection request"
        )

@router.post("/connections/{request_id}/reject")
async def reject_connection_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a connection request"""
    try:
        # Get the request
        friend_request = db.query(FriendRequest).filter(
            (FriendRequest.id == request_id) & (FriendRequest.receiver_id == current_user.id)
        ).first()
        
        if not friend_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connection request not found"
            )
        
        if friend_request.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request is not pending"
            )
        
        # Update request status
        friend_request.status = "rejected"
        friend_request.updated_at = datetime.now()
        
        db.commit()
        
        logger.info(f"User {current_user.username} rejected connection request from {friend_request.sender_id}")
        
        return {
            "success": True,
            "message": "Connection request rejected successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting connection request: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject connection request"
        )

# ==================== CONNECTION API ROUTES ====================

@router.get("/connections/current")
async def get_current_connections(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current accepted connections"""
    try:
        connections = await get_filtered_connections(
            current_user.id, db, page, limit, "name", None, None, None
        )
        
        return connections
        
    except Exception as e:
        logger.error(f"Error getting current connections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get current connections"
        )

@router.get("/connections/sent")
async def get_sent_connections(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's sent connection requests"""
    try:
        sent_requests = await get_user_sent_requests(current_user.id, db, page, limit)
        return sent_requests
        
    except Exception as e:
        logger.error(f"Error getting sent connections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get sent connections"
        )
