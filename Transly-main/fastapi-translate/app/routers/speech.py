# app/routers/speech.py
import base64
import io
import tempfile
import sys
import os
import warnings
from typing import Optional, Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from fastapi.logger import logger

import app.state as state
from app.model import translate_with_model
from app.schemas import SpeechToTextRequest, SpeechTranslateRequest, SpeechToTextResponse, SpeechTranslateResponse

# Ensure ffmpeg is in PATH (Windows)
if os.name == 'nt':
    ffmpeg_path = r"C:\ffmpeg\bin"
    if os.path.exists(ffmpeg_path) and ffmpeg_path not in os.environ.get('PATH', ''):
        os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ.get('PATH', '')

# suppress noisy pydub ffmpeg warnings
warnings.filterwarnings("ignore", message=".*ffmpeg or avconv.*")

# optional imports
whisper = None
try:
    import whisper as whisper_module
    whisper = whisper_module
except Exception as e:
    logger.warning("Whisper not available: %s", e)

pydub = None
AudioSegment = None
try:
    from pydub import AudioSegment as AudioSegment_
    AudioSegment = AudioSegment_
    import pydub as pydub_module
    pydub = pydub_module
    logger.info("pydub available for audio conversions")
except Exception:
    logger.info("pydub not available; will use audio bytes as-is for Whisper")

# optional TTS utils (if present)
tts_available = False
synthesize_text_to_wav = None
try:
    from app.utils.tts import synthesize_text_to_wav
    tts_available = True
except ImportError:
    logger.info("TTS module not available; TTS synthesis will be disabled")
    tts_available = False
except Exception as e:
    logger.warning("Failed to import TTS module: %s", e)
    tts_available = False

router = APIRouter(tags=["speech"])


# -------------------------
# Helpers
# -------------------------
def _ensure_whisper_loaded():
    """Lazy-load whisper model into state.whisper_model if not present."""
    if whisper is None:
        return  # not installed; caller must handle
    if getattr(state, "whisper_model", None) is None:
        try:
            state.whisper_model = whisper.load_model("medium")
            logger.info("Whisper model loaded (medium) - Good accuracy for Nepali/Sinhala with faster response")
        except Exception as e:
            logger.exception("Failed to load Whisper model: %s", e)
            state.whisper_model = None


