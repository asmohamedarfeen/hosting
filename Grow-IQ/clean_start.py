#!/usr/bin/env python3
"""
Clean Startup Script - Minimal output version
"""

import uvicorn
from app import app

if __name__ == "__main__":
    print("🚀 Starting CareerConnect...")
    print("📱 http://127.0.0.1:8000")
    print("🔧 Press Ctrl+C to stop")
    print("-" * 40)
    
    # Start with minimal logging
    uvicorn.run(
        "app:app",  # Use string for reload to work
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="warning",  # Minimal output
        access_log=False,      # Disable access logs
        use_colors=False       # Disable colors for cleaner output
    )
