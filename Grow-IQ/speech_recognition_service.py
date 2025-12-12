from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import speech_recognition as sr
import io
import tempfile
import os
from typing import Optional
import base64
import traceback

app = FastAPI(title="Speech Recognition Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize speech recognizer with safer defaults
recognizer = sr.Recognizer()
# Reduce sensitivity to ambient noise and avoid dynamic fluctuation issues
recognizer.dynamic_energy_threshold = False
recognizer.energy_threshold = 200  # tune as needed
recognizer.pause_threshold = 0.6

def _decode_base64_audio(data_str: str) -> bytes:
    """Accepts raw base64 or data URLs and returns bytes."""
    if not data_str:
        raise ValueError("Empty audio_data")
    # Strip data URL prefix if present
    if "," in data_str and data_str.strip().startswith("data:"):
        data_str = data_str.split(",", 1)[1]
    # Fix missing padding
    padding = len(data_str) % 4
    if padding:
        data_str += "=" * (4 - padding)
    return base64.b64decode(data_str)

class SpeechRecognitionRequest(BaseModel):
    audio_data: str  # Base64 encoded audio data
    language: str = "en-US"

class SpeechRecognitionResponse(BaseModel):
    text: str
    confidence: Optional[float] = None
    success: bool
    error: Optional[str] = None

@app.post("/speech-to-text", response_model=SpeechRecognitionResponse)
async def speech_to_text(request: SpeechRecognitionRequest):
    """
    Convert speech to text using Google Speech Recognition
    """
    try:
        # Decode base64 audio data (supports data URLs)
        audio_bytes = _decode_base64_audio(request.audio_data)

        # Write WAV bytes to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name

        try:
            with sr.AudioFile(temp_file_path) as source:
                # Optional: light ambient calibration
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=0.2)
                except Exception:
                    pass
                audio = recognizer.record(source)

            # Recognize speech using Google Speech Recognition
            text = recognizer.recognize_google(audio, language=request.language)

            return SpeechRecognitionResponse(
                text=text,
                confidence=0.8,  # Google doesn't provide confidence scores
                success=True
            )
        finally:
            if os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass
                
    except sr.UnknownValueError:
        return SpeechRecognitionResponse(
            text="",
            success=False,
            error="Could not understand the audio"
        )
    except sr.RequestError as e:
        return SpeechRecognitionResponse(
            text="",
            success=False,
            error=f"Speech recognition service error: {str(e)}"
        )
    except Exception as e:
        # Include traceback in logs for easier debugging
        print("[speech-to-text] Unexpected error:\n" + traceback.format_exc())
        return SpeechRecognitionResponse(
            text="",
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

@app.post("/speech-to-text-file", response_model=SpeechRecognitionResponse)
async def speech_to_text_file(audio_file: UploadFile = File(...), language: str = "en-US"):
    """
    Convert speech to text from uploaded audio file
    """
    try:
        # Read the uploaded file
        audio_data = await audio_file.read()
        
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        try:
            # Use the audio file
            with sr.AudioFile(temp_file_path) as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source)
                # Record the audio
                audio = recognizer.record(source)
            
            # Recognize speech using Google Speech Recognition
            text = recognizer.recognize_google(
                audio, 
                language=language
            )
            
            return SpeechRecognitionResponse(
                text=text,
                confidence=0.8,
                success=True
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except sr.UnknownValueError:
        return SpeechRecognitionResponse(
            text="",
            success=False,
            error="Could not understand the audio"
        )
    except sr.RequestError as e:
        return SpeechRecognitionResponse(
            text="",
            success=False,
            error=f"Speech recognition service error: {str(e)}"
        )
    except Exception as e:
        return SpeechRecognitionResponse(
            text="",
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok", "service": "speech-recognition"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
