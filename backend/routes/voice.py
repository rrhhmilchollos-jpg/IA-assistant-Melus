"""Voice and Advanced Features routes for Assistant Melus"""
from fastapi import APIRouter, HTTPException, Request
from typing import Optional
import logging
import os
import base64
import tempfile
from pathlib import Path

from utils import generate_id, utc_now, get_authenticated_user

from emergentintegrations.llm.openai import OpenAISpeechToText

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')


@router.post("/transcribe")
async def transcribe_audio(request: Request):
    """Transcribe audio to text using OpenAI Whisper"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    user_id = user_doc["user_id"]
    
    # Check credits (transcription costs 25 credits)
    TRANSCRIPTION_COST = 25
    if user_doc["credits"] < TRANSCRIPTION_COST:
        raise HTTPException(status_code=402, detail="Créditos insuficientes para transcripción")
    
    try:
        body = await request.json()
        audio_data = body.get("audio_data")
        language = body.get("language", "es")  # Default Spanish
        
        if not audio_data:
            raise HTTPException(status_code=400, detail="No audio data provided")
        
        # Decode base64 audio
        try:
            # Handle data URL format
            if "," in audio_data:
                audio_bytes = base64.b64decode(audio_data.split(",")[1])
            else:
                audio_bytes = base64.b64decode(audio_data)
        except Exception as e:
            logger.error(f"Failed to decode audio: {e}")
            raise HTTPException(status_code=400, detail="Invalid audio data format")
        
        # Check file size (max 25MB)
        if len(audio_bytes) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Audio file too large (max 25MB)")
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Initialize Whisper
            stt = OpenAISpeechToText(api_key=EMERGENT_LLM_KEY)
            
            # Transcribe
            with open(tmp_path, "rb") as audio_file:
                response = await stt.transcribe(
                    file=audio_file,
                    model="whisper-1",
                    response_format="json",
                    language=language
                )
            
            transcribed_text = response.text
            
            # Deduct credits
            new_credits = user_doc["credits"] - TRANSCRIPTION_COST
            await db.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {"credits": new_credits},
                    "$inc": {"credits_used": TRANSCRIPTION_COST}
                }
            )
            
            # Log usage
            await db.agent_usage.insert_one({
                "usage_id": generate_id("usage"),
                "user_id": user_id,
                "agent_type": "voice_transcription",
                "credits_used": TRANSCRIPTION_COST,
                "created_at": utc_now()
            })
            
            return {
                "text": transcribed_text,
                "language": language,
                "credits_used": TRANSCRIPTION_COST,
                "credits_remaining": new_credits
            }
            
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.post("/text-to-speech")
async def text_to_speech(request: Request):
    """Convert text to speech (placeholder for future TTS integration)"""
    raise HTTPException(status_code=501, detail="Text-to-speech not yet implemented")
