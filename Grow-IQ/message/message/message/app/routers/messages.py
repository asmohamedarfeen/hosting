"""
Messages router for real-time chat functionality.
Handles message creation, chat history, and WebSocket connections.
"""

import json
from typing import List, Dict, Set
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_

from ..db import get_db
from ..models import User, Connection, Message
from ..schemas import MessageCreate, MessageResponse, MessageListResponse, ChatHistoryRequest
from ..auth import get_current_active_user

router = APIRouter(prefix="/messages", tags=["messages"])

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time messaging."""
    
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.user_connections: Dict[int, Set[int]] = {}  # user_id -> set of connected user_ids
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a user's WebSocket."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_connections[user_id] = set()
    
    def disconnect(self, user_id: int):
        """Disconnect a user's WebSocket."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_connections:
            del self.user_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: int):
        """Send a message to a specific user."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except:
                # Remove connection if sending fails
                self.disconnect(user_id)
    
    async def broadcast_to_connection(self, message: str, user1_id: int, user2_id: int):
        """Broadcast message to both users in a connection."""
        await self.send_personal_message(message, user1_id)
        await self.send_personal_message(message, user2_id)

# Global connection manager
manager = ConnectionManager()


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to another user (only if mutually connected).
    
    Args:
        message_data: Message data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Created message
        
    Raises:
        HTTPException: If users are not mutually connected
    """
    # Check if trying to message self
    if message_data.receiver_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send message to yourself"
        )
    
    # Check if receiver user exists
    receiver = db.query(User).filter(
        User.id == message_data.receiver_id,
        User.is_active == True
    ).first()
    
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if users are mutually connected
    connection = db.query(Connection).filter(
        or_(
            and_(
                Connection.sender_id == current_user.id,
                Connection.receiver_id == message_data.receiver_id,
                Connection.status == "accepted"
            ),
            and_(
                Connection.sender_id == message_data.receiver_id,
                Connection.receiver_id == current_user.id,
                Connection.status == "accepted"
            )
        )
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only message mutually connected users"
        )
    
    # Create message
    db_message = Message(
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id,
        content=message_data.content
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Send real-time message via WebSocket if users are online
    message_json = json.dumps({
        "type": "message",
        "id": db_message.id,
        "sender_id": db_message.sender_id,
        "receiver_id": db_message.receiver_id,
        "content": db_message.content,
        "timestamp": db_message.timestamp.isoformat(),
        "sender_name": current_user.name
    })
    
    await manager.broadcast_to_connection(
        message_json,
        current_user.id,
        message_data.receiver_id
    )
    
    return MessageResponse(
        id=db_message.id,
        sender_id=db_message.sender_id,
        receiver_id=db_message.receiver_id,
        content=db_message.content,
        timestamp=db_message.timestamp,
        is_read=db_message.is_read,
        sender=current_user,
        receiver=receiver
    )


@router.get("/chat/{other_user_id}", response_model=MessageListResponse)
async def get_chat_history(
    other_user_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get chat history with another user (only if mutually connected).
    
    Args:
        other_user_id: ID of the other user
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageListResponse: Chat history
        
    Raises:
        HTTPException: If users are not mutually connected
    """
    # Check if users are mutually connected
    connection = db.query(Connection).filter(
        or_(
            and_(
                Connection.sender_id == current_user.id,
                Connection.receiver_id == other_user_id,
                Connection.status == "accepted"
            ),
            and_(
                Connection.sender_id == other_user_id,
                Connection.receiver_id == current_user.id,
                Connection.status == "accepted"
            )
        )
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view chat history with mutually connected users"
        )
    
    # Get total message count
    total = db.query(func.count(Message.id)).filter(
        or_(
            and_(
                Message.sender_id == current_user.id,
                Message.receiver_id == other_user_id
            ),
            and_(
                Message.sender_id == other_user_id,
                Message.receiver_id == current_user.id
            )
        )
    ).scalar()
    
    # Get messages
    messages = (
        db.query(Message, User)
        .join(User, Message.sender_id == User.id)
        .filter(
            or_(
                and_(
                    Message.sender_id == current_user.id,
                    Message.receiver_id == other_user_id
                ),
                and_(
                    Message.sender_id == other_user_id,
                    Message.receiver_id == current_user.id
                )
            )
        )
        .order_by(Message.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    # Convert to response format
    message_responses = []
    for msg, sender in messages:
        # Determine if current user is sender or receiver
        if msg.sender_id == current_user.id:
            receiver = db.query(User).filter(User.id == msg.receiver_id).first()
            message_responses.append(MessageResponse(
                id=msg.id,
                sender_id=msg.sender_id,
                receiver_id=msg.receiver_id,
                content=msg.content,
                timestamp=msg.timestamp,
                is_read=msg.is_read,
                sender=current_user,
                receiver=receiver
            ))
        else:
            message_responses.append(MessageResponse(
                id=msg.id,
                sender_id=msg.sender_id,
                receiver_id=msg.receiver_id,
                content=msg.content,
                timestamp=msg.timestamp,
                is_read=msg.is_read,
                sender=sender,
                receiver=current_user
            ))
    
    return MessageListResponse(
        messages=message_responses,
        total=total
    )


@router.put("/{message_id}/read", response_model=MessageResponse)
async def mark_message_as_read(
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark a message as read.
    
    Args:
        message_id: ID of the message to mark as read
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Updated message
        
    Raises:
        HTTPException: If message not found or unauthorized
    """
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.receiver_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Mark as read
    message.is_read = True
    db.commit()
    db.refresh(message)
    
    # Get sender user details
    sender = db.query(User).filter(User.id == message.sender_id).first()
    
    return MessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        content=message.content,
        timestamp=message.timestamp,
        is_read=message.is_read,
        sender=sender,
        receiver=current_user
    )


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time messaging.
    
    Args:
        websocket: WebSocket connection
        user_id: ID of the connecting user
        token: JWT token for authentication
        db: Database session
    """
    try:
        # Authenticate user
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Verify token and get user
        try:
            current_user = get_current_user_from_token(token, db)
            if current_user.id != user_id:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        except:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Connect WebSocket
        await manager.connect(websocket, user_id)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Handle different message types
                if message_data.get("type") == "typing":
                    # Broadcast typing indicator
                    receiver_id = message_data.get("receiver_id")
                    if receiver_id:
                        typing_json = json.dumps({
                            "type": "typing",
                            "sender_id": user_id,
                            "sender_name": current_user.name
                        })
                        await manager.send_personal_message(typing_json, receiver_id)
                
                elif message_data.get("type") == "read":
                    # Mark message as read
                    message_id = message_data.get("message_id")
                    if message_id:
                        message = db.query(Message).filter(
                            Message.id == message_id,
                            Message.receiver_id == user_id
                        ).first()
                        if message:
                            message.is_read = True
                            db.commit()
                
        except WebSocketDisconnect:
            manager.disconnect(user_id)
            
    except Exception as e:
        # Log error and close connection
        print(f"WebSocket error: {e}")
        if user_id in manager.active_connections:
            manager.disconnect(user_id)
        await websocket.close()


# Helper function to get user from token (for WebSocket)
def get_current_user_from_token(token: str, db: Session) -> User:
    """Get user from JWT token for WebSocket authentication."""
    from ..auth import verify_token
    
    token_data = verify_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
