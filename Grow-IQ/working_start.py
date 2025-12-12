#!/usr/bin/env python3
"""
Working Startup Script - Fixed version
"""

import uvicorn
import time
from app import app
from config import settings

def main():
    print("🚀 Starting CareerConnect FastAPI application...")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    print(f"📱 Dashboard will be available at: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API documentation at: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🏥 Health check at: http://{settings.HOST}:{settings.PORT}/health")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Set app start time for uptime tracking
        app.start_time = time.time()
        print("✅ Start time set successfully")
        
        print("🚀 Starting Uvicorn server...")
        
        # Use simpler uvicorn configuration
        uvicorn.run(
            app,  # Pass the app directly instead of string
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower()
        )
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
