# app/utils/chatbot_utils.py
"""
Utility functions for Ollama-based chatbot.
Includes language detection, prompt building, model selection, and Ollama integration.
"""

from typing import List
import ollama

from app.schemas import FAQItem

# Language mapping
LANG_LABELS = {
    "en": "English",
    "ne": "Nepali",
    "si": "Sinhala",
}

# System prompts for different modes and languages
SYSTEM_PROMPTS = {
    "qa_nepali": """नेपाल र श्रीलंका को बारे मा सवाल को सीधा जवाब दिनुहोस्।
तथ्य: नेपाल PM=प्रचण्ड, राजधानी=काठमाडौँ। Sri Lanka Pres=Dissanayake, Capital=Colombo।
यी तथ्य को प्रयोग गर्नु MUST। सामान्य अभिवादन गर्नुस्नु।""",
    
    "qa_sinhala": """සෙවින පිළිතුරු දෙන්න. කිසිවිට සාමාන්‍ය ප්‍රශ්නයක් ඉතිරි කරන්න.
නේපාල PM=ප්‍රචණ්ඩ, ප්‍රධාන නගරය=කටුමාඩු, මුද්‍රා=NPR.
ශ්‍රී ලංකා Pres=ධිසනායක, ප්‍රධාන නගරය=කොළඹ.
ප්‍රශ්නයට සෙවින පිළිතුරු දෙන්න.""",
    
    "qa_english": """Answer questions about Nepal and Sri Lanka using the facts provided.
FACTS: Nepal PM=Prachanda, Capital=Kathmandu, Currency=NPR. Sri Lanka Pres=Dissanayake, Capital=Colombo, Currency=LKR.
MUST use these facts. Answer directly, no generic greetings.""",
    
    "travel_nepali": """यात्रा सल्लाह - यात्रा, होटल, आकर्षण को लागि।
यदि नेपाल/लंका तथ्य सवाल छ भने सीधा जवाफ दिनुहोस्।
PM र राजधानी: नेपाल PM=प्रचण्ड, राजधानी=काठमाडौँ; Sri Lanka Pres=Dissanayake, Capital=Colombo।""",
    
    "travel_sinhala": """ගමනාගමන උපදෙස් - ගමනාගමන, හෝටල්, ස්ථාන පිළිබඳ.
නේපාල/ශ්‍රී ලංකා තථ්‍ය ගැන ඇසුවහොත් සෙවින පිළිතුරු දෙන්න.
PM සහ ප්‍රධාන නගර: නේපාල PM=ප්‍රචණ්ඩ, ප්‍රධාන නගරය=කටුමාඩු; Pres=Dissanayake, Capital=Colombo.""",
    
    "travel_english": """Travel advice for travel, hotels, attractions.
If asked facts about Nepal/Sri Lanka - answer directly, NOT travel advice.
Facts: Nepal PM=Prachanda, Capital=Kathmandu. Sri Lanka Pres=Dissanayake, Capital=Colombo.""",
    
    "summarize_nepali": """निम्नलिखित पाठ को नेपालीमा सारांश गर्नुहोस्। मुख्य बिंदु को छोटो रुप मा व्यक्त गर्नुहोस्।""",
    
    "summarize_sinhala": """පහත ඔබ පෙළ සිංහල භාෂාවෙන් සාරාංශ කරන්න. ප්‍රධාන කරුණු කෙටි ස්වරූපයෙන් ප්‍රකාශ කරන්න.""",
    
    "summarize_english": """Summarize the following text concisely. Extract main points and express them briefly in 3-6 sentences.""",
    
    "sentiment_nepali": """निम्नलिखित पाठको भावनात्मक स्थिति विश्लेषण गर्नुहोस्। यो सकारात्मक, नकारात्मक वा तटस्थ हो भनी बताउनुहोस्।""",
    
    "sentiment_sinhala": """පහත ඔබ පෙළේ බවිතයි විශ්ලේෂණය කරන්න. එය ධනාත්මක, ඍණාත්මක හෝ තුලනික දැයි කියන්න.""",
    
    "sentiment_english": """Analyze the sentiment of the following text. Determine if it is positive, negative, or neutral. 
Output format: 'Sentiment: [Positive/Negative/Neutral]' followed by brief explanation.""",
    
    "general_english": """Answer questions about Nepal and Sri Lanka factually.
FACTS: Nepal PM=Prachanda, Capital=Kathmandu, Currency=NPR. Sri Lanka Pres=Dissanayake, Capital=Colombo, Currency=LKR.
MUST use these facts when asked. Direct answers only.""",
    
    "general_nepali": """नेपाल र श्रीलंका को बारे मा तथ्य आधारित उत्तर दिनुहोस्।
तथ्य: नेपाल PM=प्रचण्ड, राजधानी=काठमाडौँ। Pres=Dissanayake, Capital=Colombo।
सीधा जवाफ, कहिल्यै सामान्य अभिवादन नत।""",
    
    "general_sinhala": """නේපාල සහ ශ්‍රී ලංකා ගැන තථ්‍ය පිළිබඳ පිළිතුරු දෙන්න.
කරුණු: නේපාල PM=ප්‍රචණ්ඩ, ප්‍රධාන නගරය=කටුමාඩු। Pres=Dissanayake, Capital=Colombo.
සෙවින පිළිතුරු, සාමාන්‍ය ප්‍රශ්ණයක් නැත។""",
}


