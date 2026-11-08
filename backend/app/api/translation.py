import base64
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from ..services.gemini_service import gemini_service
from ..services.whisper_service import whisper_service

router = APIRouter(prefix="/api/translate", tags=["Translation"])

class TranslationRequest(BaseModel):
    text: str = Field(..., description="Arbitrary text, sentence, or paragraph to translate")
    source_language: str = Field(default="auto", description="Source language ISO code or 'auto' for automatic detection")
    target_language: str = Field(default="uz", description="Target language ISO code")

class ImageTranslationRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 or URL of captured signboard, menu, or inscription")
    target_language: str = Field(default="en", description="Target language ISO code")

class AudioTranscribeRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64 encoded audio bytes (webm, wav, mp3, m4a, ogg)")
    filename: Optional[str] = Field(default="recording.webm", description="Audio filename hint")
    source_language: Optional[str] = Field(default="auto", description="Optional source language code hint")

class VoiceTranslationRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64 encoded audio bytes")
    filename: Optional[str] = Field(default="recording.webm", description="Audio filename hint")
    source_language: Optional[str] = Field(default="auto", description="Optional source language code")
    target_language: str = Field(default="uz", description="Desired target language ISO code")

@router.get("/status")
def get_translation_status():
    """
    Returns the real-time operational status of both the Whisper Speech-to-Text engine
    and Gemini AI Translation service.
    """
    whisper_stat = whisper_service.get_status()
    gemini_available = gemini_service.is_available()
    return {
        "status": "ready" if (whisper_stat["available"] and gemini_available) else "degraded",
        "whisper": whisper_stat,
        "gemini": {
            "available": gemini_available,
            "active_model": gemini_service.model_name
        }
    }

@router.post("")
def translate_text(req: TranslationRequest):
    """
    Research Paper Section 3.8 – Translation Assistance.
    Dynamic AI-powered translation for arbitrary text, questions, or long paragraphs.
    Preserves context, tone, and sentence structure, with phonetic pronunciation guide.
    """
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    try:
        result = gemini_service.translate_text(
            text=req.text.strip(),
            source_language=req.source_language or "auto",
            target_language=req.target_language or "uz"
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/transcribe")
def transcribe_audio_json(req: AudioTranscribeRequest):
    """
    Research Paper Section 3.8 – Speech Recognition via OpenAI Whisper.
    Accepts arbitrary base64 audio and returns the complete transcription
    with automatic language identification.
    """
    if not req.audio_base64:
        raise HTTPException(status_code=400, detail="Audio recording data is required.")

    try:
        raw_b64 = req.audio_base64
        if "base64," in raw_b64:
            raw_b64 = raw_b64.split("base64,", 1)[1]
        audio_bytes = base64.b64decode(raw_b64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 audio data: {e}")

    try:
        result = whisper_service.transcribe_audio_file(
            audio_bytes=audio_bytes,
            filename=req.filename or "recording.webm",
            source_language=req.source_language if req.source_language != "auto" else None
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech transcription failed: {str(e)}")

@router.post("/transcribe-file")
async def transcribe_audio_upload(
    file: UploadFile = File(...),
    source_language: Optional[str] = Form("auto")
):
    """
    Multipart file upload endpoint for OpenAI Whisper speech transcription.
    Supports .webm, .wav, .mp3, .m4a, .ogg, .flac files.
    """
    try:
        audio_bytes = await file.read()
        if not audio_bytes or len(audio_bytes) < 120:
            raise HTTPException(status_code=400, detail="Uploaded audio file is empty or too short.")

        result = whisper_service.transcribe_audio_file(
            audio_bytes=audio_bytes,
            filename=file.filename or "recording.webm",
            source_language=source_language if source_language != "auto" else None
        )
        return result
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech transcription failed: {str(e)}")

@router.post("/voice")
def translate_voice_pipeline(req: VoiceTranslationRequest):
    """
    Unified Voice Translation Workflow (Section 3.8):
    1. Whisper transcribes the voice recording into complete text.
    2. Whisper detects the spoken language.
    3. Gemini dynamically translates the transcribed text into the target language.
    4. Returns both the original transcription and translated result.
    """
    if not req.audio_base64:
        raise HTTPException(status_code=400, detail="Audio recording data is required.")

    try:
        raw_b64 = req.audio_base64
        if "base64," in raw_b64:
            raw_b64 = raw_b64.split("base64,", 1)[1]
        audio_bytes = base64.b64decode(raw_b64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 audio data: {e}")

    # Step 1: Whisper transcription
    try:
        stt_result = whisper_service.transcribe_audio_file(
            audio_bytes=audio_bytes,
            filename=req.filename or "recording.webm",
            source_language=req.source_language if req.source_language != "auto" else None
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice transcription failed: {str(e)}")

    transcribed_text = stt_result.get("text", "").strip()
    detected_lang = stt_result.get("language", "auto")

    if not transcribed_text:
        return {
            "transcription": stt_result,
            "translation": None,
            "message": "No spoken words were recognized in the audio recording."
        }

    # Step 2: Gemini translation
    try:
        translation_result = gemini_service.translate_text(
            text=transcribed_text,
            source_language=detected_lang,
            target_language=req.target_language or "uz"
        )
        return {
            "transcription": stt_result,
            "translation": translation_result
        }
    except Exception as e:
        # Return transcription even if translation encounters error
        return {
            "transcription": stt_result,
            "translation": None,
            "error": f"Transcription succeeded, but translation failed: {str(e)}"
        }

@router.post("/image")
def translate_image(req: ImageTranslationRequest):
    """
    Research Paper Section 3.8 – Translation Assistance (Camera / Signboard OCR).
    Extracts visible written text from signs, menus, or plaques and translates it.
    """
    if not req.image_base64:
        raise HTTPException(status_code=400, detail="Image data is required for camera translation.")

    try:
        result = gemini_service.translate_image_text(
            image_data=req.image_base64,
            target_language=req.target_language or "en"
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Camera translation failed: {str(e)}")
