import os
import sys
import tempfile
import logging
import shutil
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger("nexora.whisper")

# Ensure ffmpeg binary from imageio-ffmpeg is in PATH
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    target_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    if not os.path.exists(target_exe) and os.path.exists(ffmpeg_exe):
        try:
            shutil.copyfile(ffmpeg_exe, target_exe)
        except Exception as e:
            logger.debug(f"Could not copy ffmpeg.exe: {e}")
    if ffmpeg_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
except Exception as e:
    logger.warning(f"Could not configure imageio-ffmpeg: {e}")

# Mapping of ISO language codes to full names
LANGUAGE_NAMES = {
    "uz": "Uzbek",
    "ru": "Russian",
    "en": "English",
    "hi": "Hindi",
    "ar": "Arabic",
    "zh": "Chinese",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "tr": "Turkish",
    "fa": "Persian",
    "ja": "Japanese",
    "it": "Italian",
    "tg": "Tajik",
    "kk": "Kazakh"
}

class WhisperService:
    """
    Research Paper Section 3.8 – Translation Assistance.
    Dedicated Speech-to-Text Pipeline using OpenAI Whisper.
    Supports arbitrary speech, multilingual audio, automatic language detection,
    and runs either via OpenAI Whisper Cloud API or locally via openai-whisper.
    """

    def __init__(self):
        self._local_model = None
        self._local_model_name = "tiny"
        self._openai_client = None

    def _get_openai_client(self):
        from ..config import settings
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        if api_key and api_key.strip():
            if self._openai_client is None:
                try:
                    from openai import OpenAI
                    self._openai_client = OpenAI(api_key=api_key.strip().strip('"').strip("'"))
                    logger.info("OpenAI Whisper API client initialized.")
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI client: {e}")
                    self._openai_client = None
            return self._openai_client
        return None

    def _get_local_model(self):
        if self._local_model is None:
            try:
                import whisper
                logger.info(f"Loading local Whisper model '{self._local_model_name}'...")
                self._local_model = whisper.load_model(self._local_model_name)
                logger.info("Local Whisper model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load local Whisper model: {e}")
                raise RuntimeError(f"Local Whisper model failed to load: {e}")
        return self._local_model

    def get_status(self) -> Dict[str, Any]:
        """Returns the readiness status of the Whisper speech transcription engine."""
        from ..config import settings
        has_openai_key = bool((settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")).strip())
        local_available = False
        try:
            import whisper
            local_available = True
        except ImportError:
            local_available = False

        active_engine = "none"
        if has_openai_key:
            active_engine = "openai_whisper_api"
        elif local_available:
            active_engine = "local_whisper_cpu"

        return {
            "available": has_openai_key or local_available,
            "engine": active_engine,
            "openai_api_configured": has_openai_key,
            "local_whisper_installed": local_available,
            "local_model": self._local_model_name,
            "supported_formats": ["webm", "wav", "mp3", "m4a", "ogg", "mp4", "flac"]
        }

    def transcribe_audio_file(
        self,
        audio_bytes: bytes,
        filename: str = "recording.webm",
        source_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribes arbitrary audio bytes using OpenAI Whisper.
        
        Args:
            audio_bytes: Raw binary bytes of the recorded or uploaded audio.
            filename: Original file name or extension hint.
            source_language: Optional ISO code hint (e.g. 'uz', 'ru', 'en') or None for auto-detect.
        
        Returns:
            Dictionary with transcription, detected language, duration, and status.
        """
        if not audio_bytes or len(audio_bytes) < 120:
            raise ValueError("Audio recording is empty or too short. Please speak clearly into the microphone.")

        # Determine extension
        ext = ".webm"
        if "." in filename:
            ext = "." + filename.rsplit(".", 1)[-1].lower()
        if ext not in [".webm", ".wav", ".mp3", ".m4a", ".ogg", ".mp4", ".flac"]:
            ext = ".webm"

        # 1. Try OpenAI Whisper Cloud API if configured
        openai_client = self._get_openai_client()
        if openai_client:
            try:
                logger.info(f"Transcribing audio via OpenAI Whisper API ({len(audio_bytes)} bytes)...")
                # Write to temp file for file-like tuple upload
                import io
                audio_io = io.BytesIO(audio_bytes)
                audio_io.name = f"audio{ext}"

                kwargs = {
                    "model": "whisper-1",
                    "file": audio_io,
                    "response_format": "verbose_json"
                }
                if source_language and source_language != "auto":
                    kwargs["language"] = source_language

                transcription = openai_client.audio.transcriptions.create(**kwargs)
                
                text = getattr(transcription, "text", "") or ""
                detected_lang = getattr(transcription, "language", source_language or "unknown")
                duration = getattr(transcription, "duration", 0.0)

                return {
                    "success": True,
                    "text": text.strip(),
                    "language": detected_lang,
                    "language_name": LANGUAGE_NAMES.get(detected_lang, detected_lang.capitalize()),
                    "duration_seconds": round(duration, 2),
                    "engine": "openai-whisper-api"
                }
            except Exception as e:
                logger.warning(f"OpenAI Whisper API failed ({e}), falling back to local Whisper...")

        # 2. Try Local Whisper Engine
        try:
            model = self._get_local_model()
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name

            try:
                transcribe_args = {
                    "fp16": False,  # Safe CPU execution
                }
                if source_language and source_language != "auto":
                    transcribe_args["language"] = source_language

                result = model.transcribe(tmp_path, **transcribe_args)
                raw_text = result.get("text", "").strip()
                detected_lang = result.get("language", source_language or "en")

                # Calculate approximate duration if segments available
                segments = result.get("segments", [])
                duration = segments[-1].get("end", 0.0) if segments else 0.0

                return {
                    "success": True,
                    "text": raw_text,
                    "language": detected_lang,
                    "language_name": LANGUAGE_NAMES.get(detected_lang, detected_lang.capitalize()),
                    "duration_seconds": round(duration, 2),
                    "engine": f"local-whisper-{self._local_model_name}"
                }
            finally:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Local Whisper transcription failed: {e}")
            raise RuntimeError(f"Speech transcription failed: {str(e)}")

whisper_service = WhisperService()