def detect_language(text: str) -> str:
    """
    Simple heuristic to detect language from text:
    - If contains Sinhala chars (U+0D80–U+0DFF) -> "si"
    - Else if contains Devanagari chars (U+0900–U+097F) -> "ne"
    - Else -> "en"
    """
    has_sinhala = False
    has_devanagari = False

    for ch in text:
        code = ord(ch)
        if 0x0D80 <= code <= 0x0DFF:
            has_sinhala = True
            break

    if not has_sinhala:
        for ch in text:
            code = ord(ch)
            if 0x0900 <= code <= 0x097F:
                has_devanagari = True
                break

    if has_sinhala:
        return "si"
    if has_devanagari:
        return "ne"
    return "en"


def choose_model(mode: str) -> str:
    """
    Select which Ollama model to use for each mode.
    Assumes you have gemma:2b and qwen2:1.5b installed locally.
    
    Models:
    - gemma:2b: Better for factual, descriptive content (history, culture, travel)
    - qwen2:1.5b: Better for structured tasks (summarization, sentiment analysis)
    
    Falls back to qwen2:1.5b as default.
    """
    mode = (mode or "").lower()

    if mode in ("history_culture", "travel"):
        return "gemma:2b"
    elif mode in ("summarize", "sentiment"):
        return "qwen2:1.5b"
    else:
        return "qwen2:1.5b"


