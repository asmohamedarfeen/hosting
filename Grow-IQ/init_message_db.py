#!/usr/bin/env python3
"""
Initialize messaging database and sync users from main database.
This script sets up the messaging system to work with the main application.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from user_sync_service import user_sync_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize messaging database and sync users"""
    try:
        logger.info("🚀 Initializing messaging database...")
        
        # Create messaging database tables
        logger.info("📋 Creating messaging database tables...")
        user_sync_service.create_messaging_tables()
        logger.info("✅ Messaging database tables created successfully")
        
        # Sync all users from main database
        logger.info("👥 Syncing users from main database...")
        sync_result = user_sync_service.sync_all_users()
        
        logger.info(f"📊 Sync Results:")
        logger.info(f"   Total users: {sync_result['total_users']}")
        logger.info(f"   Synced: {sync_result['synced']}")
        logger.info(f"   Errors: {sync_result['errors']}")
        
        if sync_result['errors'] == 0:
            logger.info("✅ All users synced successfully!")
        else:
            logger.warning(f"⚠️  {sync_result['errors']} users failed to sync")
        
        logger.info("🎉 Messaging database initialization completed!")
        
    except Exception as e:
        logger.error(f"❌ Error initializing messaging database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
