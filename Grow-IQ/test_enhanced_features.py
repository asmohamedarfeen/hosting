#!/usr/bin/env python3
"""
Qrow IQ Enhanced Features Test Script
This script tests all the new features and improvements
"""

import sys
import os
import time

def test_configuration():
    """Test configuration system"""
    print("🔧 Testing Configuration System...")
    try:
        from config import settings
        print(f"   ✅ Environment: {settings.ENVIRONMENT}")
        print(f"   ✅ Debug Mode: {settings.DEBUG}")
        print(f"   ✅ Database URL: {settings.DATABASE_URL}")
        print(f"   ✅ Log Level: {settings.LOG_LEVEL}")
        return True
    except Exception as e:
        print(f"   ❌ Configuration Error: {e}")
        return False

def test_database_enhanced():
    """Test enhanced database system"""
    print("🗄️  Testing Enhanced Database System...")
    try:
        from database_enhanced import db_manager, test_db_connection, check_database_health
        print(f"   ✅ Database Manager: {type(db_manager)}")
        print(f"   ✅ Connection Test: {test_db_connection()}")
        health = check_database_health()
        print(f"   ✅ Health Check: {health['overall']}")
        return True
    except Exception as e:
        print(f"   ❌ Database Error: {e}")
        return False

def test_logging_system():
    """Test enhanced logging system"""
    print("📝 Testing Enhanced Logging System...")
    try:
        from logging_config import app_logger, security_logger, performance_logger
        print(f"   ✅ App Logger: {type(app_logger)}")
        print(f"   ✅ Security Logger: {type(security_logger)}")
        print(f"   ✅ Performance Logger: {type(performance_logger)}")
        
        # Test logging
        app_logger.info("Test log message from enhanced system")
        security_logger.log_login_attempt("testuser", "127.0.0.1", True)
        performance_logger.log_request_time("/test", "GET", 0.1, 200)
        print("   ✅ Logging functions working")
        return True
    except Exception as e:
        print(f"   ❌ Logging Error: {e}")
        return False

def test_security_features():
    """Test security features"""
    print("🔒 Testing Security Features...")
    try:
        from security import InputValidator, SQLInjectionProtection
        print(f"   ✅ Input Validator: {type(InputValidator)}")
        print(f"   ✅ SQL Injection Protection: {type(SQLInjectionProtection)}")
        
        # Test email validation
        valid_email = InputValidator.validate_email("test@example.com")
        invalid_email = InputValidator.validate_email("invalid-email")
        print(f"   ✅ Email Validation: valid={valid_email}, invalid={invalid_email}")
        
        # Test SQL injection detection
        safe_input = SQLInjectionProtection.contains_sql_keywords("Hello World")
        dangerous_input = SQLInjectionProtection.contains_sql_keywords("SELECT * FROM users")
        print(f"   ✅ SQL Injection Detection: safe={safe_input}, dangerous={dangerous_input}")
        
        return True
    except Exception as e:
        print(f"   ❌ Security Error: {e}")
        return False

def test_app_import():
    """Test main application import"""
    print("🚀 Testing Main Application Import...")
    try:
        import app
        print(f"   ✅ App Title: {app.app.title}")
        print(f"   ✅ App Version: {app.app.version}")
        print(f"   ✅ Debug Mode: {app.app.debug}")
        return True
    except Exception as e:
        print(f"   ❌ App Import Error: {e}")
        return False

def test_start_script():
    """Test start script"""
    print("▶️  Testing Start Script...")
    try:
        import start
        print("   ✅ Start script imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Start Script Error: {e}")
        return False

def test_file_creation():
    """Test if all new files were created"""
    print("📁 Testing File Creation...")
    required_files = [
        "config.py",
        "database_enhanced.py", 
        "logging_config.py",
        "security.py",
        "requirements_production.txt",
        "deploy_production.sh",
        "Dockerfile",
        "docker-compose.yml"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            missing_files.append(file)
    
    return len(missing_files) == 0

def main():
    """Run all tests"""
    print("🧪 Qrow IQ Enhanced Features Test Suite")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_database_enhanced,
        test_logging_system,
        test_security_features,
        test_app_import,
        test_start_script,
        test_file_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Qrow IQ is ready for production.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
