# app/startup.py
"""Model loading and initialization on startup."""

import app.state as state
from app.model import load_model

def load_translation_model():
    """Load the translation model."""
    try:
        print("[STARTUP] Loading translation model...")
        state.model_bundle = load_model()
        model_name = state.model_bundle.get("name") if state.model_bundle else None
        print(f"✓ Translation model loaded: {model_name}")
    except Exception as e:
        state.model_bundle = None
        print(f"✗ Translation model failed: {type(e).__name__}")

def check_tesseract():
    """Check Tesseract OCR availability."""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract available: {version}")
    except Exception as e:
        print(f"ℹ Tesseract not available: {type(e).__name__}")

def load_whisper_model():
    """Load Whisper speech-to-text model."""
    try:
        import whisper
        print("[STARTUP] Loading Whisper model...")
        state.whisper_model = whisper.load_model("medium")
        print("✓ Whisper model loaded (medium)")
    except ImportError:
        print("ℹ Whisper not installed (optional)")
        state.whisper_model = None
    except Exception as e:
        print(f"ℹ Whisper skipped: {type(e).__name__}")
        state.whisper_model = None

def initialize():
    """Run all startup initialization."""
    print("\n[STARTUP] Initializing services...\n")
    load_translation_model()
    check_tesseract()
    load_whisper_model()
    print("\n[STARTUP] All services initialized!\n")

def cleanup():
    """Cleanup on shutdown."""
    try:
        if state.model_bundle:
            state.model_bundle = None
    except:
        pass
