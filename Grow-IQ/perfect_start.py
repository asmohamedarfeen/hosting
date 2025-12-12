#!/usr/bin/env python3
"""
Perfect Error-Free Startup Script
"""

import uvicorn
import sys
import os

def main():
    try:
        print("🚀 Starting CareerConnect...")
        print("📱 http://localhost:8000")
        print("🔧 Press Ctrl+C to stop")
        print("-" * 40)
        
        # Start with perfect configuration
        uvicorn.run(
            "app:app",
            host="localhost",
            port=8000,
            reload=False,  # Disable reload to avoid any issues
            log_level="warning",  # Minimal output
            access_log=False,  # No access logs
            use_colors=False  # Clean output
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
