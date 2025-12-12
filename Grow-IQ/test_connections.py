#!/usr/bin/env python3
"""
Test script for the LinkedIn-style connection system.
This script tests the core functionality of the connection management system.
"""

import requests
import json
import time
from typing import Dict, Any

class ConnectionSystemTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} {test_name}"
        if message:
            result += f": {message}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        
    def test_connection_endpoints(self):
        """Test all connection-related API endpoints"""
        print("\n🔗 Testing Connection System Endpoints")
        print("=" * 50)
        
        # Test 1: Check if server is running
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test("Server Status", True, "Server is running")
            else:
                self.log_test("Server Status", False, f"Server returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.log_test("Server Status", False, "Cannot connect to server")
            return False
            
        # Test 2: Test connections page
        try:
            response = self.session.get(f"{self.base_url}/connections/")
            if response.status_code == 200:
                self.log_test("Connections Page", True, "Page loads successfully")
            else:
                self.log_test("Connections Page", False, f"Page returned {response.status_code}")
        except Exception as e:
            self.log_test("Connections Page", False, f"Error: {str(e)}")
            
        # Test 3: Test API endpoints (without authentication)
        api_endpoints = [
            "/connections/api/stats",
            "/connections/api/connections",
            "/connections/api/pending-requests",
            "/connections/api/sent-requests",
            "/connections/api/suggestions"
        ]
        
        for endpoint in api_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 401:
                    self.log_test(f"API {endpoint}", True, "Properly requires authentication")
                else:
                    self.log_test(f"API {endpoint}", False, f"Expected 401, got {response.status_code}")
            except Exception as e:
                self.log_test(f"API {endpoint}", False, f"Error: {str(e)}")
                
        return True
        
    def test_database_models(self):
        """Test database model functionality"""
        print("\n🗄️ Testing Database Models")
        print("=" * 50)
        
        # Test 1: Check if models can be imported
        try:
            from models import User, Connection, FriendRequest, Notification
            self.log_test("Model Import", True, "All models imported successfully")
        except ImportError as e:
            self.log_test("Model Import", False, f"Import error: {str(e)}")
            return False
            
        # Test 2: Check model attributes
        try:
            # Test User model
            user_attrs = ['id', 'username', 'email', 'full_name', 'title', 'company']
            user_model = User()
            for attr in user_attrs:
                if hasattr(user_model, attr):
                    continue
                else:
                    self.log_test("User Model Attributes", False, f"Missing attribute: {attr}")
                    break
            else:
                self.log_test("User Model Attributes", True, "All required attributes present")
                
            # Test Connection model
            connection_attrs = ['id', 'user_id', 'connected_user_id', 'status', 'created_at']
            connection_model = Connection()
            for attr in connection_attrs:
                if hasattr(connection_model, attr):
                    continue
                else:
                    self.log_test("Connection Model Attributes", False, f"Missing attribute: {attr}")
                    break
            else:
                self.log_test("Connection Model Attributes", True, "All required attributes present")
                
            # Test FriendRequest model
            friend_request_attrs = ['id', 'sender_id', 'receiver_id', 'status', 'message', 'created_at']
            friend_request_model = FriendRequest()
            for attr in friend_request_attrs:
                if hasattr(friend_request_model, attr):
                    continue
                else:
                    self.log_test("FriendRequest Model Attributes", False, f"Missing attribute: {attr}")
                    break
            else:
                self.log_test("FriendRequest Model Attributes", True, "All required attributes present")
                
        except Exception as e:
            self.log_test("Model Validation", False, f"Error: {str(e)}")
            
        return True
        
    def test_frontend_components(self):
        """Test frontend components and JavaScript functionality"""
        print("\n🎨 Testing Frontend Components")
        print("=" * 50)
        
        # Test 1: Check if connections.html template exists
        try:
            with open("templates/connections.html", "r") as f:
                content = f.read()
                if "connection-card" in content:
                    self.log_test("Connections Template", True, "Template contains required elements")
                else:
                    self.log_test("Connections Template", False, "Missing connection-card elements")
        except FileNotFoundError:
            self.log_test("Connections Template", False, "Template file not found")
        except Exception as e:
            self.log_test("Connections Template", False, f"Error: {str(e)}")
            
        # Test 2: Check if connections.js exists
        try:
            with open("static/js/connections.js", "r") as f:
                content = f.read()
                if "sendConnectionRequest" in content:
                    self.log_test("Connections JavaScript", True, "JavaScript file contains required functions")
                else:
                    self.log_test("Connections JavaScript", False, "Missing required JavaScript functions")
        except FileNotFoundError:
            self.log_test("Connections JavaScript", False, "JavaScript file not found")
        except Exception as e:
            self.log_test("Connections JavaScript", False, f"Error: {str(e)}")
            
        # Test 3: Check if CSS styles exist
        try:
            with open("static/css/style.css", "r") as f:
                content = f.read()
                if ".connection-card" in content:
                    self.log_test("Connection CSS Styles", True, "CSS contains required styles")
                else:
                    self.log_test("Connection CSS Styles", False, "Missing connection CSS styles")
        except FileNotFoundError:
            self.log_test("Connection CSS Styles", False, "CSS file not found")
        except Exception as e:
            self.log_test("Connection CSS Styles", False, f"Error: {str(e)}")
            
        return True
        
    def test_connection_routes(self):
        """Test connection route functionality"""
        print("\n🛣️ Testing Connection Routes")
        print("=" * 50)
        
        # Test 1: Check if connection_routes.py exists
        try:
            with open("connection_routes.py", "r") as f:
                content = f.read()
                
                # Check for required endpoints
                required_endpoints = [
                    "send-request",
                    "respond-request",
                    "withdraw-request",
                    "remove-connection",
                    "cancel-request"
                ]
                
                missing_endpoints = []
                for endpoint in required_endpoints:
                    if f"/api/{endpoint}" not in content:
                        missing_endpoints.append(endpoint)
                        
                if not missing_endpoints:
                    self.log_test("Connection Routes", True, "All required endpoints present")
                else:
                    self.log_test("Connection Routes", False, f"Missing endpoints: {', '.join(missing_endpoints)}")
                    
        except FileNotFoundError:
            self.log_test("Connection Routes", False, "Route file not found")
        except Exception as e:
            self.log_test("Connection Routes", False, f"Error: {str(e)}")
            
        # Test 2: Check for required functions
        try:
            with open("connection_routes.py", "r") as f:
                content = f.read()
                
                required_functions = [
                    "get_connection_suggestions_for_user",
                    "calculate_mutual_connections_count",
                    "get_connection_status"
                ]
                
                missing_functions = []
                for func in required_functions:
                    if f"def {func}" not in content:
                        missing_functions.append(func)
                        
                if not missing_functions:
                    self.log_test("Connection Functions", True, "All required functions present")
                else:
                    self.log_test("Connection Functions", False, f"Missing functions: {', '.join(missing_functions)}")
                    
        except Exception as e:
            self.log_test("Connection Functions", False, f"Error: {str(e)}")
            
        return True
        
    def run_all_tests(self):
        """Run all tests and generate summary"""
        print("🚀 Starting Connection System Tests")
        print("=" * 60)
        
        # Run all test suites
        test_suites = [
            ("Connection Endpoints", self.test_connection_endpoints),
            ("Database Models", self.test_database_models),
            ("Frontend Components", self.test_frontend_components),
            ("Connection Routes", self.test_connection_routes)
        ]
        
        for suite_name, test_func in test_suites:
            try:
                test_func()
            except Exception as e:
                self.log_test(suite_name, False, f"Test suite failed: {str(e)}")
                
        # Generate summary
        self.generate_summary()
        
    def generate_summary(self):
        """Generate test summary"""
        print("\n📊 Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
                    
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! The connection system is working correctly.")
        else:
            print(f"\n⚠️ {failed_tests} test(s) failed. Please review the issues above.")
            
        return passed_tests == total_tests

def main():
    """Main function to run tests"""
    print("🔗 LinkedIn-Style Connection System Test Suite")
    print("=" * 60)
    
    # Create tester instance
    tester = ConnectionSystemTester()
    
    # Run all tests
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
