#!/usr/bin/env python3
"""
Port Test - Check if port 8000 is available
"""

import socket

def test_port():
    """Test if port 8000 is available"""
    print("🔌 Testing Port 8000...")
    
    try:
        # Create a socket and try to bind to port 8000
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        
        if result == 0:
            print("   ❌ Port 8000 is already in use")
            print("   💡 Try using a different port or stop the existing process")
            return False
        else:
            print("   ✅ Port 8000 is available")
            return True
            
    except Exception as e:
        print(f"   ❌ Error testing port: {e}")
        return False

if __name__ == "__main__":
    test_port()