def _decode_base64_audio_str(b64_str: str) -> bytes:
    """Decode base64 string. Raises HTTPException on failure."""
    if not isinstance(b64_str, str) or not b64_str.strip():
        raise HTTPException(status_code=400, detail="audio_base64 must be a non-empty string.")
    s = b64_str.strip()
    if s.startswith("data:"):
        try:
            s = s.split(",", 1)[1]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid data URL for audio_base64.")
    try:
        return base64.b64decode(s, validate=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 audio: {e}")


def _convert_to_wav_bytes(audio_bytes: bytes, filename_hint: str = "") -> bytes:
    """
    Convert audio bytes to WAV (16kHz mono) using pydub if available.
    Returns bytes (WAV) or original bytes if conversion not possible.
    Skips conversion to avoid ffmpeg issues on some systems.
    """
    # Skip pydub conversion - Whisper can handle most formats natively
    # This avoids ffmpeg dependency issues
    logger.debug("Skipping pydub conversion; using audio as-is for Whisper")
    return audio_bytes


def _write_temp_file(data: bytes, suffix: str = ".wav") -> str:
    """Write bytes to a temporary file and return its path. Caller must delete the file."""
    # Ensure suffix starts with dot
    if suffix and not suffix.startswith('.'):
        suffix = '.' + suffix
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        tf.write(data)
        tf.flush()
    finally:
        tf.close()
    logger.debug("Created temp file: %s with suffix: %s", tf.name, suffix)
    return tf.name


def _safe_remove(path: Optional[str]):
    if not path:
        return
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.debug("Removed temp file: %s", path)
    except Exception:
        logger.exception("Failed to remove temp file: %s", path)


def _run_whisper_transcribe(audio_bytes: bytes, filename_hint: str = "audio.wav", language: Optional[str] = None) -> Dict[str, Any]:
    """
    Write audio_bytes to temp file, run whisper.transcribe,
    then clean up file. Returns dict {"transcript": str, "detected_language": str}.
    language: REQUIRED language code ("ne", "si", "en") - no auto-detection
    Raises HTTPException on errors.
    """
    if whisper is None:
        raise HTTPException(status_code=503, detail="Whisper is not installed on the server.")

    _ensure_whisper_loaded()
    if state.whisper_model is None:
        raise HTTPException(status_code=503, detail="Whisper model not loaded. Check server logs.")

    # Validate language is provided
    if not language or language not in ["ne", "si", "en"]:
        raise HTTPException(status_code=400, detail="'language' field is required. Use 'ne' (Nepali), 'si' (Sinhala), or 'en' (English).")

    # Preserve original file extension for Whisper to detect format
    file_ext = ".wav"
    if filename_hint:
        name_lower = filename_hint.lower()
        if name_lower.endswith('.mp3'):
            file_ext = ".mp3"
        elif name_lower.endswith('.m4a'):
            file_ext = ".m4a"
        elif name_lower.endswith('.ogg') or name_lower.endswith('.oga'):
            file_ext = ".ogg"
        elif name_lower.endswith('.flac'):
            file_ext = ".flac"
        elif name_lower.endswith('.webm'):
            file_ext = ".webm"
        elif name_lower.endswith('.aac'):
            file_ext = ".aac"
    
    wav_bytes = audio_bytes
    tmp_path = None
    try:
        tmp_path = _write_temp_file(wav_bytes, suffix=file_ext)
        logger.info("Transcribing with language: %s (file: %s)", language, file_ext)
        
        # Use the provided language (no auto-detection)
        whisper_lang = language
        logger.info("Whisper using fixed language: %s", whisper_lang)
        
        # Run Whisper transcription with fixed language
        result = state.whisper_model.transcribe(
            tmp_path,
            language=whisper_lang,  # "ne", "si", or "en" - FIXED, not auto
            task="transcribe",
            verbose=False,
            fp16=False,
            beam_size=1,  # No need for larger beam with fixed language
            best_of=1,
        )
        
        transcript = result.get("text", "").strip()
        
        # Return the language we were given (not detected)
        final_lang = language
        
        logger.info("Whisper transcription complete: language=%s, transcript_length=%d", 
                   final_lang, len(transcript))
        
        if not transcript:
            logger.warning("Warning: Empty transcript returned")
        
        return {"transcript": transcript, "detected_language": final_lang}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Whisper error: %s", e)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        _safe_remove(tmp_path)


# -------------------------
# Routes
# -------------------------
@router.post("/speech-to-text", response_model=SpeechToTextResponse)
async def speech_to_text(payload: SpeechToTextRequest = Body(...)):
    """
    Accepts JSON:
      { "audio_base64": "<...>", "filename": "audio.mp3", "language": "ne" }

    language is REQUIRED: "ne" (Nepali), "si" (Sinhala), or "en" (English)

    Returns:
      { "transcript": "...", "detected_language": "ne" }
    """
    if not payload or not payload.audio_base64:
        raise HTTPException(status_code=400, detail="Send JSON with 'audio_base64' and 'language' fields.")
    
    audio_bytes = _decode_base64_audio_str(payload.audio_base64)
    filename = getattr(payload, "filename", "audio")
    language = getattr(payload, "language", None)
    
    if not language:
        raise HTTPException(status_code=400, detail="'language' field is required. Use 'ne', 'si', or 'en'.")

    res = _run_whisper_transcribe(audio_bytes, filename, language)
    return {"transcript": res["transcript"], "detected_language": res["detected_language"]}


@router.post("/speech-translate", response_model=SpeechTranslateResponse)
async def speech_translate(payload: SpeechTranslateRequest = Body(...)):
    """
    Accepts JSON:
      { "audio_base64": "...", "filename": "audio.mp3", "language": "ne", "target_lang": "en", "return_tts": true }

    language is REQUIRED: "ne" (Nepali), "si" (Sinhala), or "en" (English)
    target_lang: target translation language (default: "en")

    Flow:
      1) STT via Whisper with FIXED language -> transcript
      2) Translate transcript from source language to target_lang
      3) optional TTS synthesis if payload.return_tts==True

    Returns:
      {
        "transcript": "...",
        "detected_language": "ne",
        "translated_text": "..."
      }
    """
    if not payload or not payload.audio_base64:
        raise HTTPException(status_code=400, detail="Send JSON with 'audio_base64' and 'language' fields.")
    
    audio_bytes = _decode_base64_audio_str(payload.audio_base64)
    filename = getattr(payload, "filename", "audio")
    language = getattr(payload, "language", None)
    target_lang = getattr(payload, "target_lang", "en")
    return_tts = getattr(payload, "return_tts", False) if hasattr(payload, "return_tts") else False
    
    if not language:
        raise HTTPException(status_code=400, detail="'language' field is required. Use 'ne', 'si', or 'en'.")

    # Transcribe with FIXED language (not auto-detect)
    stt_res = _run_whisper_transcribe(audio_bytes, filename, language)
    transcript = stt_res["transcript"]
    detected_lang = stt_res["detected_language"]

    # Translate
    if getattr(state, "model_bundle", None) is None:
        raise HTTPException(status_code=503, detail="Translation model not loaded.")

    try:
        translated_text = translate_with_model(state.model_bundle, transcript, detected_lang, target_lang)
    except TypeError:
        translated_text = translate_with_model(state.model_bundle, transcript, detected_lang)
    except Exception as e:
        logger.exception("Translation error: %s", e)
        raise HTTPException(status_code=500, detail=f"Translation failed: {e}")

    response_payload: Dict[str, Any] = {
        "transcript": transcript,
        "detected_language": detected_lang,
        "translated_text": translated_text
    }

    # Optional TTS
    if return_tts:
        if not tts_available:
            logger.warning("TTS requested but tts helper not installed.")
        else:
            try:
                tts_path = synthesize_text_to_wav(translated_text)
                response_payload["tts_audio_path"] = tts_path
            except Exception as e:
                logger.exception("TTS synthesis failed: %s", e)
                response_payload["tts_error"] = str(e)

    return response_payload
