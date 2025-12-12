#!/usr/bin/env python3
"""
Simple test for master admin
"""
import requests

# Test master admin login
print("Testing master admin login...")
try:
    response = requests.post("http://localhost:8000/auth/login", data={
        "identifier": "master_admin",
        "password": "MasterAdmin2024!"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
