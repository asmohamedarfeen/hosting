import logging
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from database_enhanced import get_db, db_manager
from auth_utils import get_user_from_session
from models import User, Connection
from models import Message
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Message API Adapter"]) 
router_compat = APIRouter(prefix="/api", tags=["Message API Compat"]) 


def serialize_user(u: User) -> Dict[str, Any]:
    if not u:
        return {}
    return {
        "id": u.id,
        "name": u.full_name or u.username or "User",
        "email": u.email,
        "bio": getattr(u, "bio", None),
    }


def serialize_connection(conn: Connection, sender: Optional[User], receiver: Optional[User]) -> Dict[str, Any]:
    return {
        "id": conn.id,
        "sender_id": conn.user_id,
        "receiver_id": conn.connected_user_id,
        "status": conn.status,
        "sender": serialize_user(sender) if sender else None,
        "receiver": serialize_user(receiver) if receiver else None,
    }
# Ensure messages table has required columns for adapter
def _ensure_messages_table_schema():
    try:
        engine = db_manager.engine
        with engine.begin() as conn:
            dialect = engine.dialect.name
            # Only needed for SQLite; other DBs should use migrations
            if "sqlite" in engine.url.drivername:
                cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(messages)").fetchall()]
                if "timestamp" not in cols:
                    conn.exec_driver_sql("ALTER TABLE messages ADD COLUMN timestamp DATETIME DEFAULT (CURRENT_TIMESTAMP)")
                if "is_read" not in cols:
                    conn.exec_driver_sql("ALTER TABLE messages ADD COLUMN is_read BOOLEAN DEFAULT 0")
    except Exception as e:
        logger.warning(f"Could not verify/patch messages table schema: {e}")

_ensure_messages_table_schema()



# Optional current user resolver (no login required for adapter endpoints)
def _resolve_optional_user(request: Request, db: Session) -> User:
    try:
        token = request.cookies.get("session_token")
        if token:
            session_data = get_user_from_session(token)
            if session_data:
                user = db.query(User).filter(User.id == session_data['user_id']).first()
                if user:
                    return user
    except Exception:
        pass
    user = db.query(User).filter(User.is_active == True).first()
    if user:
        return user
    # Create demo user if none exists
    demo = User(
        username="demo_user",
        email="demo@example.com",
        full_name="Demo User",
        password_hash=generate_password_hash("demo12345"),
        is_active=True,
        is_verified=True,
    )
    db.add(demo)
    db.commit()
    db.refresh(demo)
    return demo


@router.get("/users/me")
async def get_me(request: Request, db: Session = Depends(get_db)):
    user = _resolve_optional_user(request, db)
    return serialize_user(user)


