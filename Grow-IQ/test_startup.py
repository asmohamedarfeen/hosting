#!/usr/bin/env python3
"""
Qrow IQ Startup Test
This script tests if the application can start successfully
"""

import sys
import time

def test_startup():
    """Test if the application can start successfully"""
    print("🚀 Testing Qrow IQ Startup...")
    
    try:
        # Test configuration
        print("   🔧 Testing configuration...")
        from config import settings
        print(f"      ✅ Environment: {settings.ENVIRONMENT}")
        print(f"      ✅ Debug: {settings.DEBUG}")
        
        # Test database
        print("   🗄️  Testing database...")
        from database_enhanced import db_manager
        print(f"      ✅ Database manager: {type(db_manager)}")
        
        # Test logging
        print("   📝 Testing logging...")
        from logging_config import app_logger
        print(f"      ✅ Logger: {type(app_logger)}")
        
        # Test security
        print("   🔒 Testing security...")
        from security import SecurityMiddleware
        print(f"      ✅ Security middleware: {type(SecurityMiddleware)}")
        
        # Test main app
        print("   🚀 Testing main application...")
        import app
        print(f"      ✅ App title: {app.app.title}")
        print(f"      ✅ App version: {app.app.version}")
        
        # Test start script
        print("   ▶️  Testing start script...")
        import start
        print("      ✅ Start script imported")
        
        print("\n🎉 All startup tests passed!")
        print("✅ Qrow IQ is ready to run!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_startup()
    sys.exit(0 if success else 1)
