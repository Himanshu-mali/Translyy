# app/routers/chatbot.py
"""
Chatbot endpoint using local Ollama models.
Supports history, culture, travel, summarization, sentiment analysis, and general chat.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Body
import traceback

from app.schemas import ChatbotRequest, ChatbotResponse, FAQItem, FAQResponse
from app.utils.chatbot_utils import (
    detect_language,
    build_system_prompt,
    choose_model,
    call_ollama,
    get_faq_items,
    LANG_LABELS,
)

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


@router.get("/faq", response_model=FAQResponse)
async def get_faq():
    """
    Get the FAQ list for Nepal and Sri Lanka.
    
    Returns:
        FAQResponse with list of FAQ items
    """
    try:
        items = get_faq_items()
        return FAQResponse(items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get FAQ: {e}")


@router.post("/chat", response_model=ChatbotResponse)
async def chat(payload: ChatbotRequest = Body(...)):
    """
    Chat endpoint using local Ollama models.
    
    Request:
    {
        "message": "What is the capital of Nepal?",
        "mode": "history_culture",
        "language": "en"
    }
    
    Modes:
    - history_culture: Focus on history, culture, and heritage
    - travel: Travel tips and tourism information
    - summarize: Summarize text passages
    - sentiment: Analyze sentiment of text
    - general: General questions and chat
    
    Languages:
    - auto: Auto-detect user language and respond in same
    - en: English
    - ne: Nepali
    - si: Sinhala
    
    Response:
    {
        "reply": "Kathmandu is the capital of Nepal...",
        "reply_language": "en",
        "reply_language_label": "English",
        "mode": "history_culture"
    }
    """
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Get mode and language
        mode = (payload.mode or "general").lower()
        language = (payload.language or "auto").lower()
        message = payload.message.strip()
        
        # Choose which Ollama model to use
        model_name = choose_model(mode)
        
        # Build system prompt for the mode and language
        system_prompt = build_system_prompt(mode, language)
        
        # Call Ollama with the prompt and message
        reply_text = call_ollama(model_name, system_prompt, message)
        
        # Detect language of the reply
        detected_lang = detect_language(reply_text)
        
        # If user requested a specific language, use that
        if language != "auto" and language in LANG_LABELS:
            detected_lang = language
        
        return ChatbotResponse(
            reply=reply_text,
            reply_language=detected_lang,
            reply_language_label=LANG_LABELS.get(detected_lang, "English"),
            mode=mode,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Chatbot error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")


@router.post("/chat-stream")
async def chat_stream(payload: ChatbotRequest = Body(...)):
    """
    Streaming chat endpoint (returns Server-Sent Events).
    Useful for real-time responses.
    
    Note: Requires async streaming implementation
    """
    # TODO: Implement streaming with Server-Sent Events
    raise HTTPException(status_code=501, detail="Streaming not yet implemented")