@router.get("/users")
async def list_users(
    request: Request,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    current_user = _resolve_optional_user(request, db)
    users = (
        db.query(User)
        .filter(User.is_active == True, User.id != current_user.id)
        .order_by(User.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {"users": [serialize_user(u) for u in users]}


@router.post("/users/register")
async def register_user(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """Register a new user for the adapter UI."""
    username = (payload.get("username") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    full_name = (payload.get("full_name") or payload.get("name") or username).strip()

    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="username, email and password are required")

    existing = db.query(User).filter(or_(User.username == username, User.email == email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")

    hashed = generate_password_hash(password)
    user = User(
        username=username,
        email=email,
        full_name=full_name or username,
        password_hash=hashed,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"user": serialize_user(user), "message": "Registered successfully"}


@router.get("/connections")
async def get_connections(
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        current_user = _resolve_optional_user(request, db)
        # Gather connections in both directions for this user
        conns = db.query(Connection).filter(
            or_(Connection.user_id == current_user.id, Connection.connected_user_id == current_user.id)
        ).all()

        all_connections: List[Dict[str, Any]] = []
        received_connections: List[Dict[str, Any]] = []
        sent_connections: List[Dict[str, Any]] = []
        stats = {"total": 0, "pending": 0, "accepted": 0}

        for c in conns:
            sender = db.query(User).filter(User.id == c.user_id).first()
            receiver = db.query(User).filter(User.id == c.connected_user_id).first()
            item = serialize_connection(c, sender=sender, receiver=receiver)
            all_connections.append(item)

            if c.connected_user_id == current_user.id:
                received_connections.append(item)
            if c.user_id == current_user.id:
                sent_connections.append(item)

            stats["total"] += 1
            stats[c.status] = stats.get(c.status, 0) + 1

        # Return a structure compatible with the uploaded dashboard UI while preserving previous fields
        return {
            "connections": all_connections,
            "received_connections": received_connections,
            "sent_connections": sent_connections,
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"/api/v1/connections failed: {e}")
        # Fail open with empty data so the UI can still render
        return {
            "connections": [],
            "received_connections": [],
            "sent_connections": [],
            "stats": {"total": 0, "pending": 0, "accepted": 0},
        }


# Compat endpoints expected by some UIs
@router_compat.get("/connections/current")
async def compat_connections_current(
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = _resolve_optional_user(request, db)
    # accepted connections in either direction
    accepted = db.query(Connection).filter(
        or_(
            and_(Connection.user_id == current_user.id, Connection.status == 'accepted'),
            and_(Connection.connected_user_id == current_user.id, Connection.status == 'accepted'),
        )
    ).all()
    result = []
    for c in accepted:
        other_id = c.connected_user_id if c.user_id == current_user.id else c.user_id
        other = db.query(User).filter(User.id == other_id).first()
        result.append(serialize_connection(c, sender=current_user if c.user_id == current_user.id else other, receiver=other if c.user_id == current_user.id else current_user))
    return {"connections": result}


@router_compat.get("/connections/sent")
async def compat_connections_sent(
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = _resolve_optional_user(request, db)
    sent = db.query(Connection).filter(Connection.user_id == current_user.id).all()
    result = []
    for c in sent:
        other = db.query(User).filter(User.id == c.connected_user_id).first()
        result.append(serialize_connection(c, sender=current_user, receiver=other))
    return {"connections": result}


@router.post("/connections")
async def create_connection(
    request: Request,
    db: Session = Depends(get_db),
    payload: Optional[Dict[str, Any]] = None,
):
    """Create a connection request.
    Accepts JSON or form data. You can pass receiver by id (receiver_id)
    or by identifier (username/email) in the field 'receiver'.
    """
    current_user = _resolve_optional_user(request, db)

    # Accept JSON or form-encoded submissions
    if payload is None or not isinstance(payload, dict) or not payload:
        try:
            form = await request.form()
            payload = {k: v for k, v in form.items()}
        except Exception:
            payload = {}

    receiver_id = payload.get("receiver_id")
    if not receiver_id and payload.get("receiver"):
        ident = str(payload.get("receiver")).strip().lower()
        # Try resolve by username or email
        user = db.query(User).filter(or_(User.username == ident, User.email == ident)).first()
        receiver_id = user.id if user else None

    try:
        receiver_id = int(receiver_id) if receiver_id is not None else None
    except Exception:
        receiver_id = None

    if not receiver_id:
        raise HTTPException(status_code=400, detail="receiver_id (or receiver) is required")
    if receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot connect to yourself")

    receiver = db.query(User).filter(User.id == receiver_id, User.is_active == True).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")

    # Check existing connection both directions
    existing = db.query(Connection).filter(
        or_(
            and_(Connection.user_id == current_user.id, Connection.connected_user_id == receiver_id),
            and_(Connection.user_id == receiver_id, Connection.connected_user_id == current_user.id),
        )
    ).first()
    if existing:
        # If a reverse pending exists where current_user is receiver, just accept it
        if existing.status == "pending" and existing.connected_user_id == current_user.id:
            existing.status = "accepted"
            db.commit()
            sender = db.query(User).filter(User.id == existing.user_id).first()
            return JSONResponse(content=serialize_connection(existing, sender=sender, receiver=current_user), status_code=200)
        raise HTTPException(status_code=400, detail="Connection already exists")

    conn = Connection(
        user_id=current_user.id,
        connected_user_id=receiver_id,
        status="pending",
        connection_type="professional",
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return JSONResponse(content=serialize_connection(conn, sender=current_user, receiver=receiver), status_code=201)


@router.put("/connections/{connection_id}/accept")
async def accept_connection(
    connection_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = _resolve_optional_user(request, db)
    conn = db.query(Connection).filter(Connection.id == connection_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    if conn.connected_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to accept this request")
    conn.status = "accepted"
    db.commit()
    sender = db.query(User).filter(User.id == conn.user_id).first()
    return serialize_connection(conn, sender=sender, receiver=current_user)


@router.put("/connections/{connection_id}/reject")
async def reject_connection(
    connection_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = _resolve_optional_user(request, db)
    conn = db.query(Connection).filter(Connection.id == connection_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    if conn.connected_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reject this request")
    conn.status = "declined"
    db.commit()
    sender = db.query(User).filter(User.id == conn.user_id).first()
    return serialize_connection(conn, sender=sender, receiver=current_user)


@router.get("/messages/chat/{other_user_id}")
async def get_chat_messages(
    request: Request,
    other_user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    current_user = _resolve_optional_user(request, db)
    # must be connected (accepted) in either direction
    connection = db.query(Connection).filter(
        or_(
            and_(Connection.user_id == current_user.id, Connection.connected_user_id == other_user_id),
            and_(Connection.user_id == other_user_id, Connection.connected_user_id == current_user.id),
        ),
        Connection.status == "accepted",
    ).first()
    if not connection:
        raise HTTPException(status_code=403, detail="Can only view chat history with connections")

    messages = (
        db.query(Message)
        .filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id),
            )
        )
        .order_by(Message.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    other = db.query(User).filter(User.id == other_user_id).first()
    result = []
    for m in messages:
        result.append(
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "receiver_id": m.receiver_id,
                "content": m.content,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None,
                "is_read": m.is_read,
                "sender": serialize_user(current_user if m.sender_id == current_user.id else other),
            }
        )
    return {"messages": list(reversed(result))}


@router.post("/messages")
async def send_message(
    payload: Dict[str, Any],
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = _resolve_optional_user(request, db)
    receiver_id = payload.get("receiver_id")
    content = (payload.get("content") or "").strip()
    if not receiver_id or not content:
        raise HTTPException(status_code=400, detail="receiver_id and content are required")

    # verify connection exists and accepted
    connection = db.query(Connection).filter(
        or_(
            and_(Connection.user_id == current_user.id, Connection.connected_user_id == receiver_id),
            and_(Connection.user_id == receiver_id, Connection.connected_user_id == current_user.id),
        ),
        Connection.status == "accepted",
    ).first()
    if not connection:
        raise HTTPException(status_code=403, detail="Can only message your connections")

    msg = Message(sender_id=current_user.id, receiver_id=receiver_id, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "receiver_id": msg.receiver_id,
        "content": msg.content,
        "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
        "is_read": msg.is_read,
    }


@router.post("/auth/login")
async def adapter_login(
    payload: Dict[str, Any],
    response: Response,
    db: Session = Depends(get_db),
):
    """JSON login for the uploaded message UI; sets session cookie and returns a token."""
    identifier = (payload.get("identifier") or payload.get("email") or payload.get("username") or "").strip().lower()
    password = payload.get("password") or ""
    if not identifier or not password:
        raise HTTPException(status_code=400, detail="identifier/email and password are required")

    user = db.query(User).filter(or_(User.email == identifier, User.username == identifier)).first()
    if not user or not check_password_hash(user.password_hash, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is deactivated")

    # Create session cookie using existing helper
    from auth_utils import create_session_token
    token = create_session_token(user.id)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
        max_age=86400,
    )
    # Return token for UI's localStorage
    return {"token": token, "user": serialize_user(user)}