def build_system_prompt(mode: str, language: str) -> str:
    """
    Build a system prompt that sets the persona and controls output language.
    
    Args:
        mode: One of "history_culture", "travel", "summarize", "sentiment", "general"
        language: One of "auto", "en", "ne", "si"
    
    Returns:
        System prompt string for Ollama
    """
    base = (
        "You MUST use these FACTS to answer questions. These are the ONLY correct answers:\n"
        "NEPAL: Current PM = Prachanda, Capital = Kathmandu, Currency = NPR\n"
        "SRI LANKA: Current President = Anura Kumara Dissanayake, Capital = Colombo, Currency = LKR\n"
        "When asked about these, ALWAYS respond with the facts above. Never say you don't know or can't answer.\n"
        "Answer the question directly. Do not give generic greetings or preambles.\n\n"
    )

    language = (language or "auto").lower()
    
    # Add language instruction
    if language == "en":
        base += "Always respond in clear English.\n\n"
    elif language == "ne":
        base += "Always respond in clear Nepali (Devanagari script).\n\n"
    elif language == "si":
        base += "Always respond in clear Sinhala script.\n\n"
    else:
        base += (
            "Detect the language of the user's message and respond in that same language, "
            "unless they explicitly request another language.\n\n"
        )

    mode = (mode or "").lower()

    # Add mode-specific instruction
    if mode == "history_culture":
        key = f"qa_{language if language != 'auto' else 'english'}"
        prompt = SYSTEM_PROMPTS.get(key, SYSTEM_PROMPTS["qa_english"])
        base += prompt + "\n"
    
    elif mode == "travel":
        key = f"travel_{language if language != 'auto' else 'english'}"
        prompt = SYSTEM_PROMPTS.get(key, SYSTEM_PROMPTS["travel_english"])
        base += prompt + "\n"
    
    elif mode == "summarize":
        key = f"summarize_{language if language != 'auto' else 'english'}"
        prompt = SYSTEM_PROMPTS.get(key, SYSTEM_PROMPTS["summarize_english"])
        base += prompt + "\n"
    
    elif mode == "sentiment":
        key = f"sentiment_{language if language != 'auto' else 'english'}"
        prompt = SYSTEM_PROMPTS.get(key, SYSTEM_PROMPTS["sentiment_english"])
        base += prompt + "\n"
    
    else:  # general
        key = f"general_{language if language != 'auto' else 'english'}"
        prompt = SYSTEM_PROMPTS.get(key, SYSTEM_PROMPTS["general_english"])
        base += prompt + "\n"

    return base


def call_ollama(model: str, system_prompt: str, user_message: str) -> str:
    """
    Call local Ollama instance to generate a response.
    
    Args:
        model: Model name (e.g., "gemma:2b", "qwen2:1.5b")
        system_prompt: System prompt to set context
        user_message: User's message
    
    Returns:
        Model's reply text
    
    Raises:
        Exception: If Ollama is not available or fails
    """
    try:
        result = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            options={"temperature": 0.4},
        )
    except Exception as e:
        raise Exception(f"Ollama service error: {e}. Is Ollama running?")

    try:
        content = result["message"]["content"]
    except (KeyError, TypeError) as e:
        raise Exception(f"Unexpected Ollama response format: {e}")

    return content.strip()


