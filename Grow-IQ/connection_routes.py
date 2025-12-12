import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from database import get_db
from models import User, Connection, FriendRequest, Notification, Post
from auth_utils import get_user_from_session
from datetime import datetime, timedelta
import os

# Initialize router
router = APIRouter(prefix="/connections", tags=["connections"])

def get_authenticated_user_id(request: Request, db: Session) -> int:
    """Get authenticated user ID from session token"""
    session_token = request.cookies.get('session_token')
    if not session_token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_data = get_user_from_session(session_token, db)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    return user_data['user_id']

# Test route
@router.get("/test")
def test_connection_route():
    """Test route to verify the connection router is working"""
    return {"message": "Connection router is working!", "status": "success"}

# Debug authentication route
@router.get("/debug-auth")
async def debug_auth(request: Request, db: Session = Depends(get_db)):
    """Debug authentication"""
    try:
        session_token = request.cookies.get('session_token')
        if not session_token:
            return {"error": "No session token found"}
        
        user_data = get_user_from_session(session_token, db)
        if not user_data:
            return {"error": "Invalid session token"}
        
        return {"success": True, "user_id": user_data['user_id'], "token": session_token[:20] + "..."}
    except Exception as e:
        return {"error": str(e)}

# Debug route
@router.get("/debug")
def debug_connection_route():
    """Debug route to see what's happening"""
    return {"message": "Debug route working", "routes": ["/", "/test", "/debug"]}

# Get templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ==================== CONNECTION MANAGEMENT ====================

@router.get("/", response_class=HTMLResponse)
def connections_page(request: Request, db: Session = Depends(get_db)):
    """Redirect to the React network page"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/network", status_code=307)

@router.get("/api/stats")
async def get_connection_stats(request: Request, db: Session = Depends(get_db)):
    """Get user's connection statistics"""
    try:
        user_id = get_authenticated_user_id(request, db)
        
        stats = await calculate_connection_stats(user_id, db)
        return JSONResponse(content=stats)
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 401) without wrapping them
        raise
    except Exception as e:
        logging.error(f"Error getting connection stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting connection stats")

@router.get("/api/connections")
async def get_connections(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("name", regex="^(name|company|recent|mutual)$"),
    search: Optional[str] = Query(None),
    company_filter: Optional[str] = Query(None),
    location_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get user's connections with pagination, sorting, and filtering"""
    try:
        user_id = get_authenticated_user_id(request, db)
        
        connections = await get_filtered_connections(
            user_id, db, page, limit, sort_by, search, company_filter, location_filter
        )
        
        return JSONResponse(content=connections)
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 401) without wrapping them
        raise
    except Exception as e:
        logging.error(f"Error getting connections: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting connections")

@router.get("/api/pending-requests")
async def get_pending_requests(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get pending connection requests for the user"""
    try:
        user_id = get_authenticated_user_id(request, db)
        
        pending_requests = await get_user_pending_requests(user_id, db, page, limit)
        return JSONResponse(content=pending_requests)
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 401) without wrapping them
        raise
    except Exception as e:
        logging.error(f"Error getting pending requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting pending requests")

@router.get("/api/stats")
async def get_connection_stats(request: Request, db: Session = Depends(get_db)):
    """Get user's connection statistics"""
    try:
        user_id = get_authenticated_user_id(request, db)
        
        stats = await calculate_connection_stats(user_id, db)
        return JSONResponse(content=stats)
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 401) without wrapping them
        raise
    except Exception as e:
        logging.error(f"Error getting connection stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting connection stats")

@router.get("/api/connections")
async def get_connections(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("name", regex="^(name|company|recent|mutual)$"),
    search: Optional[str] = Query(None),
    company_filter: Optional[str] = Query(None),
    location_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get user's connections with pagination, sorting, and filtering"""
    try:
        user_id = get_authenticated_user_id(request, db)
        
        connections = await get_filtered_connections(
            user_id, db, page, limit, sort_by, search, company_filter, location_filter
        )
        
        return JSONResponse(content=connections)
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 401) without wrapping them
        raise
    except Exception as e:
        logging.error(f"Error getting connections: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting connections")



@router.get("/api/pending-requests")
async def get_pending_requests(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get pending connection requests for the user"""
    try:
        user_id = get_authenticated_user_id(request, db)
        
        pending_requests = await get_user_pending_requests(user_id, db, page, limit)
        return JSONResponse(content=pending_requests)
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 401) without wrapping them
        raise
    except Exception as e:
        logging.error(f"Error getting pending requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting pending requests")

@router.get("/api/sent-requests")
async def get_sent_requests(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get sent connection requests by the user"""
    try:
        user_id = get_authenticated_user_id(request, db)
        
        sent_requests = await get_user_sent_requests(user_id, db, page, limit)
        return JSONResponse(content=sent_requests)
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 401) without wrapping them
        raise
    except Exception as e:
        logging.error(f"Error getting sent requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting sent requests")

