#!/usr/bin/env python3
"""
Test script to test image upload functionality
"""

import requests
import os
from pathlib import Path

def test_image_upload():
    """Test image upload to the posts endpoint"""
    
    # Base URL
    base_url = "http://localhost:8000"
    
    # Test image path (create a simple test image)
    test_image_path = "test_image.png"
    
    # Create a simple test image if it doesn't exist
    if not os.path.exists(test_image_path):
        print("Creating test image...")
        # Create a simple 1x1 pixel PNG image
        import base64
        png_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
        with open(test_image_path, "wb") as f:
            f.write(png_data)
        print(f"Test image created: {test_image_path}")
    
    # First, try to access the home page to see if we need to login
    print("Testing home page access...")
    try:
        response = requests.get(f"{base_url}/home")
        print(f"Home page status: {response.status_code}")
        
        if response.status_code == 200:
            print("Home page accessible without login")
        elif response.status_code == 303:  # Redirect to login
            print("Redirected to login page - authentication required")
            print("Please login first and then test image upload manually")
            return
        else:
            print(f"Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to the application. Is it running?")
        print("Please start the application with: python start.py")
        return
    except Exception as e:
        print(f"Error accessing home page: {e}")
        return
    
    # Test the posts endpoint directly
    print("\nTesting posts endpoint...")
    try:
        response = requests.get(f"{base_url}/social/posts")
        print(f"Posts endpoint status: {response.status_code}")
        
        if response.status_code == 401:
            print("Authentication required - this is expected")
        elif response.status_code == 200:
            print("Posts endpoint accessible")
        else:
            print(f"Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"Error testing posts endpoint: {e}")
    
    print("\n" + "="*50)
    print("IMAGE UPLOAD TEST INSTRUCTIONS:")
    print("="*50)
    print("1. Make sure the application is running: python start.py")
    print("2. Open http://localhost:8000 in your browser")
    print("3. Login with your credentials")
    print("4. Go to the home page")
    print("5. Try to create a post with an image:")
    print("   - Click on 'Photo' button")
    print("   - Select an image file")
    print("   - Write some content")
    print("   - Click 'Post'")
    print("6. Check the browser console for any JavaScript errors")
    print("7. Check the terminal where the app is running for backend errors")
    print("\nIf you encounter issues, please share:")
    print("- Any error messages from the browser console")
    print("- Any error messages from the terminal")
    print("- What happens when you try to upload an image")

if __name__ == "__main__":
    test_image_upload()
