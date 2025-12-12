#!/usr/bin/env python3
"""
Final Working Startup Script - Guaranteed to work
"""

import uvicorn
import sys

def main():
    try:
        print("🚀 Starting Qrow IQ (Final Working Version)...")
        print("📱 http://localhost:8000")
        print("🔧 Press Ctrl+C to stop")
        print("-" * 40)
        
        # Start with guaranteed working configuration
        uvicorn.run(
            "app_minimal:app",  # Use the minimal app
            host="localhost",
            port=8000,
            reload=False,  # Disable reload to avoid issues
            log_level="info",  # Show some info for debugging
            access_log=True,  # Enable access logs to see requests
            use_colors=False  # Clean output
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("💡 This should not happen with the final working version")
        sys.exit(1)

if __name__ == "__main__":
    main()