@router.get("/api/suggestions")
async def get_connection_suggestions(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get connection suggestions for the user"""
    try:
        user_id = get_authenticated_user_id(request, db)
        
        suggestions = get_connection_suggestions_for_user(user_id, db, page, limit)
        return JSONResponse(content=suggestions)
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 401) without wrapping them
        raise
    except Exception as e:
        logging.error(f"Error getting connection suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting connection suggestions")

# ==================== CONNECTION REQUESTS ====================

@router.post("/api/request")
async def send_connection_request_json(
    request: Request,
    db: Session = Depends(get_db)
):
    """Send a connection request to another user (JSON endpoint)"""
    try:
        # Parse JSON body
        body = await request.json()
        receiver_id = body.get("receiver_id")
        message = body.get("message", "")
        
        if not receiver_id:
            raise HTTPException(status_code=400, detail="receiver_id is required")
        
        sender_id = get_authenticated_user_id(request, db)
        
        if sender_id == receiver_id:
            raise HTTPException(status_code=400, detail="Cannot send connection request to yourself")
        
        # Check if user exists (SQLAlchemy 2.x compatible)
        receiver = db.get(User, receiver_id)
        if not receiver:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if already connected
        existing_connection = db.query(Connection).filter(
            or_(
                and_(Connection.user_id == sender_id, Connection.connected_user_id == receiver_id),
                and_(Connection.user_id == receiver_id, Connection.connected_user_id == sender_id)
            ),
            Connection.status == 'accepted'
        ).first()
        
        if existing_connection:
            raise HTTPException(status_code=400, detail="Already connected with this user")
        
        # Check if request already exists
        existing_request = db.query(FriendRequest).filter(
            FriendRequest.sender_id == sender_id,
            FriendRequest.receiver_id == receiver_id,
            FriendRequest.status == 'pending'
        ).first()
        
        if existing_request:
            raise HTTPException(status_code=400, detail="Connection request already sent")
        
        # Create connection request
        friend_request = FriendRequest(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message,
            status='pending'
        )
        
        db.add(friend_request)
        
        # Create notification
        notification = Notification(
            user_id=receiver_id,
            title="New Connection Request",
            message=f"{(db.get(User, sender_id).full_name if db.get(User, sender_id) else 'Someone')} sent you a connection request",
            notification_type="connection_request",
            related_id=friend_request.id,
            related_type="friend_request"
        )
        
        db.add(notification)
        db.commit()
        
        return JSONResponse(content={
            "message": "Connection request sent successfully",
            "status": "success",
            "request_id": friend_request.id
        })
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error sending connection request: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending connection request")

@router.post("/api/accept/{user_id}")
async def accept_connection_by_user_id(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Accept a connection request from a specific user"""
    try:
        current_user_id = get_authenticated_user_id(request, db)
        
        # Find the pending friend request from this user
        friend_request = db.query(FriendRequest).filter(
            FriendRequest.sender_id == user_id,
            FriendRequest.receiver_id == current_user_id,
            FriendRequest.status == 'pending'
        ).first()
        
        if not friend_request:
            raise HTTPException(status_code=404, detail="No pending connection request from this user")
        
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
        
        # Create notification
        notification = Notification(
            user_id=user_id,
            title="Connection Request Accepted",
            message=f"{db.query(User).get(current_user_id).full_name} accepted your connection request",
            notification_type="connection_accepted",
            related_id=new_connection.id,
            related_type="connection"
        )
        
        db.add(notification)
        db.commit()
        
        return JSONResponse(content={
            "message": "Connection request accepted successfully",
            "status": "success",
            "connection_id": new_connection.id
        })
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error accepting connection request: {str(e)}")
        raise HTTPException(status_code=500, detail="Error accepting connection request")

@router.get("/accepted")
async def get_accepted_connections(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all accepted connections for the current user"""
    try:
        current_user_id = get_authenticated_user_id(request, db)
        
        # Get accepted connections
        connections = db.query(Connection, User).join(
            User, Connection.connected_user_id == User.id
        ).filter(
            Connection.user_id == current_user_id,
            Connection.status == 'accepted'
        ).all()
        
        # Format connection data
        connection_data = []
        for conn, user in connections:
            connection_data.append({
                "id": conn.id,
                "user_id": user.id,
                "full_name": user.full_name,
                "title": user.title,
                "company": user.company,
                "location": user.location,
                "profile_image": user.profile_image,
                "connected_since": conn.created_at.isoformat() if conn.created_at else None,
                "status": conn.status
            })
        
        return JSONResponse(content={
            "status": "success",
            "connections": connection_data,
            "total_count": len(connection_data)
        })
        
    except Exception as e:
        logging.error(f"Error getting accepted connections: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting accepted connections")

@router.post("/api/send-request")
async def send_connection_request(
    request: Request,
    receiver_id: int = Form(...),
    message: str = Form(""),
    db: Session = Depends(get_db)
):
    """Send a connection request to another user"""
    try:
        sender_id = get_authenticated_user_id(request, db)
        
        if sender_id == receiver_id:
            raise HTTPException(status_code=400, detail="Cannot send connection request to yourself")
        
        # Check if user exists
        receiver = db.query(User).get(receiver_id)
        if not receiver:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if already connected
        existing_connection = db.query(Connection).filter(
            or_(
                and_(Connection.user_id == sender_id, Connection.connected_user_id == receiver_id),
                and_(Connection.user_id == receiver_id, Connection.connected_user_id == sender_id)
            ),
            Connection.status == 'accepted'
        ).first()
        
        if existing_connection:
            raise HTTPException(status_code=400, detail="Already connected with this user")
        
        # Check if request already exists
        existing_request = db.query(FriendRequest).filter(
            FriendRequest.sender_id == sender_id,
            FriendRequest.receiver_id == receiver_id,
            FriendRequest.status == 'pending'
        ).first()
        
        if existing_request:
            raise HTTPException(status_code=400, detail="Connection request already sent")
        
        # Create connection request
        friend_request = FriendRequest(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message,
            status='pending'
        )
        
        db.add(friend_request)
        
        # Create notification
        notification = Notification(
            user_id=receiver_id,
            title="New Connection Request",
            message=f"{db.query(User).get(sender_id).full_name} sent you a connection request",
            notification_type="connection_request",
            related_id=friend_request.id,
            related_type="friend_request"
        )
        
        db.add(notification)
        db.commit()
        
        return JSONResponse(content={
            "message": "Connection request sent successfully",
            "status": "success",
            "request_id": friend_request.id
        })
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error sending connection request: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending connection request")
        
        db.add(friend_request)
        
        # Create notification
        notification = Notification(
            user_id=receiver_id,
            title="New Connection Request",
            message=f"{db.query(User).get(sender_id).full_name} sent you a connection request",
            notification_type="connection_request",
            related_id=friend_request.id,
            related_type="friend_request"
        )
        
        db.add(notification)
        db.commit()
        
        return JSONResponse(content={
            "message": "Connection request sent successfully",
            "status": "success",
            "request_id": friend_request.id
        })
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error sending connection request: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending connection request")

@router.post("/api/respond-request")
async def respond_to_connection_request(
    request: Request,
    request_id: int = Form(...),
    response: str = Form(..., regex="^(accept|decline)$"),
    db: Session = Depends(get_db)
):
    """Respond to a connection request (accept/decline)"""
    try:
        user_id = get_authenticated_user_id(request, db)
        
        # Get the friend request
        friend_request = db.query(FriendRequest).filter(
            FriendRequest.id == request_id,
            FriendRequest.receiver_id == user_id,
            FriendRequest.status == 'pending'
        ).first()
        
        if not friend_request:
            raise HTTPException(status_code=404, detail="Connection request not found")
        
        if response == "accept":
            # Check if connection already exists to prevent duplicates
            existing_connection = db.query(Connection).filter(
                or_(
                    and_(Connection.user_id == friend_request.sender_id, Connection.connected_user_id == friend_request.receiver_id),
                    and_(Connection.user_id == friend_request.receiver_id, Connection.connected_user_id == friend_request.sender_id)
                ),
                Connection.status == 'accepted'
            ).first()
            
            if existing_connection:
                # Connection already exists, just update the request status
                friend_request.status = 'accepted'
                friend_request.responded_at = datetime.utcnow()
            else:
                # Accept the request
                friend_request.status = 'accepted'
                friend_request.responded_at = datetime.utcnow()
                
                # Create bidirectional connections - both users should see each other
                connection1 = Connection(
                    user_id=friend_request.sender_id,
                    connected_user_id=friend_request.receiver_id,
                    status='accepted',
                    connection_type='professional',
                    accepted_at=datetime.utcnow()
                )
                
                connection2 = Connection(
                    user_id=friend_request.receiver_id,
                    connected_user_id=friend_request.sender_id,
                    status='accepted',
                    connection_type='professional',
                    accepted_at=datetime.utcnow()
                )
                
                db.add(connection1)
                db.add(connection2)
            
            # Create notification for sender
            sender = db.query(User).get(friend_request.sender_id)
            notification = Notification(
                user_id=friend_request.sender_id,
                title="Connection Request Accepted",
                message=f"{db.query(User).get(user_id).full_name} accepted your connection request",
                notification_type="connection_accepted",
                related_id=friend_request.id,
                related_type="friend_request"
            )
            
            db.add(notification)
            
        elif response == "decline":
            # Decline the request
            friend_request.status = 'declined'
            friend_request.responded_at = datetime.utcnow()
            
            # Create notification for sender
            notification = Notification(
                user_id=friend_request.sender_id,
                title="Connection Request Declined",
                message=f"{db.query(User).get(user_id).full_name} declined your connection request",
                notification_type="connection_declined",
                related_id=friend_request.id,
                related_type="friend_request"
            )
            
            db.add(notification)
        
        db.commit()
        
        return JSONResponse(content={
            "message": f"Connection request {response}ed successfully",
            "status": "success"
        })
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error responding to connection request: {str(e)}")
        raise HTTPException(status_code=500, detail="Error responding to connection request")

@router.post("/api/withdraw-request")
async def withdraw_connection_request(
    request: Request,
    request_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Withdraw a sent connection request"""
    try:
        user_id = get_authenticated_user_id(request, db)
        
        # Get the friend request
        friend_request = db.query(FriendRequest).filter(
            FriendRequest.id == request_id,
            FriendRequest.sender_id == user_id,
            FriendRequest.status == 'pending'
        ).first()
        
        if not friend_request:
            raise HTTPException(status_code=404, detail="Connection request not found")
        
        # Delete the request
        db.delete(friend_request)
        db.commit()
        
        return JSONResponse(content={
            "message": "Connection request withdrawn successfully",
            "status": "success"
        })
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error withdrawing connection request: {str(e)}")
        raise HTTPException(status_code=500, detail="Error withdrawing connection request")

@router.post("/api/remove-connection")
async def remove_connection(
    request: Request,
    connection_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Remove a connection (either delete or mark as removed)"""
    try:
        user_id = get_authenticated_user_id(request, db)
        
        # Get the connection
        connection = db.query(Connection).filter(
            Connection.id == connection_id,
            Connection.status == 'accepted',
            or_(
                Connection.user_id == user_id,
                Connection.connected_user_id == user_id
            )
        ).first()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Mark as removed instead of deleting to maintain history
        connection.status = 'removed'
        connection.updated_at = datetime.utcnow()
        
        # Create notification for the other user
        other_user_id = connection.connected_user_id if connection.user_id == user_id else connection.user_id
        current_user = db.query(User).get(user_id)
        
        notification = Notification(
            user_id=other_user_id,
            title="Connection Removed",
            message=f"{current_user.full_name} removed you from their connections",
            notification_type="connection_removed",
            related_id=connection.id,
            related_type="connection"
        )
        
        db.add(notification)
        db.commit()
        
        return JSONResponse(content={
            "message": "Connection removed successfully",
            "status": "success"
        })
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error removing connection: {str(e)}")
        raise HTTPException(status_code=500, detail="Error removing connection")

@router.post("/api/cancel-request")
async def cancel_connection_request(
    request: Request,
    request_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Cancel a sent connection request"""
    try:
        user_id = get_authenticated_user_id(request, db)
        
        # Get the friend request
        friend_request = db.query(FriendRequest).filter(
            FriendRequest.id == request_id,
            FriendRequest.sender_id == user_id,
            FriendRequest.status == 'pending'
        ).first()
        
        if not friend_request:
            raise HTTPException(status_code=404, detail="Connection request not found")
        
        # Mark as cancelled instead of deleting
        friend_request.status = 'cancelled'
        friend_request.updated_at = datetime.utcnow()
        
        db.commit()
        
        return JSONResponse(content={
            "message": "Connection request cancelled successfully",
            "status": "success"
        })
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error cancelling connection request: {str(e)}")
        raise HTTPException(status_code=500, detail="Error cancelling connection request")

# ==================== PROFILE VIEWING ====================

@router.get("/api/profile/{user_id}")
async def get_user_profile(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get detailed user profile for connection management"""
    try:
        current_user_id = get_authenticated_user_id(request, db)
        
        # Get user profile
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check connection status
        connection_status = await get_connection_status(current_user_id, user_id, db)
        
        # Get mutual connections
        mutual_connections = await get_mutual_connections(current_user_id, user_id, db)
        
        # Get user's recent activity
        recent_posts = db.query(Post).filter(
            Post.user_id == user_id,
            Post.is_public == True
        ).order_by(Post.created_at.desc()).limit(5).all()
        
        profile_data = {
            "id": user.id,
            "full_name": user.full_name,
            "title": user.title,
            "company": user.company,
            "location": user.location,
            "bio": user.bio,
            "profile_image": user.profile_image,
            "user_type": user.user_type,
            "is_verified": user.is_verified,
            "industry": user.industry,
            "skills": user.skills,
            "experience_years": user.experience_years,
            "education": user.education,
            "certifications": user.certifications,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "connection_status": connection_status,
            "mutual_connections": mutual_connections,
            "recent_posts": [
                {
                    "id": post.id,
                    "content": post.content,
                    "post_type": post.post_type,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "likes_count": post.likes_count
                } for post in recent_posts
            ]
        }
        
        return JSONResponse(content=profile_data)
        
    except Exception as e:
        logging.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting user profile")

# ==================== ENHANCED SEARCH & DISCOVERY ====================

@router.get("/api/search")
async def search_connections(
    request: Request,
    db: Session = Depends(get_db),
    query: Optional[str] = Query(None, description="Search query for name, company, title, skills, etc."),
    search_type: str = Query("all", regex="^(all|name|company|title|skills|location|industry|education)$"),
    location: Optional[str] = Query(None, description="Filter by location"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    company: Optional[str] = Query(None, description="Filter by company"),
    title: Optional[str] = Query(None, description="Filter by job title"),
    experience_min: Optional[int] = Query(None, description="Minimum years of experience"),
    experience_max: Optional[int] = Query(None, description="Maximum years of experience"),
    user_type: Optional[str] = Query(None, regex="^(normal|domain|premium)$"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    sort_by: str = Query("relevance", regex="^(relevance|name|company|location|experience|mutual_connections)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    """Enhanced search through users and connections with multiple filters"""
    try:
        user_id = get_authenticated_user_id(request, db)
        
        if not query and not any([location, industry, company, title, experience_min, experience_max, user_type]):
            # If no search criteria, return suggestions
            search_results = await get_connection_suggestions(user_id, db, page, limit)
        else:
            search_results = await enhanced_search_users_and_connections(
                user_id, db, query, search_type, location, industry, company, 
                title, experience_min, experience_max, user_type, page, limit, sort_by, sort_order
            )
        
        return JSONResponse(content=search_results)
        
    except Exception as e:
        logging.error(f"Error searching connections: {str(e)}")
        raise HTTPException(status_code=500, detail="Error searching connections")

async def enhanced_search_users_and_connections(
    user_id: int,
    db: Session,
    query: Optional[str],
    search_type: str,
    location: Optional[str],
    industry: Optional[str],
    company: Optional[str],
    title: Optional[str],
    experience_min: Optional[int],
    experience_max: Optional[int],
    user_type: Optional[str],
    page: int,
    limit: int,
    sort_by: str,
    sort_order: str
) -> Dict[str, Any]:
    """Enhanced search through users and connections with advanced filtering"""
    try:
        search_query = db.query(User).filter(User.id != user_id, User.is_active == True)
        
        # Apply search query based on type
        if query:
            if search_type == "name":
                search_terms = query.split()
                for term in search_terms:
                    search_query = search_query.filter(
                        or_(
                            User.full_name.ilike(f'%{term}%'),
                            User.username.ilike(f'%{term}%')
                        )
                    )
            elif search_type == "company":
                search_query = search_query.filter(User.company.ilike(f'%{query}%'))
            elif search_type == "title":
                search_query = search_query.filter(User.title.ilike(f'%{query}%'))
            elif search_type == "skills":
                search_query = search_query.filter(User.skills.ilike(f'%{query}%'))
            elif search_type == "location":
                search_query = search_query.filter(User.location.ilike(f'%{query}%'))
            elif search_type == "industry":
                search_query = search_query.filter(User.industry.ilike(f'%{query}%'))
            elif search_type == "education":
                search_query = search_query.filter(User.education.ilike(f'%{query}%'))
            else:  # all - comprehensive search
                search_terms = query.split()
                for term in search_terms:
                    search_query = search_query.filter(
                        or_(
                            User.full_name.ilike(f'%{term}%'),
                            User.username.ilike(f'%{term}%'),
                            User.title.ilike(f'%{term}%'),
                            User.company.ilike(f'%{term}%'),
                            User.bio.ilike(f'%{term}%'),
                            User.skills.ilike(f'%{term}%'),
                            User.industry.ilike(f'%{term}%'),
                            User.location.ilike(f'%{term}%'),
                            User.education.ilike(f'%{term}%')
                        )
                    )
        
        # Apply additional filters
        if location:
            search_query = search_query.filter(User.location.ilike(f'%{location}%'))
        
        if industry:
            search_query = search_query.filter(User.industry.ilike(f'%{industry}%'))
        
        if company:
            search_query = search_query.filter(User.company.ilike(f'%{company}%'))
        
        if title:
            search_query = search_query.filter(User.title.ilike(f'%{title}%'))
        
        if experience_min is not None:
            search_query = search_query.filter(User.experience_years >= experience_min)
        
        if experience_max is not None:
            search_query = search_query.filter(User.experience_years <= experience_max)
        
        if user_type:
            search_query = search_query.filter(User.user_type == user_type)
        
        # Apply sorting
        if sort_by == "name":
            search_query = search_query.order_by(User.full_name.asc() if sort_order == "asc" else User.full_name.desc())
        elif sort_by == "company":
            search_query = search_query.order_by(User.company.asc() if sort_order == "asc" else User.company.desc())
        elif sort_by == "location":
            search_query = search_query.order_by(User.location.asc() if sort_order == "asc" else User.location.desc())
        elif sort_by == "experience":
            search_query = search_query.order_by(User.experience_years.asc() if sort_order == "asc" else User.experience_years.desc())
        elif sort_by == "mutual_connections":
            # For mutual connections sorting, we'll need to calculate this
            search_query = search_query.order_by(User.full_name.asc())
        else:  # relevance - default sorting
            search_query = search_query.order_by(User.full_name.asc())
        
        # Get total count
        total = search_query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        users = search_query.offset(offset).limit(limit).all()
        
        # Get enhanced results with connection status and mutual connections
        results = []
        for user in users:
            connection_status = await get_connection_status(user_id, user.id, db)
            mutual_connections = await get_mutual_connections_count(user_id, user.id, db)
            profile_completeness = calculate_profile_completeness(user)
            
            results.append({
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "title": user.title,
                "company": user.company,
                "location": user.location,
                "profile_image": user.profile_image,
                "industry": user.industry,
                "bio": user.bio,
                "skills": user.skills,
                "experience_years": user.experience_years,
                "education": user.education,
                "linkedin_url": user.linkedin_url,
                "github_url": user.github_url,
                "twitter_url": user.twitter_url,
                "website": user.website,
                "user_type": user.user_type,
                "is_verified": user.is_verified,
                "connection_status": connection_status,
                "mutual_connections": mutual_connections,
                "profile_completeness": profile_completeness,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })
        
        return {
            "results": results,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            },
            "filters_applied": {
                "query": query,
                "search_type": search_type,
                "location": location,
                "industry": industry,
                "company": company,
                "title": title,
                "experience_min": experience_min,
                "experience_max": experience_max,
                "user_type": user_type
            }
        }
        
    except Exception as e:
        logging.error(f"Error in enhanced search: {str(e)}")
        raise e

async def get_mutual_connections_count(user1_id: int, user2_id: int, db: Session) -> int:
    """Get count of mutual connections between two users"""
    try:
        # Get connections of user1
        user1_connections = db.query(Connection).filter(
            Connection.user_id == user1_id,
            Connection.status == 'accepted'
        ).all()
        user1_connection_ids = [conn.connected_user_id for conn in user1_connections]
        
        # Get connections of user2
        user2_connections = db.query(Connection).filter(
            Connection.user_id == user2_id,
            Connection.status == 'accepted'
        ).all()
        user2_connection_ids = [conn.connected_user_id for conn in user2_connections]
        
        # Find mutual connections
        mutual_ids = set(user1_connection_ids) & set(user2_connection_ids)
        return len(mutual_ids)
        
    except Exception as e:
        logging.error(f"Error getting mutual connections: {str(e)}")
        return 0

def calculate_profile_completeness(user: User) -> int:
    """Calculate profile completeness percentage"""
    try:
        fields = [
            user.full_name, user.title, user.company, user.location, 
            user.bio, user.skills, user.industry, user.experience_years,
            user.education, user.profile_image
        ]
        
        filled_fields = sum(1 for field in fields if field and str(field).strip())
        total_fields = len(fields)
        
        return int((filled_fields / total_fields) * 100)
        
    except Exception as e:
        logging.error(f"Error calculating profile completeness: {str(e)}")
        return 0

@router.get("/api/search/suggestions")
async def get_search_suggestions(
    request: Request,
    db: Session = Depends(get_db),
    query: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """Get search suggestions as user types"""
    try:
        if not query or len(query.strip()) < 2:
            return JSONResponse(content={"suggestions": []})
        
        user_id = get_authenticated_user_id(request, db)
        search_query = query.strip().lower()
        
        # Search for users with names, titles, or companies that start with the query
        suggestions = db.query(User).filter(
            and_(
                User.id != user_id,
                User.is_active == True,
                or_(
                    User.full_name.ilike(f'{search_query}%'),
                    User.title.ilike(f'{search_query}%'),
                    User.company.ilike(f'{search_query}%'),
                    User.username.ilike(f'{search_query}%')
                )
            )
        ).limit(limit).all()
        
        results = []
        for user in suggestions:
            connection_status = await get_connection_status(user_id, user.id, db)
            results.append({
                "id": user.id,
                "full_name": user.full_name,
                "title": user.title,
                "company": user.company,
                "username": user.username,
                "connection_status": connection_status
            })
        
        return JSONResponse(content={"suggestions": results})
        
    except Exception as e:
        logging.error(f"Error getting search suggestions: {str(e)}")
        return JSONResponse(content={"suggestions": []})

@router.get("/api/search/recent")
async def get_recent_searches(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """Get recent search queries (placeholder for future implementation)"""
    try:
        # This would typically store search history in a separate table
        # For now, return empty array
        return JSONResponse(content={"recent_searches": []})
        
    except Exception as e:
        logging.error(f"Error getting recent searches: {str(e)}")
        return JSONResponse(content={"recent_searches": []})

@router.get("/api/search/popular")
async def get_popular_searches(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """Get popular search terms (placeholder for future implementation)"""
    try:
        # This would typically track search frequency
        # For now, return some common search terms
        popular_searches = [
            "software engineer", "data scientist", "product manager",
            "marketing", "sales", "design", "finance", "healthcare"
        ]
        
        return JSONResponse(content={"popular_searches": popular_searches[:limit]})
        
    except Exception as e:
        logging.error(f"Error getting popular searches: {str(e)}")
        return JSONResponse(content={"popular_searches": []})

# ==================== HELPER FUNCTIONS ====================

async def get_user_connections_data(user_id: int, db: Session) -> Dict[str, Any]:
    """Get comprehensive connection data for a user"""
    try:
        # Get accepted connections
        connections = db.query(Connection, User).join(
            User, Connection.connected_user_id == User.id
        ).filter(
            Connection.user_id == user_id,
            Connection.status == 'accepted'
        ).all()
        
        # Get pending requests
        pending_requests = db.query(FriendRequest, User).join(
            User, FriendRequest.sender_id == User.id
        ).filter(
            FriendRequest.receiver_id == user_id,
            FriendRequest.status == 'pending'
        ).all()
        
        # Get sent requests
        sent_requests = db.query(FriendRequest, User).join(
            User, FriendRequest.receiver_id == User.id
        ).filter(
            FriendRequest.sender_id == user_id,
            FriendRequest.status == 'pending'
        ).all()
        
        # Get connection suggestions
        suggestions = await get_connection_suggestions_for_user(user_id, db, 1, 10)
        
        # Calculate stats
        stats = await calculate_connection_stats(user_id, db)
        
        return {
            "connections": connections,
            "pending_requests": pending_requests,
            "sent_requests": sent_requests,
            "suggestions": suggestions["suggestions"],
            "stats": stats
        }
        
    except Exception as e:
        logging.error(f"Error getting user connections data: {str(e)}")
        raise e

async def calculate_connection_stats(user_id: int, db: Session) -> Dict[str, Any]:
    """Calculate comprehensive connection statistics for a user"""
    try:
        # Total connections
        total_connections = db.query(Connection).filter(
            Connection.user_id == user_id,
            Connection.status == 'accepted'
        ).count()
        
        # Pending requests
        pending_requests = db.query(FriendRequest).filter(
            FriendRequest.receiver_id == user_id,
            FriendRequest.status == 'pending'
        ).count()
        
        # Sent requests
        sent_requests = db.query(FriendRequest).filter(
            FriendRequest.sender_id == user_id,
            FriendRequest.status == 'pending'
        ).count()
        
        # Mutual connections (simplified calculation)
        mutual_connections = 0  # This would require more complex logic
        
        # Network growth (connections in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_connections = db.query(Connection).filter(
            Connection.user_id == user_id,
            Connection.status == 'accepted',
            Connection.accepted_at >= thirty_days_ago
        ).count()
        
        # Industry distribution
        industry_distribution = db.query(
            User.industry,
            func.count(User.id)
        ).join(
            Connection, User.id == Connection.connected_user_id
        ).filter(
            Connection.user_id == user_id,
            Connection.status == 'accepted',
            User.industry.isnot(None)
        ).group_by(User.industry).all()
        
        return {
            "total_connections": total_connections,
            "pending_requests": pending_requests,
            "sent_requests": sent_requests,
            "mutual_connections": mutual_connections,
            "recent_connections": recent_connections,
            "industry_distribution": dict(industry_distribution)
        }
        
    except Exception as e:
        logging.error(f"Error calculating connection stats: {str(e)}")
        raise e

async def get_filtered_connections(
    user_id: int,
    db: Session,
    page: int,
    limit: int,
    sort_by: str,
    search: Optional[str],
    company_filter: Optional[str],
    location_filter: Optional[str]
) -> Dict[str, Any]:
    """Get filtered and sorted connections for a user"""
    try:
        query = db.query(Connection, User).join(
            User, Connection.connected_user_id == User.id
        ).filter(
            Connection.user_id == user_id,
            Connection.status == 'accepted'
        )
        
        # Apply filters
        if search:
            search_terms = search.split()
            for term in search_terms:
                query = query.filter(
                    or_(
                        User.full_name.ilike(f'%{term}%'),
                        User.title.ilike(f'%{term}%'),
                        User.company.ilike(f'%{term}%'),
                        User.bio.ilike(f'%{term}%')
                    )
                )
        
        if company_filter:
            query = query.filter(User.company.ilike(f'%{company_filter}%'))
        
        if location_filter:
            query = query.filter(User.location.ilike(f'%{location_filter}%'))
        
        # Apply sorting
        if sort_by == "name":
            query = query.order_by(User.full_name.asc())
        elif sort_by == "company":
            query = query.order_by(User.company.asc())
        elif sort_by == "recent":
            query = query.order_by(Connection.accepted_at.desc())
        elif sort_by == "mutual":
            # This would require more complex logic for mutual connections
            query = query.order_by(User.full_name.asc())
        
        # Apply pagination
        total = query.count()
        offset = (page - 1) * limit
        connections = query.offset(offset).limit(limit).all()
        
        return {
            "connections": [
                {
                    "id": conn.id,
                    "user": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "title": user.title,
                        "company": user.company,
                        "location": user.location,
                        "profile_image": user.profile_image,
                        "industry": user.industry
                    },
                    "connected_since": conn.accepted_at.isoformat() if conn.accepted_at else None,
                    "connection_type": conn.connection_type
                } for conn, user in connections
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logging.error(f"Error getting filtered connections: {str(e)}")
        raise e

async def get_user_pending_requests(
    user_id: int,
    db: Session,
    page: int,
    limit: int
) -> Dict[str, Any]:
    """Get pending connection requests for a user"""
    try:
        query = db.query(FriendRequest, User).join(
            User, FriendRequest.sender_id == User.id
        ).filter(
            FriendRequest.receiver_id == user_id,
            FriendRequest.status == 'pending'
        ).order_by(FriendRequest.created_at.desc())
        
        total = query.count()
        offset = (page - 1) * limit
        requests = query.offset(offset).limit(limit).all()
        
        return {
            "requests": [
                {
                    "id": req.id,
                    "sender": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "title": user.title,
                        "company": user.company,
                        "profile_image": user.profile_image,
                        "location": user.location
                    },
                    "message": req.message,
                    "created_at": req.created_at.isoformat() if req.created_at else None
                } for req, user in requests
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logging.error(f"Error getting pending requests: {str(e)}")
        raise e

async def get_user_sent_requests(
    user_id: int,
    db: Session,
    page: int,
    limit: int
) -> Dict[str, Any]:
    """Get sent connection requests by a user"""
    try:
        query = db.query(FriendRequest, User).join(
            User, FriendRequest.receiver_id == User.id
        ).filter(
            FriendRequest.sender_id == user_id,
            FriendRequest.status == 'pending'
        ).order_by(FriendRequest.created_at.desc())
        
        total = query.count()
        offset = (page - 1) * limit
        requests = query.offset(offset).limit(limit).all()
        
        return {
            "requests": [
                {
                    "id": req.id,
                    "receiver": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "title": user.title,
                        "company": user.company,
                        "profile_image": user.profile_image,
                        "location": user.location
                    },
                    "message": req.message,
                    "created_at": req.created_at.isoformat() if req.created_at else None
                } for req, user in requests
            ],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logging.error(f"Error getting sent requests: {str(e)}")
        raise e

def get_connection_suggestions_for_user(
    user_id: int,
    db: Session,
    page: int,
    limit: int
) -> Dict[str, Any]:
    """Get connection suggestions for a user based on various factors"""
    try:
        # Get current user info
        current_user = db.query(User).get(user_id)
        if not current_user:
            return {
                "suggestions": [],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": 0,
                    "pages": 0
                }
            }
        
        # Get user's current connections to exclude them
        user_connections = db.query(Connection.connected_user_id).filter(
            Connection.user_id == user_id,
            Connection.status == 'accepted'
        ).subquery()
        
        # Get user's sent and received requests to exclude them
        user_requests = db.query(FriendRequest.sender_id).filter(
            FriendRequest.receiver_id == user_id
        ).union(
            db.query(FriendRequest.receiver_id).filter(
                FriendRequest.sender_id == user_id
            )
        ).subquery()
        
        # Find users who are not connected and not in requests
        # Prioritize users with complete profiles
        suggestions_query = db.query(User).filter(
            User.id != user_id,
            ~User.id.in_(user_connections),
            ~User.id.in_(user_requests),
            User.is_active == True
        )
        
        # Apply intelligent filtering - prioritize users with complete profiles
        suggestions_query = suggestions_query.order_by(
            # Priority 1: Users with complete company info (not generic)
            User.company.notlike('%Company%').desc(),
            User.company.notlike('%Test%').desc(),
            # Priority 2: Users with complete title info (not generic)
            User.title.notlike('%Professional%').desc(),
            # Priority 3: Users with complete location info (not generic)
            User.location.notlike('%Location%').desc(),
            # Priority 4: Users with complete industry info (not generic)
            User.industry.notlike('%Industry%').desc(),
            # Priority 5: Recent activity
            User.created_at.desc()
        )
        
        total = suggestions_query.count()
        offset = (page - 1) * limit
        suggestions = suggestions_query.offset(offset).limit(limit).all()
        
        # Create intelligent suggestions with better data quality
        suggestions_with_reasons = []
        for user in suggestions:
            reason = "New to platform"
            mutual_count = 0
            
            # Determine connection reason based on profile completeness
            if current_user.company and user.company and user.company != "Company" and user.company != "Test Company":
                if user.company == current_user.company:
                    reason = f"Same company: {user.company}"
                elif any(word in user.company.lower() for word in current_user.company.lower().split()):
                    reason = f"Similar company: {user.company}"
                else:
                    reason = f"Company: {user.company}"
            elif current_user.location and user.location and user.location != "Location":
                if user.location == current_user.location:
                    reason = f"Same location: {user.location}"
                else:
                    reason = f"Location: {user.location}"
            elif current_user.industry and user.industry and user.industry != "Industry":
                if user.industry == current_user.industry:
                    reason = f"Same industry: {user.industry}"
                else:
                    reason = f"Industry: {user.industry}"
            elif user.title and user.title != "Professional":
                reason = f"Title: {user.title}"
            elif user.company and user.company != "Company" and user.company != "Test Company":
                reason = f"Company: {user.company}"
            else:
                reason = "New to platform"
            
            # Calculate mutual connections
            mutual_count = calculate_mutual_connections_count(user_id, user.id, db)
            
            # Only include users with meaningful profile information
            if (user.title and user.title != "Professional" and 
                user.company and user.company not in ["Company", "Test Company"] and
                user.full_name and len(user.full_name.strip()) > 0):
                
                suggestions_with_reasons.append({
                    "id": user.id,
                    "full_name": user.full_name,
                    "title": user.title or "Professional",
                    "company": user.company or "Company",
                    "profile_image": user.profile_image or "default-avatar.svg",
                    "location": user.location or "Location not specified",
                    "industry": user.industry or "Industry not specified",
                    "reason": reason,
                    "mutual_count": mutual_count,
                    "profile_completeness": calculate_profile_completeness(user)
                })
        
        return {
            "suggestions": suggestions_with_reasons,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logging.error(f"Error in get_connection_suggestions_for_user: {str(e)}")
        # Return empty result instead of raising exception
        return {
            "suggestions": [],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": 0,
                "pages": 0
            }
        }

def calculate_mutual_connections_count(
    user1_id: int,
    user2_id: int,
    db: Session
) -> int:
    """Calculate the number of mutual connections between two users"""
    try:
        # Get user1's connections
        user1_connections = db.query(Connection.connected_user_id).filter(
            Connection.user_id == user1_id,
            Connection.status == 'accepted'
        ).subquery()
        
        # Count user2's connections that are also user1's connections
        mutual_count = db.query(Connection).filter(
            Connection.user_id == user2_id,
            Connection.status == 'accepted',
            Connection.connected_user_id.in_(user1_connections)
        ).count()
        
        return mutual_count
        
    except Exception as e:
        logging.error(f"Error calculating mutual connections count: {str(e)}")
        return 0

async def get_connection_status(
    current_user_id: int,
    target_user_id: int,
    db: Session
) -> str:
    """Get the connection status between two users"""
    try:
        # Check if already connected
        connection = db.query(Connection).filter(
            or_(
                and_(Connection.user_id == current_user_id, Connection.connected_user_id == target_user_id),
                and_(Connection.user_id == target_user_id, Connection.connected_user_id == current_user_id)
            ),
            Connection.status == 'accepted'
        ).first()
        
        if connection:
            return "connected"
        
        # Check if request sent
        sent_request = db.query(FriendRequest).filter(
            FriendRequest.sender_id == current_user_id,
            FriendRequest.receiver_id == target_user_id,
            FriendRequest.status == 'pending'
        ).first()
        
        if sent_request:
            return "request_sent"
        
        # Check if request received
        received_request = db.query(FriendRequest).filter(
            FriendRequest.sender_id == target_user_id,
            FriendRequest.receiver_id == current_user_id,
            FriendRequest.status == 'pending'
        ).first()
        
        if received_request:
            return "request_received"
        
        return "not_connected"
        
    except Exception as e:
        logging.error(f"Error getting connection status: {str(e)}")
        return "unknown"

async def get_mutual_connections(
    user1_id: int,
    user2_id: int,
    db: Session
) -> List[Dict[str, Any]]:
    """Get mutual connections between two users"""
    try:
        # Get user1's connections
        user1_connections = db.query(Connection.connected_user_id).filter(
            Connection.user_id == user1_id,
            Connection.status == 'accepted'
        ).subquery()
        
        # Get user2's connections that are also user1's connections
        mutual_connections = db.query(User).join(
            Connection, User.id == Connection.connected_user_id
        ).filter(
            Connection.user_id == user2_id,
            Connection.status == 'accepted',
            User.id.in_(user1_connections)
        ).limit(10).all()
        
        return [
            {
                "id": user.id,
                "full_name": user.full_name,
                "title": user.title,
                "company": user.company,
                "profile_image": user.profile_image
            } for user in mutual_connections
        ]
        
    except Exception as e:
        logging.error(f"Error getting mutual connections: {str(e)}")
        return []

def get_default_user_id(db: Session) -> int:
    """Get default user ID (first user in database)"""
    user = db.query(User).first()
    if not user:
        # Create a default user if none exists
        default_user = User(
            username="admin",
            email="admin@careerconnect.com",
            full_name="Administrator",
            is_active=True
        )
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
        return default_user.id
    return user.id

@router.get("/search", response_class=HTMLResponse)
def enhanced_search_page(request: Request, db: Session = Depends(get_db)):
    """Enhanced search page with LinkedIn-like interface"""
    try:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Find People - Qrow IQ</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background-color: #f3f2ef; color: #191919; line-height: 1.6; }
                    .header { background: linear-gradient(135deg, #0077b5 0%, #005885 100%); color: white; padding: 2rem 0; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .header h1 { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; }
                    .header p { font-size: 1.1rem; opacity: 0.9; }
                    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
                    .search-section { background: white; border-radius: 12px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 2px 20px rgba(0,0,0,0.08); }
                    .search-header { margin-bottom: 1.5rem; }
                    .search-header h2 { font-size: 1.5rem; color: #191919; margin-bottom: 0.5rem; }
                    .search-input-group { position: relative; margin-bottom: 1.5rem; }
                    .search-input { width: 100%; padding: 1rem 1rem 1rem 3rem; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 1rem; transition: all 0.3s ease; background: #fafafa; }
                    .search-input:focus { outline: none; border-color: #0077b5; background: white; box-shadow: 0 0 0 3px rgba(0,119,181,0.1); }
                    .search-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: #666; font-size: 1.2rem; }
                    .filters-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
                    .filter-group { display: flex; flex-direction: column; }
                    .filter-group label { font-weight: 600; margin-bottom: 0.5rem; color: #191919; font-size: 0.9rem; }
                    .filter-group input, .filter-group select { padding: 0.75rem; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 0.9rem; transition: border-color 0.3s ease; }
                    .filter-group input:focus, .filter-group select:focus { outline: none; border-color: #0077b5; }
                    .search-actions { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
                    .search-btn { background: #0077b5; color: white; border: none; padding: 1rem 2rem; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; gap: 0.5rem; }
                    .search-btn:hover { background: #005885; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,119,181,0.3); }
                    .clear-btn { background: #f0f0f0; color: #666; border: none; padding: 1rem 2rem; border-radius: 8px; font-size: 1rem; cursor: pointer; transition: all 0.3s ease; }
                    .clear-btn:hover { background: #e0e0e0; color: #333; }
                    .results-section { background: white; border-radius: 12px; padding: 2rem; box-shadow: 0 2px 20px rgba(0,0,0,0.08); }
                    .results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0; }
                    .results-count { color: #666; font-size: 0.9rem; }
                    .sort-controls { display: flex; gap: 1rem; align-items: center; }
                    .sort-controls select { padding: 0.5rem; border: 1px solid #e0e0e0; border-radius: 4px; font-size: 0.9rem; }
                    .user-card { border: 1px solid #e0e0e0; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; transition: all 0.3s ease; background: #fafafa; }
                    .user-card:hover { border-color: #0077b5; box-shadow: 0 4px 12px rgba(0,0,0,0.1); transform: translateY(-2px); }
                    .user-header { display: flex; align-items: center; margin-bottom: 1rem; }
                    .user-avatar { width: 60px; height: 60px; border-radius: 50%; object-fit: cover; margin-right: 1rem; border: 3px solid #0077b5; }
                    .user-info h3 { font-size: 1.2rem; color: #191919; margin-bottom: 0.25rem; }
                    .user-title { color: #666; font-weight: 500; margin-bottom: 0.25rem; }
                    .user-company { color: #0077b5; font-weight: 600; }
                    .user-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1rem; }
                    .detail-item { display: flex; align-items: center; gap: 0.5rem; color: #666; font-size: 0.9rem; }
                    .detail-item i { color: #0077b5; width: 16px; }
                    .profile-completeness { margin-bottom: 1rem; }
                    .completeness-bar { width: 100%; height: 8px; background: #e0e0e0; border-radius: 4px; overflow: hidden; margin-bottom: 0.5rem; }
                    .completeness-fill { height: 100%; background: linear-gradient(90deg, #0077b5, #00a0dc); transition: width 0.3s ease; }
                    .completeness-text { font-size: 0.8rem; color: #666; }
                    .action-buttons { display: flex; gap: 1rem; flex-wrap: wrap; }
                    .btn { padding: 0.75rem 1.5rem; border: none; border-radius: 6px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; gap: 0.5rem; }
                    .btn-primary { background: #0077b5; color: white; }
                    .btn-primary:hover { background: #005885; transform: translateY(-1px); }
                    .btn-secondary { background: transparent; color: #0077b5; border: 1px solid #0077b5; }
                    .btn-secondary:hover { background: #0077b5; color: white; }
                    .btn-success { background: #28a745; color: white; }
                    .btn-success:hover { background: #218838; }
                    .btn-warning { background: #ffc107; color: #212529; }
                    .btn-warning:hover { background: #e0a800; }
                    .loading { text-align: center; padding: 3rem; color: #666; }
                    .loading i { font-size: 2rem; color: #0077b5; margin-bottom: 1rem; }
                    .no-results { text-align: center; padding: 3rem; color: #666; }
                    .no-results i { font-size: 3rem; color: #ccc; margin-bottom: 1rem; }
                    .pagination { display: flex; justify-content: center; gap: 0.5rem; margin-top: 2rem; }
                    .page-btn { padding: 0.5rem 1rem; border: 1px solid #e0e0e0; background: white; color: #666; border-radius: 4px; cursor: pointer; transition: all 0.3s ease; }
                    .page-btn:hover { background: #f0f0f0; border-color: #0077b5; color: #0077b5; }
                    .page-btn.active { background: #0077b5; color: white; border-color: #0077b5; }
                    .page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
                    .suggestions { background: #f8f9fa; border-radius: 8px; padding: 1rem; margin-top: 1rem; }
                    .suggestions h4 { color: #191919; margin-bottom: 0.5rem; font-size: 0.9rem; }
                    .suggestion-tags { display: flex; flex-wrap: wrap; gap: 0.5rem; }
                    .suggestion-tag { background: white; border: 1px solid #e0e0e0; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; color: #666; cursor: pointer; transition: all 0.3s ease; }
                    .suggestion-tag:hover { background: #0077b5; color: white; border-color: #0077b5; }
                    @media (max-width: 768px) { .container { padding: 1rem; } .filters-row { grid-template-columns: 1fr; } .search-actions { flex-direction: column; } .search-btn, .clear-btn { width: 100%; } .results-header { flex-direction: column; gap: 1rem; align-items: flex-start; } .action-buttons { flex-direction: column; } .btn { width: 100%; justify-content: center; } }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1><i class="fas fa-search"></i> Find People</h1>
                    <p>Discover and connect with professionals in your network</p>
                </div>
                
                <div class="container">
                    <div class="search-section">
                        <div class="search-header">
                            <h2><i class="fas fa-filter"></i> Search & Filters</h2>
                            <p>Find people by name, company, skills, location, and more</p>
                        </div>
                        
                        <div class="search-input-group">
                            <i class="fas fa-search search-icon"></i>
                            <input type="text" id="searchQuery" class="search-input" placeholder="Search for people, companies, skills, titles...">
                        </div>
                        
                        <div class="filters-row">
                            <div class="filter-group">
                                <label for="searchType">Search Type</label>
                                <select id="searchType">
                                    <option value="all">All Fields</option>
                                    <option value="name">Name</option>
                                    <option value="company">Company</option>
                                    <option value="title">Job Title</option>
                                    <option value="skills">Skills</option>
                                    <option value="location">Location</option>
                                    <option value="industry">Industry</option>
                                    <option value="education">Education</option>
                                </select>
                            </div>
                            
                            <div class="filter-group">
                                <label for="location">Location</label>
                                <input type="text" id="location" placeholder="e.g., San Francisco, CA">
                            </div>
                            
                            <div class="filter-group">
                                <label for="industry">Industry</label>
                                <input type="text" id="industry" placeholder="e.g., Technology, Healthcare">
                            </div>
                            
                            <div class="filter-group">
                                <label for="company">Company</label>
                                <input type="text" id="company" placeholder="e.g., Google, Microsoft">
                            </div>
                            
                            <div class="filter-group">
                                <label for="title">Job Title</label>
                                <input type="text" id="title" placeholder="e.g., Software Engineer, Manager">
                            </div>
                            
                            <div class="filter-group">
                                <label for="experienceMin">Min Experience (years)</label>
                                <input type="number" id="experienceMin" min="0" max="50" placeholder="0">
                            </div>
                            
                            <div class="filter-group">
                                <label for="experienceMax">Max Experience (years)</label>
                                <input type="number" id="experienceMax" min="0" max="50" placeholder="20">
                            </div>
                            
                            <div class="filter-group">
                                <label for="userType">User Type</label>
                                <select id="userType">
                                    <option value="">All Types</option>
                                    <option value="normal">Normal</option>
                                    <option value="domain">Domain</option>
                                    <option value="premium">Premium</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="search-actions">
                            <button class="search-btn" onclick="performSearch()">
                                <i class="fas fa-search"></i> Search
                            </button>
                            <button class="clear-btn" onclick="clearFilters()">
                                <i class="fas fa-times"></i> Clear Filters
                            </button>
                        </div>
                        
                        <div class="suggestions">
                            <h4><i class="fas fa-lightbulb"></i> Popular Searches</h4>
                            <div class="suggestion-tags" id="popularSearches">
                                <!-- Popular searches will be loaded here -->
                            </div>
                        </div>
                    </div>
                    
                    <div class="results-section">
                        <div class="results-header">
                            <div>
                                <h2><i class="fas fa-users"></i> Search Results</h2>
                                <div class="results-count" id="resultsCount">Start your search to find people</div>
                            </div>
                            
                            <div class="sort-controls">
                                <label for="sortBy">Sort by:</label>
                                <select id="sortBy">
                                    <option value="relevance">Relevance</option>
                                    <option value="name">Name</option>
                                    <option value="company">Company</option>
                                    <option value="location">Location</option>
                                    <option value="experience">Experience</option>
                                    <option value="mutual_connections">Mutual Connections</option>
                                </select>
                                
                                <label for="sortOrder">Order:</label>
                                <select id="sortOrder">
                                    <option value="asc">A-Z</option>
                                    <option value="desc">Z-A</option>
                                </select>
                            </div>
                        </div>
                        
                        <div id="searchResults">
                            <div class="no-results">
                                <i class="fas fa-search"></i>
                                <p>Enter your search criteria above to find people</p>
                            </div>
                        </div>
                        
                        <div class="pagination" id="pagination" style="display: none;">
                            <!-- Pagination will be generated here -->
                        </div>
                    </div>
                </div>
                
                <script>
                    let currentPage = 1;
                    let currentResults = [];
                    let totalPages = 0;
                    
                    // Load popular searches on page load
                    document.addEventListener('DOMContentLoaded', function() {
                        loadPopularSearches();
                        
                        // Add enter key support for search
                        document.getElementById('searchQuery').addEventListener('keypress', function(e) {
                            if (e.key === 'Enter') {
                                performSearch();
                            }
                        });
                        
                        // Add real-time search suggestions
                        document.getElementById('searchQuery').addEventListener('input', function(e) {
                            if (e.target.value.length >= 2) {
                                getSearchSuggestions(e.target.value);
                            }
                        });
                    });
                    
                    async function loadPopularSearches() {
                        try {
                            const response = await fetch('/connections/api/search/popular');
                            const data = await response.json();
                            
                            const container = document.getElementById('popularSearches');
                            container.innerHTML = data.popular_searches.map(term => 
                                `<span class="suggestion-tag" onclick="useSearchTerm('${term}')">${term}</span>`
                            ).join('');
                        } catch (error) {
                            console.error('Error loading popular searches:', error);
                        }
                    }
                    
                    function useSearchTerm(term) {
                        document.getElementById('searchQuery').value = term;
                        performSearch();
                    }
                    
                    async function getSearchSuggestions(query) {
                        try {
                            const response = await fetch(`/connections/api/search/suggestions?query=${encodeURIComponent(query)}`);
                            const data = await response.json();
                            
                            if (data.suggestions.length > 0) {
                                // You could show these suggestions in a dropdown
                                console.log('Search suggestions:', data.suggestions);
                            }
                        } catch (error) {
                            console.error('Error getting suggestions:', error);
                        }
                    }
                    
                    async function performSearch() {
                        const query = document.getElementById('searchQuery').value;
                        const searchType = document.getElementById('searchType').value;
                        const location = document.getElementById('location').value;
                        const industry = document.getElementById('industry').value;
                        const company = document.getElementById('company').value;
                        const title = document.getElementById('title').value;
                        const experienceMin = document.getElementById('experienceMin').value;
                        const experienceMax = document.getElementById('experienceMax').value;
                        const userType = document.getElementById('userType').value;
                        const sortBy = document.getElementById('sortBy').value;
                        const sortOrder = document.getElementById('sortOrder').value;
                        
                        // Build query parameters
                        const params = new URLSearchParams();
                        if (query) params.append('query', query);
                        if (searchType) params.append('search_type', searchType);
                        if (location) params.append('location', location);
                        if (experienceMin) params.append('experience_min', experienceMin);
                        if (experienceMax) params.append('experience_max', experienceMax);
                        if (userType) params.append('user_type', userType);
                        if (sortBy) params.append('sort_by', sortBy);
                        if (sortOrder) params.append('sort_order', sortOrder);
                        params.append('page', currentPage);
                        params.append('limit', 20);
                        
                        // Show loading
                        showLoading();
                        
                        try {
                            const response = await fetch(`/connections/api/search?${params.toString()}`);
                            const data = await response.json();
                            
                            if (data.results) {
                                currentResults = data.results;
                                totalPages = data.pagination.pages;
                                displayResults(data.results, data.pagination);
                            } else {
                                showNoResults();
                            }
                        } catch (error) {
                            console.error('Search error:', error);
                            showError('An error occurred while searching. Please try again.');
                        }
                    }
                    
                    function showLoading() {
                        const container = document.getElementById('searchResults');
                        container.innerHTML = `
                            <div class="loading">
                                <i class="fas fa-spinner fa-spin"></i>
                                <p>Searching...</p>
                            </div>
                        `;
                    }
                    
                    function displayResults(results, pagination) {
                        const container = document.getElementById('searchResults');
                        const countContainer = document.getElementById('resultsCount');
                        
                        if (!results || results.length === 0) {
                            showNoResults();
                            return;
                        }
                        
                        countContainer.textContent = `${pagination.total} results found`;
                        
                        const resultsHTML = results.map(user => `
                            <div class="user-card">
                                <div class="user-header">
                                    <img src="${user.profile_image || '/static/uploads/default-avatar.svg'}" alt="Profile" class="user-avatar">
                                    <div class="user-info">
                                        <h3>${user.full_name}</h3>
                                        <div class="user-title">${user.title || 'No title specified'}</div>
                                        <div class="user-company">${user.company || 'No company specified'}</div>
                                    </div>
                                </div>
                                
                                <div class="user-details">
                                    <div class="detail-item">
                                        <i class="fas fa-map-marker-alt"></i>
                                        <span>${user.location || 'Location not specified'}</span>
                                    </div>
                                    <div class="detail-item">
                                        <i class="fas fa-industry"></i>
                                        <span>${user.industry || 'Industry not specified'}</span>
                                    </div>
                                    <div class="detail-item">
                                        <i class="fas fa-briefcase"></i>
                                        <span>${user.experience_years || 0} years experience</span>
                                    </div>
                                    <div class="detail-item">
                                        <i class="fas fa-users"></i>
                                        <span>${user.mutual_connections || 0} mutual connections</span>
                                    </div>
                                </div>
                                
                                ${user.bio ? `<div class="user-bio" style="margin-bottom: 1rem; color: #666; font-style: italic;">"${user.bio}"</div>` : ''}
                                
                                <div class="profile-completeness">
                                    <div class="completeness-bar">
                                        <div class="completeness-fill" style="width: ${user.profile_completeness || 0}%"></div>
                                    </div>
                                    <div class="completeness-text">Profile ${user.profile_completeness || 0}% complete</div>
                                </div>
                                
                                <div class="action-buttons">
                                    ${getConnectionButton(user)}
                                    <button class="btn btn-secondary" onclick="viewProfile(${user.id})">
                                        <i class="fas fa-eye"></i> View Profile
                                    </button>
                                </div>
                            </div>
                        `).join('');
                        
                        container.innerHTML = resultsHTML;
                        
                        // Show pagination if needed
                        if (totalPages > 1) {
                            showPagination();
                        } else {
                            document.getElementById('pagination').style.display = 'none';
                        }
                    }
                    
                    function getConnectionButton(user) {
                        const status = user.connection_status;
                        
                        if (status === 'connected') {
                            return `<button class="btn btn-success" disabled><i class="fas fa-check"></i> Connected</button>`;
                        } else if (status === 'pending_sent') {
                            return `<button class="btn btn-warning" disabled><i class="fas fa-clock"></i> Request Sent</button>`;
                        } else if (status === 'pending_received') {
                            return `<button class="btn btn-primary" onclick="acceptConnection(${user.id})">
                                <i class="fas fa-user-plus"></i> Accept Request
                            </button>`;
                        } else {
                            return `<button class="btn btn-primary" onclick="sendConnectionRequest(${user.id})">
                                <i class="fas fa-user-plus"></i> Connect
                            </button>`;
                        }
                    }
                    
                    function showNoResults() {
                        const container = document.getElementById('searchResults');
                        const countContainer = document.getElementById('resultsCount');
                        
                        countContainer.textContent = 'No results found';
                        container.innerHTML = `
                            <div class="no-results">
                                <i class="fas fa-search"></i>
                                <p>No people found matching your search criteria.</p>
                                <p>Try adjusting your filters or search terms.</p>
                            </div>
                        `;
                        
                        document.getElementById('pagination').style.display = 'none';
                    }
                    
                    function showError(message) {
                        const container = document.getElementById('searchResults');
                        container.innerHTML = `
                            <div class="no-results">
                                <i class="fas fa-exclamation-triangle"></i>
                                <p>${message}</p>
                            </div>
                        `;
                    }
                    
                    function showPagination() {
                        const pagination = document.getElementById('pagination');
                        pagination.style.display = 'flex';
                        
                        let paginationHTML = '';
                        
                        // Previous button
                        paginationHTML += `<button class="page-btn" onclick="changePage(${currentPage - 1})" ${currentPage <= 1 ? 'disabled' : ''}>
                            <i class="fas fa-chevron-left"></i> Previous
                        </button>`;
                        
                        // Page numbers
                        for (let i = 1; i <= totalPages; i++) {
                            if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                                paginationHTML += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">${i}</button>`;
                            } else if (i === currentPage - 3 || i === currentPage + 3) {
                                paginationHTML += `<span class="page-btn" style="cursor: default;">...</span>`;
                            }
                        }
                        
                        // Next button
                        paginationHTML += `<button class="page-btn" onclick="changePage(${currentPage + 1})" ${currentPage >= totalPages ? 'disabled' : ''}>
                            Next <i class="fas fa-chevron-right"></i>
                        </button>`;
                        
                        pagination.innerHTML = paginationHTML;
                    }
                    
                    function changePage(page) {
                        if (page < 1 || page > totalPages) return;
                        
                        currentPage = page;
                        performSearch();
                        
                        // Scroll to top of results
                        document.getElementById('searchResults').scrollIntoView({ behavior: 'smooth' });
                    }
                    
                    function clearFilters() {
                        document.getElementById('searchQuery').value = '';
                        document.getElementById('searchType').value = 'all';
                        document.getElementById('location').value = '';
                        document.getElementById('industry').value = '';
                        document.getElementById('company').value = '';
                        document.getElementById('title').value = '';
                        document.getElementById('experienceMin').value = '';
                        document.getElementById('experienceMax').value = '';
                        document.getElementById('userType').value = '';
                        document.getElementById('sortBy').value = 'relevance';
                        document.getElementById('sortOrder').value = 'asc';
                        
                        // Reset results
                        currentPage = 1;
                        document.getElementById('searchResults').innerHTML = `
                            <div class="no-results">
                                <i class="fas fa-search"></i>
                                <p>Enter your search criteria above to find people</p>
                            </div>
                        `;
                        document.getElementById('resultsCount').textContent = 'Start your search to find people';
                        document.getElementById('pagination').style.display = 'none';
                    }
                    
                    async function sendConnectionRequest(userId) {
                        try {
                            const response = await fetch('/connections/api/request', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    receiver_id: userId,
                                    message: 'I would like to connect with you on Qrow IQ!'
                                })
                            });
                            
                            if (response.ok) {
                                alert('Connection request sent successfully!');
                                performSearch(); // Refresh results
                            } else {
                                alert('Failed to send connection request. Please try again.');
                            }
                        } catch (error) {
                            console.error('Error sending connection request:', error);
                            alert('An error occurred. Please try again.');
                        }
                    }
                    
                    async function acceptConnection(userId) {
                        try {
                            const response = await fetch(`/connections/api/accept/${userId}`, {
                                method: 'POST'
                            });
                            
                            if (response.ok) {
                                alert('Connection accepted!');
                                performSearch(); // Refresh results
                            } else {
                                alert('Failed to accept connection. Please try again.');
                            }
                        } catch (error) {
                            console.error('Error accepting connection:', error);
                            alert('An error occurred. Please try again.');
                        }
                    }
                    
                    function viewProfile(userId) {
                        // TODO: Implement profile view functionality
                        alert('Profile view functionality coming soon!');
                    }
                </script>
            </body>
            </html>
            """
        )
        
    except Exception as e:
        logging.error(f"Error loading enhanced search page: {str(e)}")
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Find People</title></head>
                <body>
                    <h1>Find People</h1>
                    <p>Error: {str(e)}</p>
                    <a href="/connections/">Back to My Network</a>
                </body>
            </html>
            """
        )

@router.get("/find-connections", response_class=HTMLResponse)
def find_connections_page(request: Request, db: Session = Depends(get_db)):
    """Find Connections page with user-friendly interface"""
    try:
        user_id = get_authenticated_user_id(request, db)
        current_user = db.query(User).get(user_id)
        
        if not current_user:
            return HTMLResponse(
                content="""
                <html>
                    <head><title>Find Connections</title></head>
                    <body>
                        <h1>Error</h1>
                        <p>User not found</p>
                        <a href="/connections/">Back to My Network</a>
                    </body>
                </html>
                """
            )
        
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <title>Find Connections - Qrow IQ</title>
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">
                    <style>
                        * {{
                            margin: 0;
                            padding: 0;
                            box-sizing: border-box;
                        }}
                        
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            min-height: 100vh;
                            color: #333;
                        }}
                        
                        .header {{
                            background: rgba(255, 255, 255, 0.95);
                            backdrop-filter: blur(10px);
                            padding: 2rem;
                            text-align: center;
                            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                        }}
                        
                        .header h1 {{
                            color: #667eea;
                            margin-bottom: 0.5rem;
                            font-size: 2.5rem;
                        }}
                        
                        .header p {{
                            color: #666;
                            font-size: 1.1rem;
                        }}
                        
                        .container {{
                            max-width: 1200px;
                            margin: 2rem auto;
                            padding: 0 1rem;
                        }}
                        
                        .search-section {{
                            background: rgba(255, 255, 255, 0.95);
                            backdrop-filter: blur(10px);
                            border-radius: 15px;
                            padding: 2rem;
                            margin-bottom: 2rem;
                            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                        }}
                        
                        .search-filters {{
                            display: grid;
                            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                            gap: 1rem;
                            margin-bottom: 1.5rem;
                        }}
                        
                        .filter-group {{
                            display: flex;
                            flex-direction: column;
                        }}
                        
                        .filter-group label {{
                            font-weight: 600;
                            margin-bottom: 0.5rem;
                            color: #555;
                        }}
                        
                        .filter-group input, .filter-group select {{
                            padding: 0.75rem;
                            border: 2px solid #e1e5e9;
                            border-radius: 8px;
                            font-size: 1rem;
                            transition: border-color 0.3s;
                        }}
                        
                        .filter-group input:focus, .filter-group select:focus {{
                            outline: none;
                            border-color: #667eea;
                        }}
                        
                        .search-btn {{
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            border: none;
                            padding: 1rem 2rem;
                            border-radius: 8px;
                            font-size: 1.1rem;
                            font-weight: 600;
                            cursor: pointer;
                            transition: transform 0.3s;
                            grid-column: 1 / -1;
                            justify-self: center;
                        }}
                        
                        .search-btn:hover {{
                            transform: translateY(-2px);
                        }}
                        
                        .suggestions-section {{
                            background: rgba(255, 255, 255, 0.95);
                            backdrop-filter: blur(10px);
                            border-radius: 15px;
                            padding: 2rem;
                            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                        }}
                        
                        .suggestions-header {{
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: 2rem;
                            padding-bottom: 1rem;
                            border-bottom: 2px solid #e1e5e9;
                        }}
                        
                        .suggestions-header h2 {{
                            color: #667eea;
                            font-size: 1.8rem;
                        }}
                        
                        .suggestions-grid {{
                            display: grid;
                            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                            gap: 1.5rem;
                        }}
                        
                        .suggestion-card {{
                            background: white;
                            border-radius: 12px;
                            padding: 1.5rem;
                            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                            transition: transform 0.3s, box-shadow 0.3s;
                            border: 1px solid #e1e5e9;
                        }}
                        
                        .suggestion-card:hover {{
                            transform: translateY(-5px);
                            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
                        }}
                        
                        .user-header {{
                            display: flex;
                            align-items: center;
                            margin-bottom: 1rem;
                        }}
                        
                        .user-avatar {{
                            width: 60px;
                            height: 60px;
                            border-radius: 50%;
                            object-fit: cover;
                            margin-right: 1rem;
                            border: 3px solid #667eea;
                        }}
                        
                        .user-info h3 {{
                            color: #333;
                            margin-bottom: 0.25rem;
                            font-size: 1.2rem;
                        }}
                        
                        .user-info .title {{
                            color: #667eea;
                            font-weight: 600;
                            margin-bottom: 0.25rem;
                        }}
                        
                        .user-info .company {{
                            color: #666;
                            font-size: 0.9rem;
                        }}
                        
                        .connection-reason {{
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            padding: 0.5rem 1rem;
                            border-radius: 20px;
                            font-size: 0.9rem;
                            font-weight: 600;
                            margin-bottom: 1rem;
                            display: inline-block;
                        }}
                        
                        .user-details {{
                            margin-bottom: 1rem;
                        }}
                        
                        .detail-item {{
                            display: flex;
                            align-items: center;
                            margin-bottom: 0.5rem;
                            font-size: 0.9rem;
                            color: #666;
                        }}
                        
                        .detail-item i {{
                            margin-right: 0.5rem;
                            color: #667eea;
                            width: 16px;
                        }}
                        
                        .profile-completeness {{
                            background: #f8f9fa;
                            border-radius: 8px;
                            padding: 0.75rem;
                            margin-bottom: 1rem;
                        }}
                        
                        .completeness-bar {{
                            background: #e1e5e9;
                            height: 8px;
                            border-radius: 4px;
                            overflow: hidden;
                            margin-bottom: 0.5rem;
                        }}
                        
                        .completeness-fill {{
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            height: 100%;
                            transition: width 0.3s;
                        }}
                        
                        .completeness-text {{
                            font-size: 0.8rem;
                            color: #666;
                            text-align: center;
                        }}
                        
                        .action-buttons {{
                            display: flex;
                            gap: 0.5rem;
                        }}
                        
                        .btn {{
                            flex: 1;
                            padding: 0.75rem;
                            border: none;
                            border-radius: 8px;
                            font-weight: 600;
                            cursor: pointer;
                            transition: all 0.3s;
                            text-decoration: none;
                            text-align: center;
                            display: inline-block;
                        }}
                        
                        .btn-primary {{
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                        }}
                        
                        .btn-primary:hover {{
                            transform: translateY(-2px);
                            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                        }}
                        
                        .btn-secondary {{
                            background: #f8f9fa;
                            color: #667eea;
                            border: 2px solid #667eea;
                        }}
                        
                        .btn-secondary:hover {{
                            background: #667eea;
                            color: white;
                        }}
                        
                        .nav-buttons {{
                            display: flex;
                            justify-content: center;
                            gap: 1rem;
                            margin-top: 2rem;
                        }}
                        
                        .nav-btn {{
                            background: rgba(255, 255, 255, 0.9);
                            color: #667eea;
                            padding: 1rem 2rem;
                            border-radius: 8px;
                            text-decoration: none;
                            font-weight: 600;
                            transition: all 0.3s;
                            border: 2px solid transparent;
                        }}
                        
                        .nav-btn:hover {{
                            background: #667eea;
                            color: white;
                            transform: translateY(-2px);
                        }}
                        
                        .loading {{
                            text-align: center;
                            padding: 2rem;
                            color: #666;
                        }}
                        
                        .no-suggestions {{
                            text-align: center;
                            padding: 3rem;
                            color: #666;
                        }}
                        
                        .no-suggestions i {{
                            font-size: 4rem;
                            color: #ddd;
                            margin-bottom: 1rem;
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1><i class="fas fa-user-plus"></i> Find Connections</h1>
                        <p>Discover and connect with professionals in your network</p>
                    </div>
                    
                    <div class="container">
                        <div class="search-section">
                            <h2><i class="fas fa-search"></i> Search Filters</h2>
                            <div class="search-filters">
                                <div class="filter-group">
                                    <label for="location">Location</label>
                                    <input type="text" id="location" placeholder="Enter location">
                                </div>
                                <div class="filter-group">
                                    <label for="industry">Industry</label>
                                    <input type="text" id="industry" placeholder="Enter industry">
                                </div>
                                <div class="filter-group">
                                    <label for="company">Company</label>
                                    <input type="text" id="company" placeholder="Enter company">
                                </div>
                                <div class="filter-group">
                                    <label for="title">Job Title</label>
                                    <input type="text" id="title" placeholder="Enter job title">
                                </div>
                                <button class="search-btn" onclick="searchConnections()">
                                    <i class="fas fa-search"></i> Search Connections
                                </button>
                            </div>
                        </div>
                        
                        <div class="suggestions-section">
                            <div class="suggestions-header">
                                <h2><i class="fas fa-users"></i> Connection Suggestions</h2>
                                <div>
                                    <span id="suggestions-count">0</span> suggestions found
                                </div>
                            </div>
                            
                            <div id="suggestions-container">
                                <div class="loading">
                                    <i class="fas fa-spinner fa-spin"></i>
                                    <p>Loading suggestions...</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="nav-buttons">
                            <a href="/connections/search" class="nav-btn">
                                <i class="fas fa-search"></i> Enhanced Search
                            </a>
                            <a href="/connections/" class="nav-btn">
                                <i class="fas fa-arrow-left"></i> Back to My Network
                            </a>
                            <a href="/home" class="nav-btn">
                                <i class="fas fa-home"></i> Home
                            </a>
                        </div>
                    </div>
                    
                    <script>
                        // Load suggestions when page loads
                        document.addEventListener('DOMContentLoaded', function() {{
                            loadSuggestions();
                        }});
                        
                        function loadSuggestions() {{
                            const container = document.getElementById('suggestions-container');
                            container.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i><p>Loading suggestions...</p></div>';
                            
                            fetch('/connections/api/suggestions')
                                .then(response => response.json())
                                .then(data => {{
                                    displaySuggestions(data.suggestions);
                                    document.getElementById('suggestions-count').textContent = data.suggestions.length;
                                }})
                                .catch(error => {{
                                    console.error('Error loading suggestions:', error);
                                    container.innerHTML = '<div class="no-suggestions"><i class="fas fa-exclamation-triangle"></i><p>Error loading suggestions. Please try again.</p></div>';
                                }});
                        }}
                        
                        function displaySuggestions(suggestions) {{
                            const container = document.getElementById('suggestions-container');
                            
                            if (!suggestions || suggestions.length === 0) {{
                                container.innerHTML = '<div class="no-suggestions"><i class="fas fa-user-plus"></i><p>No suggestions found. Try adjusting your search filters.</p></div>';
                                return;
                            }}
                            
                            const suggestionsHTML = suggestions.map(suggestion => `
                                <div class="suggestion-card">
                                    <div class="user-header">
                                        <img src="${{suggestion.profile_image || '/static/uploads/default-avatar.svg'}}" alt="Profile" class="user-avatar">
                                        <div class="user-info">
                                            <h3>${{suggestion.full_name}}</h3>
                                            <div class="title">${{suggestion.title}}</div>
                                            <div class="company">${{suggestion.company}}</div>
                                        </div>
                                    </div>
                                    
                                    <div class="connection-reason">${{suggestion.reason}}</div>
                                    
                                    <div class="user-details">
                                        <div class="detail-item">
                                            <i class="fas fa-map-marker-alt"></i>
                                            <span>${{suggestion.location}}</span>
                                        </div>
                                        <div class="detail-item">
                                            <i class="fas fa-industry"></i>
                                            <span>${{suggestion.industry}}</span>
                                        </div>
                                        <div class="detail-item">
                                            <i class="fas fa-users"></i>
                                            <span>${{suggestion.mutual_count}} mutual connections</span>
                                        </div>
                                    </div>
                                    
                                    <div class="profile-completeness">
                                        <div class="completeness-bar">
                                            <div class="completeness-fill" style="width: ${{suggestion.profile_completeness || 0}}%"></div>
                                        </div>
                                        <div class="completeness-text">Profile ${{suggestion.profile_completeness || 0}}% complete</div>
                                    </div>
                                    
                                    <div class="action-buttons">
                                        <button class="btn btn-primary" onclick="sendConnectionRequest(${{suggestion.id}})">
                                            <i class="fas fa-user-plus"></i> Connect
                                        </button>
                                        <button class="btn btn-secondary" onclick="viewProfile(${{suggestion.id}})">
                                            <i class="fas fa-eye"></i> View Profile
                                        </button>
                                    </div>
                                </div>
                            `).join('');
                            
                            container.innerHTML = suggestionsHTML;
                        }}
                        
                        function searchConnections() {{
                            const location = document.getElementById('location').value;
                            const industry = document.getElementById('industry').value;
                            const company = document.getElementById('company').value;
                            const title = document.getElementById('title').value;
                            
                            // For now, just reload suggestions
                            // In the future, this could filter the API call
                            loadSuggestions();
                        }}
                        
                        function sendConnectionRequest(userId) {{
                            // TODO: Implement connection request functionality
                            alert('Connection request functionality coming soon!');
                        }}
                        
                        function viewProfile(userId) {{
                            // TODO: Implement profile view functionality
                            alert('Profile view functionality coming soon!');
                        }}
                    </script>
                </body>
            </html>
            """
        )
        
    except Exception as e:
        logging.error(f"Error loading find connections page: {str(e)}")
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Find Connections</title></head>
                <body>
                    <h1>Find Connections</h1>
                    <p>Error: {str(e)}</p>
                    <a href="/connections/">Back to My Network</a>
                </body>
            </html>
            """
        )

@router.get("/search", response_class=HTMLResponse)
def enhanced_search_page(request: Request, db: Session = Depends(get_db)):
    """Enhanced search page with LinkedIn-like interface"""
    try:
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Find People - Qrow IQ</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    
                    body {{
                        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background-color: #f3f2ef;
                        color: #191919;
                        line-height: 1.6;
                    }}
                    
                    .header {{
                        background: linear-gradient(135deg, #0077b5 0%, #005885 100%);
                        color: white;
                        padding: 2rem 0;
                        text-align: center;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    
                    .header h1 {{
                        font-size: 2.5rem;
                        font-weight: 700;
                        margin-bottom: 0.5rem;
                    }}
                    
                    .header p {{
                        font-size: 1.1rem;
                        opacity: 0.9;
                    }}
                    
                    .container {{
                        max-width: 1200px;
                        margin: 2rem auto;
                        padding: 0 1rem;
                    }}
                    
                    .search-section {{
                        background: white;
                        border-radius: 12px;
                        padding: 2rem;
                        margin-bottom: 2rem;
                        box-shadow: 0 2px 20px rgba(0,0,0,0.08);
                    }}
                    
                    .search-header {{
                        margin-bottom: 1.5rem;
                    }}
                    
                    .search-header h2 {{
                        font-size: 1.5rem;
                        color: #191919;
                        margin-bottom: 0.5rem;
                    }}
                    
                    .search-input-group {{
                        position: relative;
                        margin-bottom: 1.5rem;
                    }}
                    
                    .search-input {{
                        width: 100%;
                        padding: 1rem 1rem 1rem 3rem;
                        border: 2px solid #e0e0e0;
                        border-radius: 8px;
                        font-size: 1rem;
                        transition: all 0.3s ease;
                        background: #fafafa;
                    }}
                    
                    .search-input:focus {{
                        outline: none;
                        border-color: #0077b5;
                        background: white;
                        box-shadow: 0 0 0 3px rgba(0,119,181,0.1);
                    }}
                    
                    .search-icon {{
                        position: absolute;
                        left: 1rem;
                        top: 50%;
                        transform: translateY(-50%);
                        color: #666;
                        font-size: 1.2rem;
                    }}
                    
                    .filters-row {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 1rem;
                        margin-bottom: 1.5rem;
                    }}
                    
                    .filter-group {{
                        display: flex;
                        flex-direction: column;
                    }}
                    
                    .filter-group label {{
                        font-weight: 600;
                        margin-bottom: 0.5rem;
                        color: #191919;
                        font-size: 0.9rem;
                    }}
                    
                    .filter-group input, .filter-group select {{
                        padding: 0.75rem;
                        border: 1px solid #e0e0e0;
                        border-radius: 6px;
                        font-size: 0.9rem;
                        transition: border-color 0.3s ease;
                    }}
                    
                    .filter-group input:focus, .filter-group select:focus {{
                        outline: none;
                        border-color: #0077b5;
                    }}
                    
                    .search-actions {{
                        display: flex;
                        gap: 1rem;
                        align-items: center;
                        flex-wrap: wrap;
                    }}
                    
                    .search-btn {{
                        background: #0077b5;
                        color: white;
                        border: none;
                        padding: 1rem 2rem;
                        border-radius: 8px;
                        font-size: 1rem;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                    }}
                    
                    .search-btn:hover {{
                        background: #005885;
                        transform: translateY(-1px);
                        box-shadow: 0 4px 12px rgba(0,119,181,0.3);
                    }}
                    
                    .clear-btn {{
                        background: #f0f0f0;
                        color: #666;
                        border: none;
                        padding: 1rem 2rem;
                        border-radius: 8px;
                        font-size: 1rem;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    }}
                    
                    .clear-btn:hover {{
                        background: #e0e0e0;
                        color: #333;
                    }}
                    
                    .results-section {{
                        background: white;
                        border-radius: 12px;
                        padding: 2rem;
                        box-shadow: 0 2px 20px rgba(0,0,0,0.08);
                    }}
                    
                    .results-header {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 1.5rem;
                        padding-bottom: 1rem;
                        border-bottom: 1px solid #e0e0e0;
                    }}
                    
                    .results-count {{
                        color: #666;
                        font-size: 0.9rem;
                    }}
                    
                    .sort-controls {{
                        display: flex;
                        gap: 1rem;
                        align-items: center;
                    }}
                    
                    .sort-controls select {{
                        padding: 0.5rem;
                        border: 1px solid #e0e0e0;
                        border-radius: 4px;
                        font-size: 0.9rem;
                    }}
                    
                    .user-card {{
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        padding: 1.5rem;
                        margin-bottom: 1rem;
                        transition: all 0.3s ease;
                        background: #fafafa;
                    }}
                    
                    .user-card:hover {{
                        border-color: #0077b5;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                        transform: translateY(-2px);
                    }}
                    
                    .user-header {{
                        display: flex;
                        align-items: center;
                        margin-bottom: 1rem;
                    }}
                    
                    .user-avatar {{
                        width: 60px;
                        height: 60px;
                        border-radius: 50%;
                        object-fit: cover;
                        margin-right: 1rem;
                        border: 3px solid #0077b5;
                    }}
                    
                    .user-info h3 {{
                        font-size: 1.2rem;
                        color: #191919;
                        margin-bottom: 0.25rem;
                    }}
                    
                    .user-title {{
                        color: #666;
                        font-weight: 500;
                        margin-bottom: 0.25rem;
                    }}
                    
                    .user-company {{
                        color: #0077b5;
                        font-weight: 600;
                    }}
                    
                    .user-details {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                        gap: 1rem;
                        margin-bottom: 1rem;
                    }}
                    
                    .detail-item {{
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                        color: #666;
                        font-size: 0.9rem;
                    }}
                    
                    .detail-item i {{
                        color: #0077b5;
                        width: 16px;
                    }}
                    
                    .profile-completeness {{
                        margin-bottom: 1rem;
                    }}
                    
                    .completeness-bar {{
                        width: 100%;
                        height: 8px;
                        background: #e0e0e0;
                        border-radius: 4px;
                        overflow: hidden;
                        margin-bottom: 0.5rem;
                    }}
                    
                    .completeness-fill {{
                        height: 100%;
                        background: linear-gradient(90deg, #0077b5, #00a0dc);
                        transition: width 0.3s ease;
                    }}
                    
                    .completeness-text {{
                        font-size: 0.8rem;
                        color: #666;
                    }}
                    
                    .action-buttons {{
                        display: flex;
                        gap: 1rem;
                        flex-wrap: wrap;
                    }}
                    
                    .btn {{
                        padding: 0.75rem 1.5rem;
                        border: none;
                        border-radius: 6px;
                        font-size: 0.9rem;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                    }}
                    
                    .btn-primary {{
                        background: #0077b5;
                        color: white;
                    }}
                    
                    .btn-primary:hover {{
                        background: #005885;
                        transform: translateY(-1px);
                    }}
                    
                    .btn-secondary {{
                        background: transparent;
                        color: #0077b5;
                        border: 1px solid #0077b5;
                    }}
                    
                    .btn-secondary:hover {{
                        background: #0077b5;
                        color: white;
                    }}
                    
                    .btn-success {{
                        background: #28a745;
                        color: white;
                    }}
                    
                    .btn-success:hover {{
                        background: #218838;
                    }}
                    
                    .btn-warning {{
                        background: #ffc107;
                        color: #212529;
                    }}
                    
                    .btn-warning:hover {{
                        background: #e0a800;
                    }}
                    
                    .loading {{
                        text-align: center;
                        padding: 3rem;
                        color: #666;
                    }}
                    
                    .loading i {{
                        font-size: 2rem;
                        color: #0077b5;
                        margin-bottom: 1rem;
                    }}
                    
                    .no-results {{
                        text-align: center;
                        padding: 3rem;
                        color: #666;
                    }}
                    
                    .no-results i {{
                        font-size: 3rem;
                        color: #ccc;
                        margin-bottom: 1rem;
                    }}
                    
                    .pagination {{
                        display: flex;
                        justify-content: center;
                        gap: 0.5rem;
                        margin-top: 2rem;
                    }}
                    
                    .page-btn {{
                        padding: 0.5rem 1rem;
                        border: 1px solid #e0e0e0;
                        background: white;
                        color: #666;
                        border-radius: 4px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    }}
                    
                    .page-btn:hover {{
                        background: #f0f0f0;
                        border-color: #0077b5;
                        color: #0077b5;
                    }}
                    
                    .page-btn.active {{
                        background: #0077b5;
                        color: white;
                        border-color: #0077b5;
                    }}
                    
                    .page-btn:disabled {{
                        opacity: 0.5;
                        cursor: not-allowed;
                    }}
                    
                    .suggestions {{
                        background: #f8f9fa;
                        border-radius: 8px;
                        padding: 1rem;
                        margin-top: 1rem;
                    }}
                    
                    .suggestions h4 {{
                        color: #191919;
                        margin-bottom: 0.5rem;
                        font-size: 0.9rem;
                    }}
                    
                    .suggestion-tags {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 0.5rem;
                    }}
                    
                    .suggestion-tag {{
                        background: white;
                        border: 1px solid #e0e0e0;
                        padding: 0.25rem 0.75rem;
                        border-radius: 20px;
                        font-size: 0.8rem;
                        color: #666;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    }}
                    
                    .suggestion-tag:hover {{
                        background: #0077b5;
                        color: white;
                        border-color: #0077b5;
                    }}
                    
                    @media (max-width: 768px) {{
                        .container {{
                            padding: 1rem;
                        }}
                        
                        .filters-row {{
                            grid-template-columns: 1fr;
                        }}
                        
                        .search-actions {{
                            flex-direction: column;
                        }}
                        
                        .search-btn, .clear-btn {{
                            width: 100%;
                        }}
                        
                        .results-header {{
                            flex-direction: column;
                            gap: 1rem;
                            align-items: flex-start;
                        }}
                        
                        .action-buttons {{
                            flex-direction: column;
                        }}
                        
                        .btn {{
                            width: 100%;
                            justify-content: center;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1><i class="fas fa-search"></i> Find People</h1>
                    <p>Discover and connect with professionals in your network</p>
                </div>
                
                <div class="container">
                    <div class="search-section">
                        <div class="search-header">
                            <h2><i class="fas fa-filter"></i> Search & Filters</h2>
                            <p>Find people by name, company, skills, location, and more</p>
                        </div>
                        
                        <div class="search-input-group">
                            <i class="fas fa-search search-icon"></i>
                            <input type="text" id="searchQuery" class="search-input" placeholder="Search for people, companies, skills, titles...">
                        </div>
                        
                        <div class="filters-row">
                            <div class="filter-group">
                                <label for="searchType">Search Type</label>
                                <select id="searchType">
                                    <option value="all">All Fields</option>
                                    <option value="name">Name</option>
                                    <option value="company">Company</option>
                                    <option value="title">Job Title</option>
                                    <option value="skills">Skills</option>
                                    <option value="location">Location</option>
                                    <option value="industry">Industry</option>
                                    <option value="education">Education</option>
                                </select>
                            </div>
                            
                            <div class="filter-group">
                                <label for="location">Location</label>
                                <input type="text" id="location" placeholder="e.g., San Francisco, CA">
                            </div>
                            
                            <div class="filter-group">
                                <label for="industry">Industry</label>
                                <input type="text" id="industry" placeholder="e.g., Technology, Healthcare">
                            </div>
                            
                            <div class="filter-group">
                                <label for="company">Company</label>
                                <input type="text" id="company" placeholder="e.g., Google, Microsoft">
                            </div>
                            
                            <div class="filter-group">
                                <label for="title">Job Title</label>
                                <input type="text" id="title" placeholder="e.g., Software Engineer, Manager">
                            </div>
                            
                            <div class="filter-group">
                                <label for="experienceMin">Min Experience (years)</label>
                                <input type="number" id="experienceMin" min="0" max="50" placeholder="0">
                            </div>
                            
                            <div class="filter-group">
                                <label for="experienceMax">Max Experience (years)</label>
                                <input type="number" id="experienceMax" min="0" max="50" placeholder="20">
                            </div>
                            
                            <div class="filter-group">
                                <label for="userType">User Type</label>
                                <select id="userType">
                                    <option value="">All Types</option>
                                    <option value="normal">Normal</option>
                                    <option value="domain">Domain</option>
                                    <option value="premium">Premium</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="search-actions">
                            <button class="search-btn" onclick="performSearch()">
                                <i class="fas fa-search"></i> Search
                            </button>
                            <button class="clear-btn" onclick="clearFilters()">
                                <i class="fas fa-times"></i> Clear Filters
                            </button>
                        </div>
                        
                        <div class="suggestions">
                            <h4><i class="fas fa-lightbulb"></i> Popular Searches</h4>
                            <div class="suggestion-tags" id="popularSearches">
                                <!-- Popular searches will be loaded here -->
                            </div>
                        </div>
                    </div>
                    
                    <div class="results-section">
                        <div class="results-header">
                            <div>
                                <h2><i class="fas fa-users"></i> Search Results</h2>
                                <div class="results-count" id="resultsCount">Start your search to find people</div>
                            </div>
                            
                            <div class="sort-controls">
                                <label for="sortBy">Sort by:</label>
                                <select id="sortBy">
                                    <option value="relevance">Relevance</option>
                                    <option value="name">Name</option>
                                    <option value="company">Company</option>
                                    <option value="location">Location</option>
                                    <option value="experience">Experience</option>
                                    <option value="mutual_connections">Mutual Connections</option>
                                </select>
                                
                                <label for="sortOrder">Order:</label>
                                <select id="sortOrder">
                                    <option value="asc">A-Z</option>
                                    <option value="desc">Z-A</option>
                                </select>
                            </div>
                        </div>
                        
                        <div id="searchResults">
                            <div class="no-results">
                                <i class="fas fa-search"></i>
                                <p>Enter your search criteria above to find people</p>
                            </div>
                        </div>
                        
                        <div class="pagination" id="pagination" style="display: none;">
                            <!-- Pagination will be generated here -->
                        </div>
                    </div>
                </div>
                
                <script>
                    let currentPage = 1;
                    let currentResults = [];
                    let totalPages = 0;
                    
                    // Load popular searches on page load
                    document.addEventListener('DOMContentLoaded', function() {{
                        loadPopularSearches();
                        
                        // Add enter key support for search
                        document.getElementById('searchQuery').addEventListener('keypress', function(e) {{
                            if (e.key === 'Enter') {{
                                performSearch();
                            }}
                        }});
                        
                        // Add real-time search suggestions
                        document.getElementById('searchQuery').addEventListener('input', function(e) {{
                            if (e.target.value.length >= 2) {{
                                getSearchSuggestions(e.target.value);
                            }}
                        }});
                    }});
                    
                    async function loadPopularSearches() {{
                        try {{
                            const response = await fetch('/connections/api/search/popular');
                            const data = await response.json();
                            
                            const container = document.getElementById('popularSearches');
                            container.innerHTML = data.popular_searches.map(term => 
                                `<span class="suggestion-tag" onclick="useSearchTerm('${{term}}')">${{term}}</span>`
                            ).join('');
                        }} catch (error) {{
                            console.error('Error loading popular searches:', error);
                        }}
                    }}
                    
                    function useSearchTerm(term) {{
                        document.getElementById('searchQuery').value = term;
                        performSearch();
                    }}
                    
                    async function getSearchSuggestions(query) {{
                        try {{
                            const response = await fetch(`/connections/api/search/suggestions?query=${{encodeURIComponent(query)}}`);
                            const data = await response.json();
                            
                            if (data.suggestions.length > 0) {{
                                // You could show these suggestions in a dropdown
                                console.log('Search suggestions:', data.suggestions);
                            }}
                        }} catch (error) {{
                            console.error('Error getting suggestions:', error);
                        }}
                    }}
                    
                    async function performSearch() {{
                        const query = document.getElementById('searchQuery').value;
                        const searchType = document.getElementById('searchType').value;
                        const location = document.getElementById('location').value;
                        const industry = document.getElementById('industry').value;
                        const company = document.getElementById('company').value;
                        const title = document.getElementById('title').value;
                        const experienceMin = document.getElementById('experienceMin').value;
                        const experienceMax = document.getElementById('experienceMax').value;
                        const userType = document.getElementById('userType').value;
                        const sortBy = document.getElementById('sortBy').value;
                        const sortOrder = document.getElementById('sortOrder').value;
                        
                        // Build query parameters
                        const params = new URLSearchParams();
                        if (query) params.append('query', query);
                        if (searchType) params.append('search_type', searchType);
                        if (location) params.append('location', location);
                        if (industry) params.append('industry', industry);
                        if (company) params.append('company', company);
                        if (title) params.append('title', title);
                        if (experienceMin) params.append('experience_min', experienceMin);
                        if (experienceMax) params.append('experience_max', experienceMax);
                        if (userType) params.append('user_type', userType);
                        if (sortBy) params.append('sort_by', sortBy);
                        if (sortOrder) params.append('sort_order', sortOrder);
                        params.append('page', currentPage);
                        params.append('limit', 20);
                        
                        // Show loading
                        showLoading();
                        
                        try {{
                            const response = await fetch(`/connections/api/search?${{params.toString()}}`);
                            const data = await response.json();
                            
                            if (data.results) {{
                                currentResults = data.results;
                                totalPages = data.pagination.pages;
                                displayResults(data.results, data.pagination);
                            }} else {{
                                showNoResults();
                            }}
                        }} catch (error) {{
                            console.error('Search error:', error);
                            showError('An error occurred while searching. Please try again.');
                        }}
                    }}
                    
                    function showLoading() {{
                        const container = document.getElementById('searchResults');
                        container.innerHTML = `
                            <div class="loading">
                                <i class="fas fa-spinner fa-spin"></i>
                                <p>Searching...</p>
                            </div>
                        `;
                    }}
                    
                    function displayResults(results, pagination) {{
                        const container = document.getElementById('searchResults');
                        const countContainer = document.getElementById('resultsCount');
                        
                        if (!results || results.length === 0) {{
                            showNoResults();
                            return;
                        }}
                        
                        countContainer.textContent = `${{pagination.total}} results found`;
                        
                        const resultsHTML = results.map(user => `
                            <div class="user-card">
                                <div class="user-header">
                                    <img src="${{user.profile_image || '/static/uploads/default-avatar.svg'}}" alt="Profile" class="user-avatar">
                                    <div class="user-info">
                                        <h3>${{user.full_name}}</h3>
                                        <div class="user-title">${{user.title || 'No title specified'}}</div>
                                        <div class="user-company">${{user.company || 'No company specified'}}</div>
                                    </div>
                                </div>
                                
                                <div class="user-details">
                                    <div class="detail-item">
                                        <i class="fas fa-map-marker-alt"></i>
                                        <span>${{user.location || 'Location not specified'}}</span>
                                    </div>
                                    <div class="detail-item">
                                        <i class="fas fa-industry"></i>
                                        <span>${{user.industry || 'Industry not specified'}}</span>
                                    </div>
                                    <div class="detail-item">
                                        <i class="fas fa-briefcase"></i>
                                        <span>${{user.experience_years || 0}} years experience</span>
                                    </div>
                                    <div class="detail-item">
                                        <i class="fas fa-users"></i>
                                        <span>${{user.mutual_connections || 0}} mutual connections</span>
                                    </div>
                                </div>
                                
                                ${{user.bio ? `<div class="user-bio" style="margin-bottom: 1rem; color: #666; font-style: italic;">"${{user.bio}}"</div>` : ''}}
                                
                                <div class="profile-completeness">
                                    <div class="completeness-bar">
                                        <div class="completeness-fill" style="width: ${{user.profile_completeness || 0}}%"></div>
                                    </div>
                                    <div class="completeness-text">Profile ${{user.profile_completeness || 0}}% complete</div>
                                </div>
                                
                                <div class="action-buttons">
                                    ${{getConnectionButton(user)}}
                                    <button class="btn btn-secondary" onclick="viewProfile(${{user.id}})">
                                        <i class="fas fa-eye"></i> View Profile
                                    </button>
                                </div>
                            </div>
                        `).join('');
                        
                        container.innerHTML = resultsHTML;
                        
                        // Show pagination if needed
                        if (totalPages > 1) {{
                            showPagination();
                        }} else {{
                            document.getElementById('pagination').style.display = 'none';
                        }}
                    }}
                    
                    function getConnectionButton(user) {{
                        const status = user.connection_status;
                        
                        if (status === 'connected') {{
                            return `<button class="btn btn-success" disabled><i class="fas fa-check"></i> Connected</button>`;
                        }} else if (status === 'pending_sent') {{
                            return `<button class="btn btn-warning" disabled><i class="fas fa-clock"></i> Request Sent</button>`;
                        }} else if (status === 'pending_received') {{
                            return `<button class="btn btn-primary" onclick="acceptConnection(${{user.id}})">
                                <i class="fas fa-user-plus"></i> Accept Request
                            </button>`;
                        }} else {{
                            return `<button class="btn btn-primary" onclick="sendConnectionRequest(${{user.id}})">
                                <i class="fas fa-user-plus"></i> Connect
                            </button>`;
                        }}
                    }}
                    
                    function showNoResults() {{
                        const container = document.getElementById('searchResults');
                        const countContainer = document.getElementById('resultsCount');
                        
                        countContainer.textContent = 'No results found';
                        container.innerHTML = `
                            <div class="no-results">
                                <i class="fas fa-search"></i>
                                <p>No people found matching your search criteria.</p>
                                <p>Try adjusting your filters or search terms.</p>
                            </div>
                        `;
                        
                        document.getElementById('pagination').style.display = 'none';
                    }}
                    
                    function showError(message) {{
                        const container = document.getElementById('searchResults');
                        container.innerHTML = `
                            <div class="no-results">
                                <i class="fas fa-exclamation-triangle"></i>
                                <p>${{message}}</p>
                            </div>
                        `;
                    }}
                    
                    function showPagination() {{
                        const pagination = document.getElementById('pagination');
                        pagination.style.display = 'flex';
                        
                        let paginationHTML = '';
                        
                        // Previous button
                        paginationHTML += `<button class="page-btn" onclick="changePage(${{currentPage - 1}})" ${{currentPage <= 1 ? 'disabled' : ''}}>
                            <i class="fas fa-chevron-left"></i> Previous
                        </button>`;
                        
                        // Page numbers
                        for (let i = 1; i <= totalPages; i++) {{
                            if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {{
                                paginationHTML += `<button class="page-btn ${{i === currentPage ? 'active' : ''}}" onclick="changePage(${{i}})">${{i}}</button>`;
                            }} else if (i === currentPage - 3 || i === currentPage + 3) {{
                                paginationHTML += `<span class="page-btn" style="cursor: default;">...</span>`;
                            }}
                        }}
                        
                        // Next button
                        paginationHTML += `<button class="page-btn" onclick="changePage(${{currentPage + 1}})" ${{currentPage >= totalPages ? 'disabled' : ''}}>
                            Next <i class="fas fa-chevron-right"></i>
                        </button>`;
                        
                        pagination.innerHTML = paginationHTML;
                    }}
                    
                    function changePage(page) {{
                        if (page < 1 || page > totalPages) return;
                        
                        currentPage = page;
                        performSearch();
                        
                        // Scroll to top of results
                        document.getElementById('searchResults').scrollIntoView({{ behavior: 'smooth' }});
                    }}
                    
                    function clearFilters() {{
                        document.getElementById('searchQuery').value = '';
                        document.getElementById('searchType').value = 'all';
                        document.getElementById('location').value = '';
                        document.getElementById('industry').value = '';
                        document.getElementById('company').value = '';
                        document.getElementById('title').value = '';
                        document.getElementById('experienceMin').value = '';
                        document.getElementById('experienceMax').value = '';
                        document.getElementById('userType').value = '';
                        document.getElementById('sortBy').value = 'relevance';
                        document.getElementById('sortOrder').value = 'asc';
                        
                        // Reset results
                        currentPage = 1;
                        document.getElementById('searchResults').innerHTML = `
                            <div class="no-results">
                                <i class="fas fa-search"></i>
                                <p>Enter your search criteria above to find people</p>
                            </div>
                        `;
                        document.getElementById('resultsCount').textContent = 'Start your search to find people';
                        document.getElementById('pagination').style.display = 'none';
                    }}
                    
                    async function sendConnectionRequest(userId) {{
                        try {{
                            const response = await fetch('/connections/api/send-request', {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/x-www-form-urlencoded',
                                }},
                                body: new URLSearchParams({{
                                    receiver_id: userId,
                                    message: 'I would like to connect with you on Qrow IQ!'
                                }})
                            }});
                            
                            if (response.ok) {{
                                alert('Connection request sent successfully!');
                                performSearch(); // Refresh results
                            }} else {{
                                alert('Failed to send connection request. Please try again.');
                            }}
                        }} catch (error) {{
                            console.error('Error sending connection request:', error);
                            alert('An error occurred. Please try again.');
                        }}
                    }}
                    
                    async function acceptConnection(userId) {{
                        try {{
                            const response = await fetch(`/connections/api/respond-request`, {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/x-www-form-urlencoded',
                                }},
                                body: new URLSearchParams({{
                                    request_id: userId,
                                    response: 'accept'
                                }})
                            }});
                            
                            if (response.ok) {{
                                alert('Connection accepted!');
                                performSearch(); // Refresh results
                            }} else {{
                                alert('Failed to accept connection. Please try again.');
                            }}
                        }} catch (error) {{
                            console.error('Error accepting connection:', error);
                            alert('An error occurred. Please try again.');
                        }}
                    }}
                    
                    function viewProfile(userId) {{
                        // TODO: Implement profile view functionality
                        alert('Profile view functionality coming soon!');
                    }}
                </script>
            </body>
            </html>
            """
        )
        
    except Exception as e:
        logging.error(f"Error loading enhanced search page: {str(e)}")
        return HTMLResponse(
            content=f"""
            <html>
                <head><title>Find People</title></head>
                <body>
                    <h1>Find People</h1>
                    <p>Error: {str(e)}</p>
                    <a href="/connections/">Back to My Network</a>
                </body>
            </html>
            """
        )
