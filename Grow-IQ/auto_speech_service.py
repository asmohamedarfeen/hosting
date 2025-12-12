"""
Auto Speech Service
Handles automatic speech-to-text processing and submission for mock interviews
"""

import asyncio
import logging
import tempfile
import traceback
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import speech_recognition as sr
import base64
import numpy as np
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth_utils import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize speech recognizer
recognizer = sr.Recognizer()

class AutoSpeechRequest(BaseModel):
    audio_data: str  # Base64 encoded audio data
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    language: str = "en-US"
    auto_submit: bool = True

class AutoSpeechResponse(BaseModel):
    success: bool
    text: str
    confidence: float
    submitted: bool
    message_id: Optional[str] = None
    error: Optional[str] = None

class AutoSpeechService:
    def __init__(self):
        self.processing_queue = asyncio.Queue()
        self.is_processing = False
    
    async def process_auto_speech(self, request: AutoSpeechRequest, db: Session) -> AutoSpeechResponse:
        """
        Process speech automatically and submit to interview session
        """
        try:
            # Decode audio data
            audio_bytes = self._decode_base64_audio(request.audio_data)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Process audio for speech recognition
                with sr.AudioFile(temp_file_path) as source:
                    # Adjust for ambient noise
                    try:
                        recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    except Exception:
                        pass
                    
                    # Record audio
                    audio = recognizer.record(source)
                
                # Perform speech recognition
                try:
                    text = recognizer.recognize_google(audio, language=request.language)
                    confidence = 0.8  # Google doesn't provide confidence scores
                except sr.UnknownValueError:
                    return AutoSpeechResponse(
                        success=False,
                        text="",
                        confidence=0.0,
                        submitted=False,
                        error="Could not understand the audio"
                    )
                except sr.RequestError as e:
                    return AutoSpeechResponse(
                        success=False,
                        text="",
                        confidence=0.0,
                        submitted=False,
                        error=f"Speech recognition service error: {str(e)}"
                    )
                
                # If auto_submit is enabled and we have a session_id, submit the message
                submitted = False
                message_id = None
                
                if request.auto_submit and request.session_id and text.strip():
                    try:
                        # Submit to interview session
                        submission_result = await self._submit_to_interview(
                            session_id=request.session_id,
                            text=text,
                            user_id=request.user_id,
                            db=db
                        )
                        submitted = submission_result.get("success", False)
                        message_id = submission_result.get("message_id")
                    except Exception as e:
                        logger.error(f"Failed to submit to interview: {str(e)}")
                        # Still return the text even if submission failed
                
                return AutoSpeechResponse(
                    success=True,
                    text=text,
                    confidence=confidence,
                    submitted=submitted,
                    message_id=message_id
                )
                
            finally:
                # Clean up temporary file
                try:
                    import os
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                except Exception:
                    pass
                    
        except Exception as e:
            logger.error(f"Auto speech processing error: {str(e)}")
            logger.error(traceback.format_exc())
            return AutoSpeechResponse(
                success=False,
                text="",
                confidence=0.0,
                submitted=False,
                error=f"Processing error: {str(e)}"
            )
    
    def _decode_base64_audio(self, data_str: str) -> bytes:
        """Decode base64 audio data"""
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
    
    async def _submit_to_interview(self, session_id: str, text: str, user_id: Optional[int], db: Session) -> Dict[str, Any]:
        """
        Submit the transcribed text to the interview session
        """
        try:
            # Import here to avoid circular imports
            from mockinterview_routes import send_message
            
            # Create message request
            message_request = {
                "session_id": session_id,
                "message": text,
                "user_id": user_id
            }
            
            # Submit message to interview
            result = await send_message(message_request, db)
            
            return {
                "success": True,
                "message_id": result.get("message_id") if isinstance(result, dict) else None
            }
            
        except Exception as e:
            logger.error(f"Failed to submit to interview session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Initialize service
auto_speech_service = AutoSpeechService()

# FastAPI endpoints
app = FastAPI(title="Auto Speech Service")

@app.post("/api/auto-speech/process", response_model=AutoSpeechResponse)
async def process_auto_speech(
    request: AutoSpeechRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process speech automatically and optionally submit to interview
    """
    try:
        # Set user_id from current user if not provided
        if not request.user_id:
            request.user_id = current_user.id
        
        result = await auto_speech_service.process_auto_speech(request, db)
        return result
        
    except Exception as e:
        logger.error(f"Auto speech endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/auto-speech/validate")
async def validate_audio(request: AutoSpeechRequest):
    """
    Validate if audio contains speech without processing
    """
    try:
        audio_bytes = auto_speech_service._decode_base64_audio(request.audio_data)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            with sr.AudioFile(temp_file_path) as source:
                audio = recognizer.record(source)
                audio_data = audio.get_raw_data()
                
                # Convert to float32 array for analysis
                audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Calculate RMS for voice activity detection
                rms = np.sqrt(np.mean(audio_array ** 2))
                duration = len(audio_array) / source.SAMPLE_RATE
                
                # Determine if voice is present
                has_voice = rms > 0.005 and duration >= 0.5
                confidence = min(1.0, rms / 0.05)  # Scale confidence
                
                return {
                    "has_voice": has_voice,
                    "confidence": confidence,
                    "duration": duration,
                    "rms": rms
                }
                
        finally:
            try:
                import os
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            except Exception:
                pass
                
    except Exception as e:
        logger.error(f"Audio validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