def get_faq_items() -> List[FAQItem]:
    """
    Get the static FAQ list for Nepal and Sri Lanka.
    
    Returns:
        List of FAQItem objects
    """
    faq_data = [
        # Nepal basics
        FAQItem(
            question="What is the capital of Nepal?",
            answer="The capital city of Nepal is Kathmandu. It is famous for its historic temples, Durbar Squares, and vibrant cultural life."
        ),
        FAQItem(
            question="What is the official language of Nepal?",
            answer="The official language of Nepal is Nepali. It is written in the Devanagari script and is spoken across the country alongside many regional languages."
        ),
        FAQItem(
            question="Which mountains are in Nepal?",
            answer="Nepal is home to the Himalayan mountain range, including Mount Everest (Sagarmatha), the world's highest peak, as well as Annapurna, Manaslu, and many others."
        ),
        FAQItem(
            question="What is Dashain festival in Nepal?",
            answer="Dashain is Nepal's biggest festival, celebrating the victory of good over evil. Families gather, receive tika and jamara from elders, and enjoy special foods and traditions."
        ),
        FAQItem(
            question="What is Tihar festival?",
            answer="Tihar, also known as Deepawali, is the festival of lights in Nepal. It honours crows, dogs, cows, and Laxmi, the goddess of wealth, with lamps, rangoli, and family celebrations."
        ),
        FAQItem(
            question="Which currency is used in Nepal?",
            answer="Nepal uses the Nepalese Rupee (NPR) as its official currency."
        ),
        FAQItem(
            question="What is the major religion in Nepal?",
            answer="Hinduism is the majority religion in Nepal, followed by Buddhism. The two traditions are closely linked in culture and daily life."
        ),
        FAQItem(
            question="What are some famous places to visit in Nepal?",
            answer="Popular destinations include Kathmandu Valley, Pokhara, Chitwan National Park, Lumbini (the birthplace of Buddha), and trekking regions like Everest and Annapurna."
        ),

        # Sri Lanka basics
        FAQItem(
            question="What is the capital of Sri Lanka?",
            answer="Sri Lanka has two capitals: Sri Jayawardenepura Kotte as the official administrative capital, and Colombo as the commercial capital."
        ),
        FAQItem(
            question="What is the national flower of Sri Lanka?",
            answer="The national flower of Sri Lanka is the Blue Water Lily (Nymphaea nouchali), known locally as Nil Manel."
        ),
        FAQItem(
            question="Which languages are official in Sri Lanka?",
            answer="Sri Lanka has two official languages: Sinhala and Tamil. English is widely used as a link language in administration, education, and business."
        ),
        FAQItem(
            question="What is Vesak in Sri Lanka?",
            answer="Vesak is a major Buddhist festival marking the birth, enlightenment, and passing away (Parinirvana) of the Buddha. Streets and homes are decorated with lanterns and pandals."
        ),
        FAQItem(
            question="What is the currency of Sri Lanka?",
            answer="Sri Lanka uses the Sri Lankan Rupee (LKR) as its official currency."
        ),
        FAQItem(
            question="What are popular tourist spots in Sri Lanka?",
            answer="Key attractions include Sigiriya Rock Fortress, Kandy, Ella, Galle, Yala National Park, and the coastal beaches like Mirissa and Unawatuna."
        ),
        FAQItem(
            question="What is typical Sri Lankan food?",
            answer="Rice and curry is the staple, often served with dhal, vegetables, sambols, and sometimes fish or meat. Popular dishes include string hoppers, kottu, and hoppers (appa)."
        ),
        FAQItem(
            question="Which religions are followed in Sri Lanka?",
            answer="Buddhism is the majority religion, followed by Hinduism, Islam, and Christianity. Religious festivals from all communities are celebrated throughout the year."
        ),

        # Nepal–Sri Lanka comparison & travel
        FAQItem(
            question="How are Nepal and Sri Lanka different in geography?",
            answer="Nepal is a landlocked, mountainous country dominated by the Himalayas, while Sri Lanka is an island nation in the Indian Ocean with coastal plains and central highlands."
        ),
        FAQItem(
            question="Which time zone do Nepal and Sri Lanka use?",
            answer="Nepal uses Nepal Time (UTC+5:45). Sri Lanka uses Sri Lanka Standard Time (UTC+5:30)."
        ),
        FAQItem(
            question="Is it safe to travel to Nepal and Sri Lanka?",
            answer="Both Nepal and Sri Lanka are generally safe for tourists if you follow normal travel precautions, respect local customs, and keep updated through official advisories."
        ),
        FAQItem(
            question="Do I need a visa to visit Nepal or Sri Lanka?",
            answer="Many visitors need a visa for both countries, often available on arrival or through an e-visa system. Always check the latest official requirements before travelling."
        ),

        # Culture & history extras
        FAQItem(
            question="What is Lumbini famous for?",
            answer="Lumbini in Nepal is famous as the birthplace of Siddhartha Gautama, who became the Buddha. It is a UNESCO World Heritage Site with monasteries and a sacred garden."
        ),
        FAQItem(
            question="Why is Kandy important in Sri Lanka?",
            answer="Kandy is culturally important because it hosts the Temple of the Tooth Relic (Sri Dalada Maligawa), one of the most sacred Buddhist sites in Sri Lanka."
        ),
        FAQItem(
            question="What is special about Nepali and Sinhala New Year?",
            answer="Both Nepali New Year (around mid-April) and Sinhala and Tamil New Year in Sri Lanka celebrate the agricultural cycle with family gatherings, food, games, and rituals."
        ),
        FAQItem(
            question="Can people speak English in Nepal and Sri Lanka?",
            answer="Yes. While local languages dominate daily life, many people in cities, tourism, and education can communicate in English in both countries."
        ),
    ]
    
    return faq_data
