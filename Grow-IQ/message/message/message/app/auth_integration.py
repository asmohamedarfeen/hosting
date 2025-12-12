"""
Authentication Integration Service
Integrates messaging system with main database authentication.
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Add the main project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from user_sync_service import user_sync_service
    from models import User as MainUser
    from database import get_db as get_main_db
    from auth_utils import verify_password, create_session_token
except ImportError as e:
    logging.error(f"Failed to import main app modules: {e}")
    user_sync_service = None

logger = logging.getLogger(__name__)

class AuthIntegrationService:
    """Service to integrate messaging authentication with main database"""
    
    def __init__(self):
        self.user_sync_service = user_sync_service
    
    def authenticate_user_with_main_db(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user using main database credentials"""
        if not self.user_sync_service:
            logger.error("User sync service not available")
            return None
        
        try:
            # Use the sync service to authenticate
            auth_result = self.user_sync_service.authenticate_user(email, password)
            if auth_result:
                return auth_result
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user with main DB: {e}")
            return None
    
    def get_user_from_main_db(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from main database"""
        if not self.user_sync_service:
            return None
        
        try:
            return self.user_sync_service.get_user_by_id(user_id, from_main=True)
        except Exception as e:
            logger.error(f"Error getting user from main DB: {e}")
            return None
    
    def sync_user_to_messaging(self, main_user_id: int) -> Optional[Dict[str, Any]]:
        """Sync user from main database to messaging database"""
        if not self.user_sync_service:
            return None
        
        try:
            main_user = self.user_sync_service.get_main_user(main_user_id)
            if main_user:
                return self.user_sync_service.sync_user_to_messaging(main_user)
            return None
        except Exception as e:
            logger.error(f"Error syncing user to messaging: {e}")
            return None
    
    def create_messaging_token(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Create a JWT token for messaging system"""
        try:
            # Import JWT functions from messaging auth
            from .auth import create_user_token
            
            # Create a mock user object for token creation
            class MockUser:
                def __init__(self, user_data):
                    self.id = user_data.get('messaging_user_id', user_data.get('id'))
                    self.name = user_data.get('name', '')
                    self.email = user_data.get('email', '')
                    self.is_active = user_data.get('is_active', True)
            
            mock_user = MockUser(user_data)
            return create_user_token(mock_user)
            
        except Exception as e:
            logger.error(f"Error creating messaging token: {e}")
            return {"access_token": "", "token_type": "bearer"}

# Global instance
auth_integration_service = AuthIntegrationService()
