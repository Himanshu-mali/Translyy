

# app/main.py
"""
Multilingual Translation + OCR + Speech-to-Text + Chatbot API
Services: Translation, OCR, Speech Recognition, Ollama Chatbot
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import setup_ffmpeg, setup_pydub
from app.startup import initialize, cleanup
from app.routers.translate import router as translate_router
from app.routers.ocr import router as ocr_router
from app.routers.speech import router as speech_router
from app.routers.chatbot import router as chatbot_router

# Initialize FastAPI application
app = FastAPI(
    title="Multilingual Translation + OCR + Speech + Chatbot",
    version="1.0.0",
    description="Translation, OCR, speech-to-text, and chatbot services"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for frontend."""
    return {"status": "ok", "message": "Backend is running"}

# Register routers
app.include_router(translate_router)
app.include_router(ocr_router)
app.include_router(speech_router)
app.include_router(chatbot_router)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    setup_ffmpeg()
    setup_pydub()
    initialize()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    cleanup()
