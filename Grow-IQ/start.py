import uvicorn
import os
import time
from app import app
from config import settings

if __name__ == "__main__":
    print("🚀 Starting Qrow IQ FastAPI application...")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    print(f"📱 Dashboard will be available at: http://localhost:{settings.PORT}")
    print(f"📚 API documentation at: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🏥 Health check at: http://{settings.HOST}:{settings.PORT}/health")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Set app start time for uptime tracking
    app.start_time = time.time()
    
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=int(settings.PORT),
        reload=settings.DEBUG,  # Auto-reload only in development
        log_level="info",  # Set to info to reduce debug output
        workers=settings.WORKERS if not settings.DEBUG else 1 
    )   