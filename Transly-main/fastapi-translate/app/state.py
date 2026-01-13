from typing import Optional

# Shared state for the FastAPI app
model_bundle: Optional[dict] = None
whisper_model = None  # Speech recognition model
qa_model_bundle: Optional[dict] = None  # Q&A/LLM model bundle

# Note: No longer storing ocr_reader since we use pytesseract directly
