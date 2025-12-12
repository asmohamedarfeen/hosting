"""
User Synchronization Service
Bridges the main database and messaging database to share user data and authentication.
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime
import hashlib
import os
from werkzeug.security import check_password_hash
from passlib.context import CryptContext

# Import main database models
from models import User as MainUser
from database import get_db as get_main_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing contexts
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserSyncService:
    """Service to synchronize users between main database and messaging database"""
    
    def __init__(self):
        # Main database configuration (already exists)
        self.main_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.db")
        self.main_db_url = f"sqlite:///{self.main_db_path}"
        
        # Messaging database configuration
        self.message_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "message", "message", "message", "app.db")
        self.message_db_url = f"sqlite:///{self.message_db_path}"
        
        # Create engines
        self.main_engine = create_engine(
            self.main_db_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        
        self.message_engine = create_engine(
            self.message_db_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
        
        # Session factories
        self.MainSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.main_engine)
        self.MessageSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.message_engine)
    
    def get_main_user(self, user_id: int) -> Optional[MainUser]:
        """Get user from main database"""
        try:
            with self.MainSessionLocal() as session:
                return session.query(MainUser).filter(MainUser.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting main user {user_id}: {e}")
            return None
    
    def get_main_user_by_email(self, email: str) -> Optional[MainUser]:
        """Get user from main database by email"""
        try:
            with self.MainSessionLocal() as session:
                return session.query(MainUser).filter(MainUser.email == email).first()
        except Exception as e:
            logger.error(f"Error getting main user by email {email}: {e}")
            return None
    
    def convert_password_hash(self, werkzeug_hash: str) -> str:
        """Convert werkzeug password hash to bcrypt hash"""
        try:
            # For now, we'll create a new bcrypt hash
            # In a real scenario, you'd need to verify the original password
            # and create a new hash, but since we don't have the plain password,
            # we'll use a default approach
            return pwd_context.hash("default_password")
        except Exception as e:
            logger.error(f"Error converting password hash: {e}")
            return pwd_context.hash("default_password")
    
    def sync_user_to_messaging(self, main_user: MainUser) -> Optional[Dict[str, Any]]:
        """Sync user from main database to messaging database"""
        try:
            with self.MessageSessionLocal() as session:
                # Check if user already exists in messaging database
                existing_user = session.execute(
                    text("SELECT id FROM users WHERE email = :email"),
                    {"email": main_user.email}
                ).fetchone()
                
                if existing_user:
                    # Update existing user
                    session.execute(
                        text("""
                            UPDATE users 
                            SET name = :name, password_hash = :password_hash, bio = :bio, 
                                is_active = :is_active
                            WHERE email = :email
                        """),
                        {
                            "name": main_user.full_name or main_user.username,
                            "password_hash": main_user.password_hash or "",
                            "bio": main_user.bio or "",
                            "is_active": main_user.is_active,
                            "email": main_user.email
                        }
                    )
                    user_id = existing_user[0]
                else:
                    # Create new user
                    result = session.execute(
                        text("""
                            INSERT INTO users (name, email, password_hash, bio, is_active, created_at)
                            VALUES (:name, :email, :password_hash, :bio, :is_active, :created_at)
                        """),
                        {
                            "name": main_user.full_name or main_user.username,
                            "email": main_user.email,
                            "password_hash": main_user.password_hash or "",
                            "bio": main_user.bio or "",
                            "is_active": main_user.is_active,
                            "created_at": datetime.now()
                        }
                    )
                    user_id = result.lastrowid
                
                session.commit()
                
                # Return user data
                return {
                    "id": user_id,
                    "name": main_user.full_name or main_user.username,
                    "email": main_user.email,
                    "bio": main_user.bio or "",
                    "is_active": main_user.is_active
                }
                
        except Exception as e:
            logger.error(f"Error syncing user to messaging database: {e}")
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user using main database credentials"""
        try:
            # Get user from main database
            main_user = self.get_main_user_by_email(email)
            if not main_user:
                return None
            
            # Check password (assuming password is already hashed in main database)
            if main_user.password_hash and main_user.password_hash == password:
                # Sync user to messaging database
                messaging_user = self.sync_user_to_messaging(main_user)
                if messaging_user:
                    return {
                        "main_user_id": main_user.id,
                        "messaging_user_id": messaging_user["id"],
                        "name": main_user.full_name or main_user.username,
                        "email": main_user.email,
                        "bio": main_user.bio or "",
                        "is_active": main_user.is_active,
                        "profile_image": main_user.get_profile_pic_url(),
                        "company": main_user.company,
                        "title": main_user.title,
                        "location": main_user.location
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int, from_main: bool = True) -> Optional[Dict[str, Any]]:
        """Get user data from either database"""
        try:
            if from_main:
                # Get from main database
                main_user = self.get_main_user(user_id)
                if main_user:
                    return {
                        "id": main_user.id,
                        "name": main_user.full_name or main_user.username,
                        "email": main_user.email,
                        "bio": main_user.bio or "",
                        "is_active": main_user.is_active,
                        "profile_image": main_user.get_profile_pic_url(),
                        "company": main_user.company,
                        "title": main_user.title,
                        "location": main_user.location
                    }
            else:
                # Get from messaging database
                with self.MessageSessionLocal() as session:
                    result = session.execute(
                        text("SELECT id, name, email, bio, is_active, created_at FROM users WHERE id = :user_id"),
                        {"user_id": user_id}
                    ).fetchone()
                    
                    if result:
                        return {
                            "id": result[0],
                            "name": result[1],
                            "email": result[2],
                            "bio": result[3] or "",
                            "is_active": result[4],
                            "created_at": result[5].isoformat() if result[5] else None
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def sync_all_users(self) -> Dict[str, int]:
        """Sync all users from main database to messaging database"""
        try:
            with self.MainSessionLocal() as main_session:
                users = main_session.query(MainUser).all()
                
                synced_count = 0
                error_count = 0
                
                for user in users:
                    if self.sync_user_to_messaging(user):
                        synced_count += 1
                    else:
                        error_count += 1
                
                return {
                    "total_users": len(users),
                    "synced": synced_count,
                    "errors": error_count
                }
                
        except Exception as e:
            logger.error(f"Error syncing all users: {e}")
            return {"total_users": 0, "synced": 0, "errors": 1}
    
    def create_messaging_tables(self):
        """Create messaging database tables if they don't exist"""
        try:
            with self.message_engine.connect() as conn:
                # Create users table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        bio TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """))
                
                # Create connections table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS connections (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (sender_id) REFERENCES users(id),
                        FOREIGN KEY (receiver_id) REFERENCES users(id)
                    )
                """))
                
                # Create messages table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        is_read BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (sender_id) REFERENCES users(id),
                        FOREIGN KEY (receiver_id) REFERENCES users(id)
                    )
                """))
                
                conn.commit()
                logger.info("Messaging database tables created successfully")
                
        except Exception as e:
            logger.error(f"Error creating messaging tables: {e}")
            raise

# Global instance
user_sync_service = UserSyncService()
