#!/usr/bin/env python3
"""
Simple Startup Script - Debug version
"""

import uvicorn
import time
from app import app
from config import settings

def main():
    print("🚀 Starting Qrow IQ FastAPI application...")
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
        uvicorn.run(
            "app:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,  # Auto-reload only in development
            log_level=settings.LOG_LEVEL.lower(),
            workers=settings.WORKERS if not settings.DEBUG else 1
        )
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
