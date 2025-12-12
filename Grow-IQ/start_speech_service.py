#!/usr/bin/env python3
"""
Start the Speech Recognition Service
This service provides Python-based speech recognition as an alternative to browser-based recognition
"""

import uvicorn
from speech_recognition_service import app

if __name__ == "__main__":
    print("Starting Speech Recognition Service on port 8001...")
    print("This service provides enhanced speech recognition capabilities")
    print("Access the API documentation at: http://localhost:8001/docs")
    
    uvicorn.run(
        "speech_recognition_service:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
