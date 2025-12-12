#!/usr/bin/env python3
"""
Minimal Startup Script - Uses the working minimal app
"""

import uvicorn
import sys

def main():
    try:
        print("🚀 Starting CareerConnect (Minimal Mode)...")
        print("📱 http://localhost:8000")
        print("🔧 Press Ctrl+C to stop")
        print("-" * 40)
        
        # Start with the minimal app
        uvicorn.run(
            "app_minimal:app",  # Use the minimal app
            host="localhost",
            port=8000,
            reload=False,  # Disable reload to avoid issues
            log_level="warning",  # Minimal output
            access_log=False,  # No access logs
            use_colors=False  # Clean output
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("💡 This should not happen with the minimal version")
        sys.exit(1)

if __name__ == "__main__":
    main()
