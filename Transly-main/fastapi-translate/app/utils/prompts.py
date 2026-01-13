"""
System prompts for Q&A, Summarization, and Sentiment Analysis tasks.
Optimized for Nepali, Sinhala, and English.
"""

SYSTEM_PROMPTS = {
    "qa_nepali": """तपाइँ एक सहायक हुनुहुन्छ जो नेपाली सांस्कृतिक विरासत र पर्यटन बारे प्रश्नको उत्तर दिन्छ।
सरल, स्पष्ट र सटीक उत्तर प्रदान गर्नुहोस्। नेपाली परम्परा, इतिहास र आकर्षणहरु बारे विशेषज्ञ जानकारी दिनुहोस्।""",
    
    "qa_sinhala": """ඔබ සිංහල සांස्कृතिक උරුම සහ සංචාරක තොරතුරු සිටින ඉලක්කම් ප්‍රශ්නවලට පිළිතුරු දෙන සහාය වේ.
සරල, පැහැදිලි සහ නිවැරදි පිළිතුරු ලබා දෙන්න. ශ්‍රී ලංකා සම්ප්‍රදාය, ඉතිහාසය සහ ආකර්ශණ පිළිබඳ විශේෂඥ තොරතුරු ලබා දෙන්න.""",
    
    "qa_english": """You are a helpful assistant answering questions about Nepali and Sinhala cultural heritage and tourism.
Provide clear, accurate, and concise answers about traditions, history, and attractions.""",
    
    "summarize_nepali": """निम्नलिखित पाठ को नेपालीमा सारांश गर्नुहोस्। मुख्य बिंदु को छोटो रुप मा व्यक्त गर्नुहोस्।""",
    
    "summarize_sinhala": """පහත ඔබ පෙළ සිංහල භාෂාවෙන් සාරාංශ කරන්න. ප්‍රධාන කරුණු කෙටි ස්වරූපයෙන් ප්‍රකාශ කරන්න.""",
    
    "summarize_english": """Summarize the following text concisely. Extract main points and express them briefly.""",
    
    "sentiment_nepali": """निम्नलिखित पाठको भावनात्मक स्थिति विश्लेषण गर्नुहोस्। यो सकारात्मक, नकारात्मक वा तटस्थ हो भनी बताउनुहोस्।""",
    
    "sentiment_sinhala": """පහත ඔබ පෙළේ බවිතයි විශ්ලේෂණය කරන්න. එය ධනාත්මක, ඍණාත්මක හෝ තුලනික දැයි කියන්න.""",
    
    "sentiment_english": """Analyze the sentiment of the following text. Determine if it is positive, negative, or neutral.""",
}


def get_qa_prompt(question: str, context: str = None, language: str = "en") -> str:
    """Build Q&A prompt with optional context."""
    system = SYSTEM_PROMPTS.get(f"qa_{language}", SYSTEM_PROMPTS["qa_english"])
    
    if context:
        return f"{system}\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    return f"{system}\n\nQuestion: {question}\n\nAnswer:"


def get_summarize_prompt(text: str, language: str = "en") -> str:
    """Build summarization prompt."""
    system = SYSTEM_PROMPTS.get(f"summarize_{language}", SYSTEM_PROMPTS["summarize_english"])
    return f"{system}\n\nText:\n{text}\n\nSummary:"


def get_sentiment_prompt(text: str, language: str = "en") -> str:
    """Build sentiment analysis prompt."""
    system = SYSTEM_PROMPTS.get(f"sentiment_{language}", SYSTEM_PROMPTS["sentiment_english"])
    return f"{system}\n\nText: {text}\n\nSentiment:"
