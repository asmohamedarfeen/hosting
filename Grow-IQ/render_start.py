#!/usr/bin/env python3
"""
Render Production Startup Script
Optimized for Render.com deployment
"""

import os
import uvicorn
from app import app
from config import settings
from database_enhanced import init_database, test_db_connection

def main():
    """Start the application for production on Render"""
    
    print("🚀 Starting Grow-IQ on Render...")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    
    # Ensure database is initialized
    print("📊 Checking database connection...")
    if test_db_connection():
        print("✅ Database connection successful")
        if init_database():
            print("✅ Database tables initialized")
        else:
            print("⚠️  Database tables may already exist")
    else:
        print("❌ Database connection failed!")
        print("   Please check your DATABASE_URL environment variable")
        raise RuntimeError("Cannot connect to database")
    
    # Get port from environment (Render sets this automatically)
    # Handle case where PORT might be set to literal '$PORT' string
    port_str = os.getenv("PORT", "8000")
    if port_str == "$PORT" or not port_str:
        port = 8000
    else:
        try:
            port = int(port_str)
        except (ValueError, TypeError):
            port = 8000
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🌐 Starting server on {host}:{port}")
    print(f"📚 API docs: http://{host}:{port}/docs")
    print(f"🏥 Health check: http://{host}:{port}/health")
    print("-" * 50)
    
    # Start uvicorn server
    # Note: Render expects the app to bind to $PORT
    # Note: uvicorn doesn't support workers parameter - use gunicorn for multiple workers
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        # Don't use reload in production
        reload=False
    )

if __name__ == "__main__":
    main()

