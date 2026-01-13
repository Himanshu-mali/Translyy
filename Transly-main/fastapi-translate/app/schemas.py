# app/schemas.py
from typing import Optional, Literal
from pydantic import BaseModel


# ------------------------------------------------------------
# TRANSLATION SCHEMAS
# ------------------------------------------------------------

class TranslateRequest(BaseModel):
    text: str
    source_lang: Optional[str] = None  # "ne", "si", "en", or None
    target_lang: Optional[str] = "en"  # default to English


class TranslateResponse(BaseModel):
    translated_text: str


# ------------------------------------------------------------
# OCR SCHEMAS
# ------------------------------------------------------------

class OCRRequest(BaseModel):
    image_base64: str
    source_lang: Optional[str] = "ne"


class OCRResponse(BaseModel):
    detected_script: str
    detected_language: str
    extracted_text: str
    translated_text: Optional[str] = None


# ------------------------------------------------------------
# SPEECH — BASE MODELS
# ------------------------------------------------------------

class SpeechBase(BaseModel):
    audio_base64: Optional[str] = None
    language: Literal["ne", "si", "en"]      # REQUIRED: "ne" (Nepali), "si" (Sinhala), "en" (English)
    filename: Optional[str] = None           # e.g., "audio.mp3"
    return_tts: bool = False                 # true = generate English speech output


# ---------------------
# SPEECH-TO-TEXT
# ---------------------

class SpeechToTextRequest(SpeechBase):
    """
    Accepts:
    {
        "audio_base64": "...",
        "language": "ne" | "si" | "en",
        "filename": "my.m4a"
    }
    """
    pass


class SpeechToTextResponse(BaseModel):
    transcript: str
    detected_language: str


# ---------------------
# SPEECH-TRANSLATE
# ---------------------

class SpeechTranslateRequest(SpeechBase):
    """
    Accepts:
    {
        "audio_base64": "...",
        "language": "ne" | "si" | "en",
        "filename": "rec.m4a",
        "target_lang": "en",
        "return_tts": true
    }
    """
    target_lang: str = "en"   # output language


class SpeechTranslateResponse(SpeechToTextResponse):
    translated_text: str
    tts_audio_path: Optional[str] = None     # server temp file path
    tts_error: Optional[str] = None          # if TTS fails, but translation succeeds


# =========================================================
# CHATBOT SCHEMAS (Ollama-based)
# =========================================================

class ChatbotRequest(BaseModel):
    message: str
    mode: Literal["history_culture", "travel", "summarize", "sentiment", "general"] = "general"
    language: Literal["auto", "en", "ne", "si"] = "auto"


class ChatbotResponse(BaseModel):
    reply: str
    reply_language: str
    reply_language_label: str
    mode: str


class FAQItem(BaseModel):
    question: str
    answer: str


class FAQResponse(BaseModel):
    items: list[FAQItem]
