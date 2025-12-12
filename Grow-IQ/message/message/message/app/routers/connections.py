"""
Connections router for LinkedIn-like connection management.
Handles connection requests, accept/reject, and connection listing.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_

from ..db import get_db
from ..models import User, Connection
from ..schemas import (
    ConnectionCreate, ConnectionResponse, ConnectionUpdate, ConnectionListResponse
)
from ..auth import get_current_active_user

router = APIRouter(prefix="/connections", tags=["connections"])


@router.post("/", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection_request(
    connection_data: ConnectionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Send a connection request to another user.
    
    Args:
        connection_data: Connection request data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ConnectionResponse: Created connection request
        
    Raises:
        HTTPException: If connection already exists or invalid user
    """
    # Check if trying to connect with self
    if connection_data.receiver_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot connect with yourself"
        )
    
    # Check if receiver user exists
    receiver = db.query(User).filter(
        User.id == connection_data.receiver_id,
        User.is_active == True
    ).first()
    
    if not receiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if connection already exists
    existing_connection = db.query(Connection).filter(
        or_(
            and_(
                Connection.sender_id == current_user.id,
                Connection.receiver_id == connection_data.receiver_id
            ),
            and_(
                Connection.sender_id == connection_data.receiver_id,
                Connection.receiver_id == current_user.id
            )
        )
    ).first()
    
    if existing_connection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection already exists"
        )
    
    # Create connection request
    db_connection = Connection(
        sender_id=current_user.id,
        receiver_id=connection_data.receiver_id,
        status="pending"
    )
    
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    
    # Return connection with user details
    return ConnectionResponse(
        id=db_connection.id,
        sender_id=db_connection.sender_id,
        receiver_id=db_connection.receiver_id,
        status=db_connection.status,
        created_at=db_connection.created_at,
        updated_at=db_connection.updated_at,
        sender=current_user,
        receiver=receiver
    )


@router.put("/{connection_id}/accept", response_model=ConnectionResponse)
async def accept_connection(
    connection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Accept a connection request.
    
    Args:
        connection_id: ID of the connection to accept
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ConnectionResponse: Updated connection
        
    Raises:
        HTTPException: If connection not found or unauthorized
    """
    # Get connection and verify it's for the current user
    connection = db.query(Connection).filter(
        Connection.id == connection_id,
        Connection.receiver_id == current_user.id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection request not found"
        )
    
    if connection.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection request already processed"
        )
    
    # Accept the connection
    connection.status = "accepted"
    db.commit()
    db.refresh(connection)
    
    # Get sender user details
    sender = db.query(User).filter(User.id == connection.sender_id).first()
    
    return ConnectionResponse(
        id=connection.id,
        sender_id=connection.sender_id,
        receiver_id=connection.receiver_id,
        status=connection.status,
        created_at=connection.created_at,
        updated_at=connection.updated_at,
        sender=sender,
        receiver=current_user
    )


@router.put("/{connection_id}/reject", response_model=ConnectionResponse)
async def reject_connection(
    connection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Reject a connection request.
    
    Args:
        connection_id: ID of the connection to reject
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ConnectionResponse: Updated connection
        
    Raises:
        HTTPException: If connection not found or unauthorized
    """
    # Get connection and verify it's for the current user
    connection = db.query(Connection).filter(
        Connection.id == connection_id,
        Connection.receiver_id == current_user.id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection request not found"
        )
    
    if connection.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection request already processed"
        )
    
    # Reject the connection
    connection.status = "rejected"
    db.commit()
    db.refresh(connection)
    
    # Get sender user details
    sender = db.query(User).filter(User.id == connection.sender_id).first()
    
    return ConnectionResponse(
        id=connection.id,
        sender_id=connection.sender_id,
        receiver_id=connection.receiver_id,
        status=connection.status,
        created_at=connection.created_at,
        updated_at=connection.updated_at,
        sender=sender,
        receiver=current_user
    )


@router.get("/", response_model=ConnectionListResponse)
async def list_connections(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all connections for the current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ConnectionListResponse: List of sent and received connections
    """
    # Get sent connections
    sent_connections = (
        db.query(Connection, User)
        .join(User, Connection.receiver_id == User.id)
        .filter(
            Connection.sender_id == current_user.id
        )
        .all()
    )
    
    # Get received connections
    received_connections = (
        db.query(Connection, User)
        .join(User, Connection.sender_id == User.id)
        .filter(
            Connection.receiver_id == current_user.id
        )
        .all()
    )
    
    # Convert to response format
    sent_responses = []
    for conn, receiver in sent_connections:
        sent_responses.append(ConnectionResponse(
            id=conn.id,
            sender_id=conn.sender_id,
            receiver_id=conn.receiver_id,
            status=conn.status,
            created_at=conn.created_at,
            updated_at=conn.updated_at,
            sender=current_user,
            receiver=receiver
        ))
    
    received_responses = []
    for conn, sender in received_connections:
        received_responses.append(ConnectionResponse(
            id=conn.id,
            sender_id=conn.sender_id,
            receiver_id=conn.receiver_id,
            status=conn.status,
            created_at=conn.created_at,
            updated_at=conn.updated_at,
            sender=sender,
            receiver=current_user
        ))
    
    return ConnectionListResponse(
        sent_connections=sent_responses,
        received_connections=received_responses,
        total_sent=len(sent_responses),
        total_received=len(received_responses)
    )


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific connection by ID.
    
    Args:
        connection_id: ID of the connection to retrieve
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ConnectionResponse: Connection details
        
    Raises:
        HTTPException: If connection not found or unauthorized
    """
    connection = db.query(Connection).filter(
        Connection.id == connection_id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    # Verify user is part of this connection
    if connection.sender_id != current_user.id and connection.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this connection"
        )
    
    # Get user details
    sender = db.query(User).filter(User.id == connection.sender_id).first()
    receiver = db.query(User).filter(User.id == connection.receiver_id).first()
    
    return ConnectionResponse(
        id=connection.id,
        sender_id=connection.sender_id,
        receiver_id=connection.receiver_id,
        status=connection.status,
        created_at=connection.created_at,
        updated_at=connection.updated_at,
        sender=sender,
        receiver=receiver
    )


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    connection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a connection (cancel request or remove connection).
    
    Args:
        connection_id: ID of the connection to delete
        current_user: Current authenticated user
        db: Database session
        
    Raises:
        HTTPException: If connection not found or unauthorized
    """
    connection = db.query(Connection).filter(
        Connection.id == connection_id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    # Verify user is part of this connection
    if connection.sender_id != current_user.id and connection.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this connection"
        )
    
    # Delete the connection
    db.delete(connection)
    db.commit()
