# 🚀 FastAPI Multi-Service Backend

**A fully-featured, offline-capable FastAPI backend with Translation, Speech-to-Text, OCR, and AI-powered Chatbot.**

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Architecture](#-architecture)
3. [Endpoints](#-endpoints)
4. [Installation & Setup](#-installation--setup)
5. [API Documentation](#-api-documentation)
6. [Configuration](#-configuration)
7. [Deployment](#-deployment)
8. [Troubleshooting](#-troubleshooting)

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Windows / macOS / Linux
- 8GB+ RAM
- 10GB+ disk space (for models)

### 1️⃣ Install & Run

```powershell
# Navigate to project
cd "C:\Users\deepu\Downloads\fastapi-translate (2)\fastapi-translate"

# Create virtual environment (if needed)
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Server runs at:** `http://localhost:8000`

### 2️⃣ Test an Endpoint

```bash
curl -X POST http://localhost:8000/translate-text \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello","source_lang":"en","target_lang":"ne"}'
```

### 3️⃣ View API Docs

- **Interactive Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React/Vue)                    │
│                    (Separate Repository)                     │
└────────────┬────────────────────────────────────────────────┘
             │ HTTP/CORS
             ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (8000)                   │
├─────────────────────────────────────────────────────────────┤
│ Routes:                                                       │
│ • /health                   ← Health check                   │
│ • /translate-text           ← Translation (NLLB-200)        │
│ • /ocr-*                    ← OCR (Tesseract + NLLB)        │
│ • /speech-*                 ← Speech (Whisper)              │
│ • /chatbot/*                ← Chatbot (Ollama)              │
├─────────────────────────────────────────────────────────────┤
│ Models Loaded:                                                │
│ • Translation: NLLB-200 (~1.2 GB) ✓ Loaded                  │
│ • OCR: Tesseract (~1 GB) ✓ Loaded                           │
│ • Speech: Whisper Medium (~1.5 GB) ✓ Loaded                 │
│ • Chatbot: Ollama (requires external service)               │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
        ┌─────────────┐
        │   Ollama    │  (localhost:11434)
        │  Service    │  • gemma:2b
        │  (External) │  • qwen2:1.5b
        └─────────────┘
```

### File Structure

```
fastapi-translate/
├── app/
│   ├── main.py                  ← FastAPI app initialization
│   ├── model.py                 ← Model loaders
│   ├── schemas.py               ← Request/response models
│   ├── state.py                 ← Global state management
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── translate.py         ← Translation endpoints
│   │   ├── ocr.py               ← OCR endpoints
│   │   ├── speech.py            ← Speech endpoints
│   │   └── chatbot.py           ← Chatbot endpoints (Ollama)
│   └── utils/
│       ├── __init__.py
│       ├── prompts.py           ← System prompts (multilingual)
│       └── chatbot_utils.py     ← Chatbot utilities
├── requirements.txt             ← Python dependencies
├── README.md                    ← This file
├── ENDPOINT_REFERENCE.md        ← Quick endpoint reference
├── CHATBOT_INTEGRATION.md       ← Chatbot setup guide
└── CHATBOT_INTEGRATION_SUMMARY.md ← Chatbot summary
```

---

## 🔌 Endpoints

### Overview

| Endpoint | Method | Purpose | Model | Status |
|----------|--------|---------|-------|--------|
| `/health` | GET | Health check | - | ✅ Active |
| `/translate-text` | POST | Translate text | NLLB-200 | ✅ Active |
| `/ocr-image` | POST | Extract text from image | Tesseract | ✅ Active |
| `/ocr-pdf` | POST | Extract text from PDF | Tesseract | ✅ Active |
| `/speech-to-text` | POST | Transcribe audio | Whisper | ✅ Active |
| `/speech-translate` | POST | Transcribe + translate | Whisper + NLLB | ✅ Active |
| `/chatbot/faq` | GET | Get FAQ items | - | ✅ Active |
| `/chatbot/chat` | POST | Chat with AI | Ollama | ✅ Active |

---

## 🛠️ Installation & Setup

### Step 1: Clone & Setup

```bash
cd C:\Users\deepu\Downloads\fastapi-translate\ 2\fastapi-translate

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Install Tesseract (Required for OCR)

**Windows:**
```powershell
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use Chocolatey:
choco install tesseract

# Set environment variable
[Environment]::SetEnvironmentVariable('TESSERACT_CMD', 'C:\Program Files\Tesseract-OCR\tesseract.exe', 'User')
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Step 3: Install Ollama (Required for Chatbot)

Download from: https://ollama.com/download

**After installation:**
```bash
# Pull required models
ollama pull gemma:2b
ollama pull qwen2:1.5b

# Start Ollama service (should run automatically on port 11434)
ollama serve
```

### Step 4: Start Backend Server

```bash
cd "C:\Users\deepu\Downloads\fastapi-translate (2)\fastapi-translate"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
[STARTUP] Loading translation model...
✓ Translation model loaded: facebook/nllb-200-distilled-600M
✓ Tesseract version: 5.5.0.20241111
[STARTUP] All models loaded successfully!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 📚 API Documentation

### 1️⃣ Translation Endpoint

**Endpoint:** `POST /translate-text`

**Description:** Translate text between 200+ languages using NLLB-200 model

**Request:**
```json
{
  "text": "Hello, how are you?",
  "source_lang": "en",
  "target_lang": "ne"
}
```

**Response:**
```json
{
  "translated_text": "नमस्ते, तिमी कसरी छौ?"
}
```

**Supported Languages:**
- Nepali (`ne`), Sinhala (`si`), English (`en`), Hindi, Chinese, Spanish, French, German, Arabic, Portuguese, Japanese, and 190+ others

**curl Example:**
```bash
curl -X POST http://localhost:8000/translate-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "नेपाल",
    "source_lang": "ne",
    "target_lang": "en"
  }'
```

---

### 2️⃣ OCR - Image Endpoint

**Endpoint:** `POST /ocr-image`

**Description:** Extract text from images using Tesseract OCR

**Request:**
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
  "source_lang": "ne"
}
```

**Response:**
```json
{
  "detected_script": "Devanagari",
  "detected_language": "ne",
  "extracted_text": "नेपालको राजधानी काठमाडौँ हो।",
  "translated_text": "The capital of Nepal is Kathmandu."
}
```

**Supported Languages:** All Tesseract-supported languages (English, Nepali, Sinhala, Hindi, Arabic, Chinese, Japanese, etc.)

---

### 3️⃣ OCR - PDF Endpoint

**Endpoint:** `POST /ocr-pdf`

**Description:** Extract text from PDF files

**Request:**
```json
{
  "pdf_base64": "JVBERi0xLjQK..."
}
```

**Response:**
```json
{
  "extracted_text": "Page 1: ...\nPage 2: ..."
}
```

---

### 4️⃣ Speech-to-Text Endpoint

**Endpoint:** `POST /speech-to-text`

**Description:** Transcribe audio files using Whisper

**Request:**
```json
{
  "audio_base64": "//NExAA...",
  "language": "ne",
  "filename": "audio.mp3"
}
```

**Response:**
```json
{
  "transcript": "नेपाल एक सुन्दर देश हो।",
  "detected_language": "ne"
}
```

**Supported Formats:** MP3, WAV, M4A, FLAC, OGG, OPUS
**Supported Languages:** 99 languages including Nepali, Sinhala, English, Hindi, Arabic, Chinese, Japanese, etc.

---

### 5️⃣ Speech-Translate Endpoint

**Endpoint:** `POST /speech-translate`

**Description:** Transcribe audio and translate to target language

**Request:**
```json
{
  "audio_base64": "//NExAA...",
  "language": "ne",
  "target_lang": "en",
  "filename": "nepali_audio.mp3"
}
```

**Response:**
```json
{
  "transcript": "नेपाल एक सुन्दर देश हो।",
  "detected_language": "ne",
  "translated_text": "Nepal is a beautiful country.",
  "tts_audio_path": "/tmp/response_audio.mp3"
}
```

---

### 6️⃣ Chatbot - FAQ Endpoint

**Endpoint:** `GET /chatbot/faq`

**Description:** Get list of pre-built FAQ items

**Request:**
```
GET http://localhost:8000/chatbot/faq
```

**Response:**
```json
{
  "items": [
    {
      "question": "What is the capital of Nepal?",
      "answer": "Kathmandu is the capital of Nepal..."
    },
    {
      "question": "What is the capital of Sri Lanka?",
      "answer": "Sri Jayawardenepura Kotte is the administrative capital..."
    }
  ]
}
```

**Number of FAQs:** 24 pre-built items

---

### 7️⃣ Chatbot - Chat Endpoint

**Endpoint:** `POST /chatbot/chat`

**Description:** Chat with AI-powered chatbot (Ollama-based)

**Request:**
```json
{
  "message": "Tell me about Nepal",
  "mode": "history_culture",
  "language": "en"
}
```

**Response:**
```json
{
  "reply": "Nepal is a country rich in history and culture...",
  "reply_language": "en",
  "reply_language_label": "English",
  "mode": "history_culture"
}
```

**Available Modes:**
- `history_culture` - Focus on history, heritage, and culture (uses gemma:2b)
- `travel` - Travel tips and tourism information (uses gemma:2b)
- `summarize` - Text summarization (uses qwen2:1.5b)
- `sentiment` - Sentiment analysis (uses qwen2:1.5b)
- `general` - General questions and chat (uses qwen2:1.5b)

**Supported Languages:**
- `auto` - Auto-detect user language and respond in same
- `en` - English
- `ne` - Nepali
- `si` - Sinhala

**curl Example:**
```bash
curl -X POST http://localhost:8000/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Kathmandu?",
    "mode": "travel",
    "language": "en"
  }'
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Server
HOST=0.0.0.0
PORT=8000

# Ollama
OLLAMA_HOST=http://localhost:11434

# Models
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Logging
LOG_LEVEL=INFO
```

### Model Configuration

**app/model.py:**
```python
MODEL_NAME = "facebook/nllb-200-distilled-600M"
MAX_GEN_LENGTH = 128
NUM_BEAMS = 4
EARLY_STOPPING = True
```

**app/utils/chatbot_utils.py:**
```python
OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "qwen2:1.5b"
FACTUAL_MODEL = "gemma:2b"
```

---

## 🚀 Deployment

### Development

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build & Run:**
```bash
docker build -t fastapi-backend .
docker run -p 8000:8000 fastapi-backend
```

---

## 🔍 Troubleshooting

### Issue: 500 Error on Chat Endpoint

**Cause:** Ollama service not running or models not found

**Solution:**
```bash
# Check Ollama status
ollama list

# Pull missing models
ollama pull gemma:2b
ollama pull qwen2:1.5b

# Restart Ollama service
ollama serve
```

### Issue: Out of Memory

**Cause:** Running too many models simultaneously

**Solution:**
- Minimum 8GB RAM required
- Close other applications
- Reduce model complexity if needed

### Issue: Tesseract Not Found

**Cause:** Tesseract not installed or path incorrect

**Solution:**
```powershell
# Install Tesseract
choco install tesseract

# Set path
[Environment]::SetEnvironmentVariable('TESSERACT_CMD', 'C:\Program Files\Tesseract-OCR\tesseract.exe', 'User')

# Restart terminal and server
```

### Issue: Slow Speech-to-Text

**Cause:** Normal behavior for CPU-based processing

**Solution:**
- First request processes the model, subsequent requests are cached
- Consider using GPU if available
- Expected times: 30-60 seconds for audio processing

### Issue: CORS Errors in Frontend

**Solution:** Backend already has CORS enabled. Check:
1. Frontend URL matches CORS whitelist
2. Correct HTTP method (POST for translate, GET for health)
3. Content-Type header is `application/json`

---

## 📊 Performance

### Response Times (Approximate)

| Endpoint | First Run | Cached Run | Notes |
|----------|-----------|-----------|-------|
| `/health` | 1ms | 1ms | Instant |
| `/translate-text` | 3-5s | 1-2s | Text processing |
| `/ocr-image` | 5-10s | 5-10s | Image size dependent |
| `/speech-to-text` | 30-60s | 30-60s | Audio length dependent |
| `/chatbot/chat` | 5-10s | 2-5s | Text generation |

### Memory Usage

| Component | Size |
|-----------|------|
| Translation (NLLB-200) | ~1.2 GB |
| OCR (Tesseract) | ~1 GB |
| Speech (Whisper) | ~1.5 GB |
| **Total** | **~3.7 GB** |

*Note: Ollama runs as external service with its own memory*

---

## 📝 Notes

- ✅ All features work **completely offline** after first run
- ✅ Models are cached locally after download
- ✅ CORS enabled for frontend integration
- ✅ Multilingual support (200+ languages for translation, 99 for speech)
- ✅ Fully REST API compliant
- ⏱️ Response times improve after first request (model caching)

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review API documentation at `/docs`
3. Check server logs for detailed error messages
4. Ensure all prerequisites are installed

---

**Last Updated:** December 2, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
