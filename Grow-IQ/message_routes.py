from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from models import Message, User, Connection
from auth_utils import get_user_from_session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: str
    updated_at: str
    sender: dict
    receiver: dict

def get_authenticated_user_id(request: Request, db: Session) -> int:
    """Get authenticated user ID from session token"""
    try:
        # Get session token from cookie
        session_token = request.cookies.get("session_token")
        if not session_token:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get user from session
        session_data = get_user_from_session(session_token, db)
        if not session_data:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        return session_data['user_id']
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication required")

@router.post("/api/messages/send", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Send a message to another user"""
    sender_id = get_authenticated_user_id(request, db)
    
    # Check if receiver exists
    receiver = db.query(User).filter(User.id == message_data.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    # Check if users are connected
    connection = db.query(Connection).filter(
        ((Connection.user_id == sender_id) & (Connection.connected_user_id == message_data.receiver_id)) |
        ((Connection.user_id == message_data.receiver_id) & (Connection.connected_user_id == sender_id))
    ).filter(Connection.status == 'accepted').first()
    
    if not connection:
        raise HTTPException(status_code=403, detail="You can only message your connections")
    
    # Create the message
    message = Message(
        sender_id=sender_id,
        receiver_id=message_data.receiver_id,
        content=message_data.content
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return MessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        content=message.content,
        is_read=message.is_read,
        created_at=message.created_at.isoformat(),
        updated_at=message.updated_at.isoformat(),
        sender=message.sender.to_dict(),
        receiver=message.receiver.to_dict()
    )

@router.get("/api/messages/chat/{user_id}", response_model=List[MessageResponse])
async def get_chat_history(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get chat history with a specific user"""
    current_user_id = get_authenticated_user_id(request, db)
    
    # Check if users are connected
    connection = db.query(Connection).filter(
        ((Connection.user_id == current_user_id) & (Connection.connected_user_id == user_id)) |
        ((Connection.user_id == user_id) & (Connection.connected_user_id == current_user_id))
    ).filter(Connection.status == 'accepted').first()
    
    if not connection:
        raise HTTPException(status_code=403, detail="You can only view messages with your connections")
    
    # Get messages between the two users
    messages = db.query(Message).filter(
        ((Message.sender_id == current_user_id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user_id))
    ).order_by(Message.created_at.asc()).all()
    
    # Mark messages as read
    for message in messages:
        if message.receiver_id == current_user_id and not message.is_read:
            message.is_read = True
    
    db.commit()
    
    return [
        MessageResponse(
            id=msg.id,
            sender_id=msg.sender_id,
            receiver_id=msg.receiver_id,
            content=msg.content,
            is_read=msg.is_read,
            created_at=msg.created_at.isoformat(),
            updated_at=msg.updated_at.isoformat(),
            sender=msg.sender.to_dict(),
            receiver=msg.receiver.to_dict()
        )
        for msg in messages
    ]

@router.get("/api/messages/conversations", response_model=List[dict])
async def get_conversations(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user"""
    current_user_id = get_authenticated_user_id(request, db)
    
    # Get all unique users the current user has messaged with
    conversations = db.query(Message).filter(
        (Message.sender_id == current_user_id) | (Message.receiver_id == current_user_id)
    ).order_by(Message.created_at.desc()).all()
    
    # Group by conversation partner
    conversation_map = {}
    for message in conversations:
        partner_id = message.sender_id if message.sender_id != current_user_id else message.receiver_id
        if partner_id not in conversation_map:
            conversation_map[partner_id] = {
                'user': message.sender if message.sender_id != current_user_id else message.receiver,
                'last_message': message,
                'unread_count': 0
            }
        else:
            # Update if this is a more recent message
            last_message = conversation_map[partner_id]['last_message']
            if (message.created_at and last_message.created_at and 
                message.created_at > last_message.created_at):
                conversation_map[partner_id]['last_message'] = message
        
        # Count unread messages
        if message.receiver_id == current_user_id and not message.is_read:
            conversation_map[partner_id]['unread_count'] += 1
    
    # Convert to list format
    result = []
    for partner_id, data in conversation_map.items():
        last_message = data['last_message']
        result.append({
            'user': data['user'].to_dict(),
            'last_message': {
                'id': last_message.id if last_message else None,
                'content': last_message.content if last_message else '',
                'created_at': last_message.created_at.isoformat() if last_message and last_message.created_at else None,
                'sender_id': last_message.sender_id if last_message else None
            },
            'unread_count': data['unread_count']
        })
    
    # Sort by last message time (handle null values)
    result.sort(key=lambda x: x['last_message']['created_at'] or '', reverse=True)
    
    return result

@router.put("/api/messages/{message_id}/read")
async def mark_message_read(
    message_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Mark a message as read"""
    current_user_id = get_authenticated_user_id(request, db)
    
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.receiver_id == current_user_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.is_read = True
    db.commit()
    
    return {"success": True, "message": "Message marked as read"}

@router.get("/api/messages/unread-count")
async def get_unread_count(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get unread message count for current user"""
    current_user_id = get_authenticated_user_id(request, db)
    
    unread_count = db.query(Message).filter(
        Message.receiver_id == current_user_id,
        Message.is_read == False
    ).count()
    
    return {"unread_count": unread_count}