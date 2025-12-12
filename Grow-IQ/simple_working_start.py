#!/usr/bin/env python3
"""
Simple Working Startup Script
"""

import uvicorn
from app import app

if __name__ == "__main__":
    print("🚀 Starting Qrow IQ FastAPI application...")
    print("📱 Dashboard will be available at: http://127.0.0.1:8000")
    print("📚 API documentation at: http://127.0.0.1:8000/docs")
    print("🏥 Health check at: http://127.0.0.1:8000/health")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="warning"  # Set to warning to minimize output
    )
