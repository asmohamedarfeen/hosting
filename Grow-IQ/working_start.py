#!/usr/bin/env python3
"""
Working Startup Script - Fixed version
"""

import os
import uvicorn
import time
from app import app
from config import settings

def main():
    print("🚀 Starting CareerConnect FastAPI application...")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    
    # Get port from environment (Render sets $PORT automatically)
    # Fallback to settings.PORT for local development
    port = int(os.getenv("PORT", settings.PORT))
    host = os.getenv("HOST", settings.HOST)
    
    print(f"📱 Dashboard will be available at: http://{host}:{port}")
    print(f"📚 API documentation at: http://{host}:{port}/docs")
    print(f"🏥 Health check at: http://{host}:{port}/health")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Set app start time for uptime tracking
        app.start_time = time.time()
        print("✅ Start time set successfully")
        
        print("🚀 Starting Uvicorn server...")
        
        # Use simpler uvicorn configuration
        # Note: Don't use reload in production (Render sets DEBUG=false)
        uvicorn.run(
            app,  # Pass the app directly instead of string
            host=host,
            port=port,
            reload=settings.DEBUG,  # Only reload in development
            log_level=settings.LOG_LEVEL.lower()
        )
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
