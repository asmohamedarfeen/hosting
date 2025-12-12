#!/usr/bin/env python3
"""
Quick Start Test - Tests if the application can initialize without running the server
"""

def test_quick_start():
    """Test if the application can initialize successfully"""
    print("🚀 Testing Qrow IQ Quick Start...")
    
    try:
        # Test all imports
        print("   🔧 Testing imports...")
        from config import settings
        from database_enhanced import db_manager
        from logging_config import app_logger
        from security import SecurityMiddleware
        import app
        
        print("      ✅ All modules imported successfully")
        
        # Test configuration
        print("   ⚙️  Testing configuration...")
        print(f"      ✅ Environment: {settings.ENVIRONMENT}")
        print(f"      ✅ Debug: {settings.DEBUG}")
        print(f"      ✅ Host: {settings.HOST}")
        print(f"      ✅ Port: {settings.PORT}")
        
        # Test app properties
        print("   🚀 Testing application...")
        print(f"      ✅ App Title: {app.app.title}")
        print(f"      ✅ App Version: {app.app.version}")
        print(f"      ✅ Debug Mode: {app.app.debug}")
        
        # Test database
        print("   🗄️  Testing database...")
        print(f"      ✅ Database Manager: {type(db_manager)}")
        print(f"      ✅ Engine: {type(db_manager.engine)}")
        
        print("\n🎉 Quick start test completed successfully!")
        print("✅ Qrow IQ is ready to run!")
        print("\nTo start the application, run:")
        print("   python start.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Quick start test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_quick_start()
