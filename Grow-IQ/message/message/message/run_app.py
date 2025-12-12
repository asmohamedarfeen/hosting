#!/usr/bin/env python3
"""
Launcher script for the LinkedIn-like Connection + Messaging App
Run this file directly to start the application.
"""

import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting LinkedIn-like Connection + Messaging App...")
    print("📱 Access the application at: http://localhost:9000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=9000,
        reload=True,
        log_level="info"
    )
