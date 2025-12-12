#!/usr/bin/env python3
"""
Google OAuth Setup Script for CareerConnect
This script helps you configure Google OAuth for your application.
"""

import os
import sys

def create_env_file():
    """Create a .env file with Google OAuth configuration"""
    
    print("🚀 Google OAuth Setup for CareerConnect")
    print("=" * 50)
    
    # Check if .env file already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print("\n📋 Please provide the following information:")
    print("(You can get these from Google Cloud Console)")
    print()
    
    # Get Google OAuth credentials
    client_id = input("Google Client ID: ").strip()
    if not client_id:
        print("❌ Client ID is required!")
        return
    
    client_secret = input("Google Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret is required!")
        return
    
    redirect_uri = input("Redirect URI [http://localhost:8000/auth/google/callback]: ").strip()
    if not redirect_uri:
        redirect_uri = "http://localhost:8000/auth/google/callback"
    
    # Get other settings
    secret_key = input("Secret Key [dev-secret-key-change-in-production]: ").strip()
    if not secret_key:
        secret_key = "dev-secret-key-change-in-production"
    
    debug = input("Debug mode [true]: ").strip()
    if not debug:
        debug = "true"
    
    environment = input("Environment [development]: ").strip()
    if not environment:
        environment = "development"
    
    # Create .env content
    env_content = f"""# Google OAuth Configuration
GOOGLE_CLIENT_ID={client_id}
GOOGLE_CLIENT_SECRET={client_secret}
GOOGLE_REDIRECT_URI={redirect_uri}

# Application Settings
DEBUG={debug}
ENVIRONMENT={environment}
SECRET_KEY={secret_key}

# Database
DATABASE_URL=sqlite:///./dashboard.db

# Server
HOST=0.0.0.0
PORT=8000
"""
    
    # Write .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("\n✅ .env file created successfully!")
        print(f"📁 Location: {os.path.abspath('.env')}")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return
    
    print("\n🔧 Next Steps:")
    print("1. Make sure your Google Cloud Console is configured")
    print("2. Set the redirect URI in Google Console to: " + redirect_uri)
    print("3. Start your application: python start.py")
    print("4. Test Google OAuth on the login page")
    
    print("\n📚 For detailed setup instructions, see: GOOGLE_OAUTH_SETUP.md")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import requests
        print("✅ requests library is available")
    except ImportError:
        print("❌ requests library not found!")
        print("Install it with: pip install requests")
        return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy is available")
    except ImportError:
        print("❌ SQLAlchemy not found!")
        print("Install it with: pip install sqlalchemy")
        return False
    
    print("✅ All dependencies are available")
    return True

def main():
    """Main setup function"""
    print("CareerConnect - Google OAuth Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        return
    
    print("\n" + "=" * 40)
    
    # Create environment file
    create_env_file()
    
    print("\n🎉 Setup complete!")
    print("Happy coding! 🚀")

if __name__ == "__main__":
    main()
