# Connecting Chatbot to Frontend - Complete Guide

## Quick Start

Your chatbot API is ready at: `http://localhost:8000/chatbot/chat`

### Step 1: Start the Backend Server

```bash
cd "C:\Users\deepu\Downloads\fastapi-translate (2)\fastapi-translate"
python -m uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Test the API (Before Frontend)

**Using PowerShell:**
```powershell
$body = @{
    message = "Who is the Prime Minister of Nepal?"
    mode = "general"
    language = "en"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:8000/chatbot/chat" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body

$response.Content | ConvertFrom-Json | Format-List
```

**Expected Response:**
```json
{
  "reply": "The Prime Minister of Nepal is Prachanda.",
  "reply_language": "en",
  "reply_language_label": "English",
  "mode": "general"
}
```

---

## Frontend Integration Options

### Option A: HTML + JavaScript (Simplest)

**File: `frontend.html`**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Chatbot</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; }
        #chat-container { border: 1px solid #ddd; padding: 20px; height: 400px; overflow-y: auto; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user { background-color: #e3f2fd; text-align: right; }
        .bot { background-color: #f5f5f5; }
        #input-container { margin-top: 20px; display: flex; gap: 10px; }
        input { flex: 1; padding: 10px; border: 1px solid #ddd; }
        button { padding: 10px 20px; background-color: #2196F3; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Chatbot</h1>
    
    <div id="chat-container"></div>
    
    <div id="input-container">
        <input type="text" id="message-input" placeholder="Type your message..." />
        <select id="mode-select">
            <option value="general">General</option>
            <option value="qa">Q&A</option>
            <option value="travel">Travel</option>
            <option value="summarize">Summarize</option>
            <option value="sentiment">Sentiment</option>
        </select>
        <select id="language-select">
            <option value="en">English</option>
            <option value="ne">Nepali</option>
            <option value="si">Sinhala</option>
            <option value="auto">Auto</option>
        </select>
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        const API_URL = "http://localhost:8000/chatbot/chat";
        const chatContainer = document.getElementById("chat-container");

        async function sendMessage() {
            const message = document.getElementById("message-input").value;
            const mode = document.getElementById("mode-select").value;
            const language = document.getElementById("language-select").value;

            if (!message.trim()) return;

            // Display user message
            addMessage(message, "user");
            document.getElementById("message-input").value = "";

            try {
                // Send to backend
                const response = await fetch(API_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        message: message,
                        mode: mode,
                        language: language
                    })
                });

                const data = await response.json();
                
                // Display bot response
                addMessage(data.reply, "bot");
            } catch (error) {
                addMessage("Error: " + error.message, "bot");
            }
        }

        function addMessage(text, sender) {
            const div = document.createElement("div");
            div.className = "message " + sender;
            div.textContent = text;
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Send on Enter key
        document.getElementById("message-input").addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendMessage();
        });
    </script>
</body>
</html>
```

**Usage:**
1. Save as `frontend.html`
2. Open in web browser
3. Start typing messages

---

### Option B: React (Modern)

**File: `ChatbotComponent.jsx`**
```jsx
import React, { useState } from 'react';

export default function ChatbotComponent() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [mode, setMode] = useState("general");
    const [language, setLanguage] = useState("en");
    const [loading, setLoading] = useState(false);

    const API_URL = "http://localhost:8000/chatbot/chat";

    const sendMessage = async () => {
        if (!input.trim()) return;

        // Add user message
        setMessages(prev => [...prev, { text: input, sender: "user" }]);
        setInput("");
        setLoading(true);

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: input,
                    mode: mode,
                    language: language
                })
            });

            const data = await response.json();
            setMessages(prev => [...prev, { text: data.reply, sender: "bot" }]);
        } catch (error) {
            setMessages(prev => [...prev, { text: "Error: " + error.message, sender: "bot" }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: "800px", margin: "50px auto" }}>
            <h1>Chatbot</h1>
            
            <div style={{
                border: "1px solid #ddd",
                padding: "20px",
                height: "400px",
                overflowY: "auto",
                marginBottom: "20px"
            }}>
                {messages.map((msg, idx) => (
                    <div key={idx} style={{
                        margin: "10px 0",
                        padding: "10px",
                        backgroundColor: msg.sender === "user" ? "#e3f2fd" : "#f5f5f5",
                        textAlign: msg.sender === "user" ? "right" : "left",
                        borderRadius: "5px"
                    }}>
                        {msg.text}
                    </div>
                ))}
            </div>

            <div style={{ display: "flex", gap: "10px" }}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && sendMessage()}
                    placeholder="Type your message..."
                    style={{ flex: 1, padding: "10px", border: "1px solid #ddd" }}
                    disabled={loading}
                />
                <select value={mode} onChange={(e) => setMode(e.target.value)} style={{ padding: "10px" }}>
                    <option value="general">General</option>
                    <option value="qa">Q&A</option>
                    <option value="travel">Travel</option>
                </select>
                <select value={language} onChange={(e) => setLanguage(e.target.value)} style={{ padding: "10px" }}>
                    <option value="en">English</option>
                    <option value="ne">Nepali</option>
                    <option value="si">Sinhala</option>
                </select>
                <button onClick={sendMessage} disabled={loading} style={{
                    padding: "10px 20px",
                    backgroundColor: "#2196F3",
                    color: "white",
                    border: "none",
                    cursor: "pointer"
                }}>
                    {loading ? "..." : "Send"}
                </button>
            </div>
        </div>
    );
}
```

---

### Option C: Vue.js

**File: `ChatbotComponent.vue`**
```vue
<template>
    <div class="chatbot">
        <h1>Chatbot</h1>
        
        <div class="chat-container">
            <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.sender]">
                {{ msg.text }}
            </div>
        </div>

        <div class="input-container">
            <input
                v-model="input"
                @keyup.enter="sendMessage"
                placeholder="Type your message..."
                :disabled="loading"
            />
            <select v-model="mode">
                <option value="general">General</option>
                <option value="qa">Q&A</option>
                <option value="travel">Travel</option>
            </select>
            <select v-model="language">
                <option value="en">English</option>
                <option value="ne">Nepali</option>
                <option value="si">Sinhala</option>
            </select>
            <button @click="sendMessage" :disabled="loading">
                {{ loading ? "..." : "Send" }}
            </button>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            messages: [],
            input: "",
            mode: "general",
            language: "en",
            loading: false,
            apiUrl: "http://localhost:8000/chatbot/chat"
        };
    },
    methods: {
        async sendMessage() {
            if (!this.input.trim()) return;

            this.messages.push({ text: this.input, sender: "user" });
            const msg = this.input;
            this.input = "";
            this.loading = true;

            try {
                const response = await fetch(this.apiUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        message: msg,
                        mode: this.mode,
                        language: this.language
                    })
                });

                const data = await response.json();
                this.messages.push({ text: data.reply, sender: "bot" });
            } catch (error) {
                this.messages.push({ text: "Error: " + error.message, sender: "bot" });
            } finally {
                this.loading = false;
            }
        }
    }
};
</script>

<style scoped>
.chatbot { max-width: 800px; margin: 50px auto; }
.chat-container { border: 1px solid #ddd; padding: 20px; height: 400px; overflow-y: auto; margin-bottom: 20px; }
.message { margin: 10px 0; padding: 10px; border-radius: 5px; }
.user { background-color: #e3f2fd; text-align: right; }
.bot { background-color: #f5f5f5; }
.input-container { display: flex; gap: 10px; }
input, select { padding: 10px; border: 1px solid #ddd; }
button { padding: 10px 20px; background-color: #2196F3; color: white; border: none; cursor: pointer; }
</style>
```

---

## API Reference

### Endpoint: POST `/chatbot/chat`

**URL:** `http://localhost:8000/chatbot/chat`

**Request:**
```json
{
    "message": "Who is the Prime Minister of Nepal?",
    "mode": "general",
    "language": "en"
}
```

**Parameters:**

| Parameter | Type | Options | Default |
|-----------|------|---------|---------|
| `message` | string | Any text | Required |
| `mode` | string | `general`, `qa`, `travel`, `summarize`, `sentiment` | `general` |
| `language` | string | `en`, `ne`, `si`, `auto` | `auto` |

**Response:**
```json
{
    "reply": "The Prime Minister of Nepal is Prachanda.",
    "reply_language": "en",
    "reply_language_label": "English",
    "mode": "general"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `reply` | string | The chatbot's response |
| `reply_language` | string | Detected response language |
| `reply_language_label` | string | Human-readable language name |
| `mode` | string | The mode used for the request |

---

## Error Handling

### Status Code: 400 - Bad Request
```json
{ "detail": "Message cannot be empty" }
```

### Status Code: 500 - Server Error
```json
{ "detail": "Chatbot error: [error details]" }
```

**Handle in frontend:**
```javascript
if (!response.ok) {
    const error = await response.json();
    console.error("Error:", error.detail);
}
```

---

## CORS Configuration (If Needed)

If your frontend is on a different domain, add CORS to `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## FAQ Endpoint (Optional)

You can also get the FAQ list:

**Endpoint:** GET `/chatbot/faq`

**Response:**
```json
{
    "items": [
        {
            "question": "What is the capital of Nepal?",
            "answer": "The capital city of Nepal is Kathmandu..."
        },
        ...
    ]
}
```

---

## Example Requests

### 1. Simple Chat
```javascript
fetch('http://localhost:8000/chatbot/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: 'Hello',
        mode: 'general',
        language: 'en'
    })
});
```

### 2. Travel Mode
```javascript
fetch('http://localhost:8000/chatbot/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: 'Where can I stay in Kathmandu?',
        mode: 'travel',
        language: 'en'
    })
});
```

### 3. Nepali Input
```javascript
fetch('http://localhost:8000/chatbot/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: 'नेपाल को पीएम कौन है?',
        mode: 'general',
        language: 'ne'
    })
});
```

### 4. Auto-detect Language
```javascript
fetch('http://localhost:8000/chatbot/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: 'What is the capital?',
        mode: 'general',
        language: 'auto'
    })
});
```

---

## Testing Tools

### Using curl
```bash
curl -X POST "http://localhost:8000/chatbot/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Who is PM?","mode":"general","language":"en"}'
```

### Using Postman
1. Create new POST request
2. URL: `http://localhost:8000/chatbot/chat`
3. Headers: `Content-Type: application/json`
4. Body (raw):
```json
{
    "message": "Who is the Prime Minister of Nepal?",
    "mode": "general",
    "language": "en"
}
```

---

## Running Both Backend & Frontend

### Terminal 1: Backend
```bash
cd "C:\Users\deepu\Downloads\fastapi-translate (2)\fastapi-translate"
python -m uvicorn app.main:app --reload
# Server running on http://localhost:8000
```

### Terminal 2: Frontend (if React/Vue)
```bash
npm start
# Frontend running on http://localhost:3000 (React) or http://localhost:8080 (Vue)
```

### Access Frontend
Open browser: `http://localhost:3000` or `http://localhost:8080`

---

## Troubleshooting

### Issue: CORS Error
**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:** Add CORS middleware (see CORS Configuration section above)

### Issue: Connection Refused
**Error:** `Failed to fetch`

**Solution:** Verify backend is running
```bash
# Check if server is running
curl http://localhost:8000/docs
```

### Issue: Empty Response
**Error:** Response is null or undefined

**Solution:** Check response status code
```javascript
if (!response.ok) {
    console.error("HTTP Error:", response.status);
}
```

### Issue: Slow Response
**Cause:** Model loading time on first request

**Solution:** Models warm up after first request, subsequent requests are faster

---

## Summary

✅ Your chatbot API is ready at: `http://localhost:8000/chatbot/chat`
✅ Use any of the frontend options above
✅ Test with provided examples
✅ Deploy to production when ready

**Next Steps:**
1. Choose a frontend framework (HTML/React/Vue)
2. Implement using provided code
3. Start backend server
4. Test chatbot functionality
5. Deploy frontend separately
