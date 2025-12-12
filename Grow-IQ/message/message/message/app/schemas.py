"""
Pydantic schemas for request/response validation and data serialization.
Provides type safety and automatic validation for API endpoints.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    bio: Optional[str] = Field(None, max_length=500, description="User's bio")


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")


class UserUpdate(BaseModel):
    """Schema for user profile updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    bio: Optional[str] = Field(None, max_length=500)


class UserResponse(UserBase):
    """Schema for user responses (excludes sensitive data)."""
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for listing users."""
    users: List[UserResponse]
    total: int


# Authentication schemas
class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Schema for JWT token payload."""
    user_id: Optional[int] = None
    email: Optional[str] = None


# Connection schemas
class ConnectionCreate(BaseModel):
    """Schema for creating connection requests."""
    receiver_id: int = Field(..., gt=0, description="ID of user to connect with")


class ConnectionResponse(BaseModel):
    """Schema for connection responses."""
    id: int
    sender_id: int
    receiver_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    sender: UserResponse
    receiver: UserResponse

    class Config:
        from_attributes = True


class ConnectionUpdate(BaseModel):
    """Schema for updating connection status."""
    status: str = Field(..., pattern="^(accepted|rejected)$")


class ConnectionListResponse(BaseModel):
    """Schema for listing connections."""
    sent_connections: List[ConnectionResponse]
    received_connections: List[ConnectionResponse]
    total_sent: int
    total_received: int


# Message schemas
class MessageCreate(BaseModel):
    """Schema for creating messages."""
    receiver_id: int = Field(..., gt=0, description="ID of user to send message to")
    content: str = Field(..., min_length=1, max_length=1000, description="Message content")


class MessageResponse(BaseModel):
    """Schema for message responses."""
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime
    is_read: bool
    sender: UserResponse
    receiver: UserResponse

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Schema for listing messages."""
    messages: List[MessageResponse]
    total: int


class ChatHistoryRequest(BaseModel):
    """Schema for requesting chat history."""
    other_user_id: int = Field(..., gt=0, description="ID of user to get chat history with")
    limit: Optional[int] = Field(50, ge=1, le=100, description="Number of messages to retrieve")
    offset: Optional[int] = Field(0, ge=0, description="Number of messages to skip")


# WebSocket schemas
class WebSocketMessage(BaseModel):
    """Schema for WebSocket message format."""
    type: str = Field(..., description="Message type: 'message', 'typing', 'read'")
    content: Optional[str] = None
    receiver_id: Optional[int] = None
    timestamp: Optional[datetime] = None


# Response schemas
class SuccessResponse(BaseModel):
    """Generic success response."""
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Generic error response."""
    error: str
    detail: Optional[str] = None
    status_code: int
