#!/usr/bin/env python3
"""
Test to check exact error and route paths
"""
import requests

def test_exact_error():
    """Test to see the exact error"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Exact Error...")
    print("=" * 50)
    
    # Test different paths to see what happens
    test_paths = [
        "/",
        "/home", 
        "/auth/login",
        "/dashboard",
        "/api/posts",
        "/health"
    ]
    
    for path in test_paths:
        print(f"\n📍 Testing path: {path}")
        try:
            response = requests.get(f"{base_url}{path}", allow_redirects=False)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == 200:
                print("   ✅ Success!")
            elif response.status_code == 303:
                print(f"   🔄 Redirect to: {response.headers.get('location')}")
            elif response.status_code == 401:
                print("   🔒 Unauthorized (requires login)")
            elif response.status_code == 404:
                print("   ❌ Not Found")
                print(f"   Response: {response.text[:200]}...")
            else:
                print(f"   ⚠️  Unexpected: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Analysis:")
    print("If /home returns 404, the route isn't registered properly.")
    print("If /home returns 401, it's working but requires authentication.")
    print("If /home returns 200, it's working perfectly.")
    print("\n🔧 Next Steps:")
    print("1. Check what exact path you're trying to access")
    print("2. Make sure you're logged in if accessing protected routes")
    print("3. Check the server logs for any error messages")

if __name__ == "__main__":
    print("Starting Exact Error Test...")
    print("Make sure your app is running on port 8000!")
    print()
    
    input("Press Enter when your app is running, or Ctrl+C to cancel...")
    test_exact_error()
