#!/usr/bin/env python3
"""
Final Working Startup Script
"""

import uvicorn
import time
from app import app
from config import settings

def main():
    print("🚀 Starting CareerConnect FastAPI application...")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    print(f"📱 Dashboard will be available at: http://127.0.0.1:8000")
    print(f"📚 API documentation at: http://127.0.0.1:8000/docs")
    print(f"🏥 Health check at: http://127.0.0.1:8000/health")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Set app start time for uptime tracking
        app.start_time = time.time()
        print("✅ Start time set successfully")
        
        print("🚀 Starting Uvicorn server...")
        
        # Use localhost instead of 0.0.0.0 for better compatibility
        uvicorn.run(
            app,
            host="127.0.0.1",  # Use localhost
            port=8000,
            reload=True,  # Always enable reload for development
            log_level="warning"  # Set to warning to minimize output
        )
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
