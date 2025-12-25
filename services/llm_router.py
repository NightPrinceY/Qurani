"""
LLM Router Service
Handles intent classification and routing to appropriate services
Uses Hugging Face Inference API for GPT-OSS-20B
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Literal
from huggingface_hub import InferenceClient
import logging
import os

# Try to import from config, use defaults if not available
try:
    from config import HF_TOKEN, LLM_MODEL
except ImportError:
    HF_TOKEN = os.getenv("HF_TOKEN", "")
    LLM_MODEL = "openai/gpt-oss-20b"
    if not HF_TOKEN:
        logging.warning("HF_TOKEN not set! LLM service may not work.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize HF Inference Client
client = InferenceClient(api_key=HF_TOKEN)

app = FastAPI(
    title="LLM Router Service",
    description="Intelligent routing and orchestration service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Intent types
IntentType = Literal[
    "recitation_validation",
    "translation_request",
    "tafsir_query",
    "general_qa",
    "verse_lookup",
    "other_nlp_tasks"
]

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    context: Optional[Dict] = None

class IntentRequest(BaseModel):
    text: str
    context: Optional[Dict] = None

class RoutingRequest(BaseModel):
    intent: IntentType
    text: str
    context: Optional[Dict] = None

# System prompts for different tasks (in Arabic context)
SYSTEM_PROMPTS = {
    "intent_classification": """أنت مصنف نوايا لمساعد صوتي قرآني. 
صنف النص العربي للمستخدم إلى واحدة من هذه النوايا:
- recitation_validation: المستخدم يريد التحقق من تلاوته القرآنية
- translation_request: المستخدم يريد ترجمة آية
- tafsir_query: المستخدم يريد تفسير أو شرح آية
- verse_lookup: المستخدم يريد العثور على آية محددة
- general_qa: أسئلة عامة عن القرآن أو الإسلام
- other_nlp_tasks: مهام معالجة لغة طبيعية أخرى

أجب باسم النية فقط، لا شيء آخر.""",
    
    "routing": """أنت موجه لنظام قرآني متعدد الوكلاء. بناءً على نية المستخدم والاستعلام، 
حدد الخدمات التي يجب استدعاؤها وترتيبها. الخدمات المتاحة:
- quran_validator: للتحقق من التلاوة
- tafsir_rag: لتفسير وشرح الآيات
- translation: لترجمة الآيات
- verse_search: للعثور على الآيات

أجب بكائن JSON يحتوي على:
{
    "services": ["service1", "service2"],
    "reasoning": "شرح موجز"
}""",
    
    "general_qa": """أنت مساعد مفيد للأسئلة حول القرآن والإسلام. 
قدم إجابات دقيقة ومحترمة بناءً على المعرفة الإسلامية. 
أجب دائماً بالعربية. إذا لم تكن متأكداً، قل ذلك."""
}

@app.get("/health")
async def health_check():
    """Health check endpoint - tests LLM connection"""
    try:
        # Test a simple query to ensure connectivity - use exact model card format
        test_messages = [{"role": "user", "content": "Hello"}]
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=test_messages,
            max_tokens=10,
            temperature=0.1
        )
        if completion.choices[0].message.content:
            return {
                "status": "healthy",
                "llm_connected": True,
                "model": LLM_MODEL,
                "service": "llm_router"
            }
        return {
            "status": "degraded",
            "llm_connected": False,
            "message": "LLM did not return content",
            "model": LLM_MODEL,
            "service": "llm_router"
        }
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        return {
            "status": "unhealthy",
            "llm_connected": False,
            "error": str(e),
            "model": LLM_MODEL,
            "service": "llm_router",
            "message": "LLM connection failed. Check HF_TOKEN and model availability."
        }

@app.post("/validate_recitation")
async def validate_recitation(request: IntentRequest):
    """
    Validate Quran recitation using LLM as a specialized Quran expert
    Uses actual Quran database to find matches, then LLM for detailed feedback
    """
    import json
    from pathlib import Path
    from difflib import SequenceMatcher
    import re
    
    try:
        # Load Quran database
        BASE_DIR = Path(__file__).parent.parent
        QURAN_DATA_DIR = BASE_DIR / "Quran_Data" / "data"
        SURAH_DIR = QURAN_DATA_DIR / "surah"
        TAJWEED_DIR = QURAN_DATA_DIR / "tajweed"
        
        # Find best matching verse from database
        best_match = None
        best_similarity = 0.0
        matched_verse_text = ""
        matched_surah_index = ""
        matched_verse_key = ""
        matched_surah_name = ""
        
        # Normalize user text for comparison
        def normalize_text(text):
            # Remove diacritics for comparison
            text = re.sub(r'[\u064B-\u0652\u0654-\u065F\u0670]', '', text)
            text = text.replace('\u0623', '\u0627').replace('\u0625', '\u0627').replace('\u0622', '\u0627')
            text = text.replace('\u0649', '\u064A').replace('\u0629', '\u0647')
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        
        user_text_normalized = normalize_text(request.text)
        
        # Search through all surahs
        for surah_file in SURAH_DIR.glob("surah_*.json"):
            try:
                with open(surah_file, "r", encoding="utf-8") as f:
                    surah_data = json.load(f)
                    if "verse" in surah_data:
                        for verse_key, verse_text in surah_data["verse"].items():
                            verse_normalized = normalize_text(verse_text)
                            similarity = SequenceMatcher(None, user_text_normalized, verse_normalized).ratio()
                            
                            if similarity > best_similarity:
                                best_similarity = similarity
                                matched_verse_text = verse_text
                                matched_surah_index = surah_data["index"]
                                matched_verse_key = verse_key
                                matched_surah_name = surah_data.get("name", "")
                                best_match = {
                                    "surah_index": surah_data["index"],
                                    "surah_name": surah_data.get("name", ""),
                                    "verse_key": verse_key,
                                    "verse_text": verse_text,
                                    "similarity": similarity
                                }
            except Exception as e:
                logger.warning(f"Error reading {surah_file}: {e}")
                continue
        
        # Load surah metadata for Arabic name
        try:
            with open(QURAN_DATA_DIR / "surah.json", "r", encoding="utf-8") as f:
                surah_metadata = json.load(f)
                for surah_meta in surah_metadata:
                    if surah_meta["index"] == matched_surah_index:
                        matched_surah_name = surah_meta.get("titleAr", matched_surah_name)
                        break
        except:
            pass
        
        # Prepare context for LLM
        context_info = ""
        if best_match and best_similarity > 0.7:
            context_info = f"""
الآية المطابقة من قاعدة البيانات:
- السورة: {matched_surah_name} ({matched_surah_index})
- رقم الآية: {matched_verse_key}
- النص الصحيح: {matched_verse_text}
- نسبة التطابق: {best_similarity:.1%}
"""
        
        # Load tajweed rules if available
        tajweed_info = ""
        tajweed_rules_list = []
        if matched_surah_index and matched_verse_key:
            try:
                tajweed_file = TAJWEED_DIR / f"surah_{matched_surah_index}.json"
                if tajweed_file.exists():
                    with open(tajweed_file, "r", encoding="utf-8") as f:
                        tajweed_data = json.load(f)
                        if "verse" in tajweed_data and matched_verse_key in tajweed_data["verse"]:
                            rules = tajweed_data["verse"][matched_verse_key]
                            tajweed_rules_list = rules
                            
                            # Format tajweed rules for LLM
                            rules_text = []
                            for rule in rules:
                                rule_name = rule.get("rule", "")
                                start = rule.get("start", 0)
                                end = rule.get("end", 0)
                                
                                # Translate rule names to Arabic
                                rule_translations = {
                                    "hamzat_wasl": "همزة الوصل",
                                    "madd_2": "مد طبيعي (مدتين)",
                                    "madd_246": "مد لازم (أربع أو ست مدات)",
                                    "madd_6": "مد لازم (ست مدات)",
                                    "lam_shamsiyyah": "اللام الشمسية",
                                    "ghunnah": "الغنة",
                                    "idgham": "الإدغام",
                                    "ikhfa": "الإخفاء",
                                    "qalqalah": "القلقلة"
                                }
                                rule_ar = rule_translations.get(rule_name, rule_name)
                                rules_text.append(f"- {rule_ar} (من الحرف {start} إلى {end})")
                            
                            if rules_text:
                                tajweed_info = f"\n\nقواعد التجويد المطلوبة لهذه الآية:\n" + "\n".join(rules_text)
            except Exception as e:
                logger.debug(f"Could not load tajweed: {e}")
        
        # Create enhanced system prompt with Quran knowledge and tajweed
        if best_match and best_similarity > 0.7:
            system_prompt = f"""أنت خبير متخصص في القرآن الكريم والتلاوة الصحيحة والتجويد. مهمتك هي التحقق من صحة تلاوة القرآن بدقة.

{context_info}

عندما يعطيك المستخدم نصاً، يجب أن:
1. قارن نص المستخدم مع النص الصحيح من قاعدة البيانات أعلاه
2. تحدد إذا كانت التلاوة صحيحة تماماً (مطابقة 100%)
3. إذا كانت هناك أخطاء، حددها بدقة مع التصحيحات المحددة
4. ركز على أخطاء التجويد (التجويد) مثل:
   - مدة المد (madd) - يجب تطبيق المد بالعدد الصحيح
   - همزة الوصل (hamzat_wasl) - يجب نطقها أو حذفها حسب السياق
   - اللام الشمسية (lam_shamsiyyah) - يجب دمج اللام مع الحرف التالي
   - الغنة (ghunnah) - يجب تطبيق الصوت الأنفي
   - الإدغام (idgham) - يجب دمج الحروف
   - وغيرها من قواعد التجويد
5. أجب دائماً بالعربية
6. كن دقيقاً ومهذباً في التصحيحات
7. إذا كانت التلاوة صحيحة، اذكر اسم السورة ورقم الآية

{tajweed_info if tajweed_info else ""}

أجب بصيغة JSON فقط:
{{
    "is_correct": true/false,
    "feedback": "ردك بالعربية مع التشجيع أو التصحيحات المحددة",
    "corrections": ["قائمة التصحيحات المحددة إن وجدت"],
    "matched_verse": "{matched_verse_text}",
    "surah_name": "{matched_surah_name}",
    "verse_key": "{matched_verse_key}"
}}"""
        else:
            # No good match found - use LLM's Quran knowledge
            system_prompt = """أنت خبير متخصص في القرآن الكريم والتلاوة الصحيحة والتجويد. مهمتك هي التحقق من صحة تلاوة القرآن بدقة.

استخدم معرفتك الكاملة بالقرآن الكريم (جميع السور والآيات) للتحقق من التلاوة.

عندما يعطيك المستخدم نصاً، يجب أن:
1. ابحث في معرفتك عن الآية المطابقة
2. تحدد إذا كانت التلاوة صحيحة تماماً
3. إذا كانت هناك أخطاء، حددها بدقة مع التصحيحات المحددة
4. ركز على أخطاء التجويد (التجويد)
5. أجب دائماً بالعربية
6. كن دقيقاً ومهذباً في التصحيحات

أجب بصيغة JSON فقط:
{
    "is_correct": true/false,
    "feedback": "ردك بالعربية مع التشجيع أو التصحيحات المحددة",
    "corrections": ["قائمة التصحيحات المحددة إن وجدت"],
    "matched_verse": "النص الصحيح من القرآن إن تم التعرف عليه",
    "surah_name": "اسم السورة إن تم التعرف عليها",
    "verse_key": "رقم الآية إن تم التعرف عليها"
}"""

        user_message = f"تحقق من هذه التلاوة:\n{request.text}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        logger.info(f"Validating recitation: {request.text[:50]}... (Best match: {best_similarity:.1%})")
        
        # Ensure model name is valid (no colons) - use exact model card format
        model_name = "openai/gpt-oss-20b"
        
        try:
            # Try with JSON format first, fallback to regular if it fails
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=600,
                    temperature=0.1,  # Low temperature for accuracy
                    response_format={"type": "json_object"}
                )
            except Exception as json_error:
                logger.warning(f"JSON format failed, trying without: {json_error}")
                # Fallback: ask LLM to return JSON in text, then parse
                messages_with_json_instruction = messages.copy()
                messages_with_json_instruction[-1]["content"] = messages[-1]["content"] + "\n\nأجب بصيغة JSON فقط: {\"is_correct\": true/false, \"feedback\": \"...\", \"corrections\": [...], \"matched_verse\": \"...\", \"surah_name\": \"...\", \"verse_key\": \"...\"}"
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=messages_with_json_instruction,
                    max_tokens=600,
                    temperature=0.1
                )
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            # Return fallback response
            return JSONResponse({
                "is_correct": False,
                "feedback": "عذراً، حدث خطأ في الاتصال بخدمة التحقق. يرجى المحاولة مرة أخرى.",
                "corrections": [],
                "matched_verse": matched_verse_text if best_match else "",
                "surah_name": matched_surah_name if best_match else "",
                "verse_key": matched_verse_key if best_match else "",
                "error": str(e)
            }, status_code=503)
        
        llm_response = completion.choices[0].message.content
        
        # Handle None response
        if not llm_response:
            logger.warning("LLM returned None response in validate_recitation")
            llm_response = "عذراً، لم أتمكن من الحصول على استجابة. يرجى المحاولة مرة أخرى."
        
        logger.info(f"LLM validation response: {llm_response[:100] if llm_response else 'None'}...")

        # Parse JSON response
        try:
            result = json.loads(llm_response)
            
            # Enhance with database match info
            if best_match and best_similarity > 0.85:
                result["is_correct"] = True
                if not result.get("matched_verse"):
                    result["matched_verse"] = matched_verse_text
                if not result.get("surah_name"):
                    result["surah_name"] = matched_surah_name
                if not result.get("verse_key"):
                    result["verse_key"] = matched_verse_key
            elif best_match:
                # Partial match - use LLM feedback but add database info
                if not result.get("matched_verse"):
                    result["matched_verse"] = matched_verse_text
                if not result.get("surah_name"):
                    result["surah_name"] = matched_surah_name
                if not result.get("verse_key"):
                    result["verse_key"] = matched_verse_key
                result["similarity"] = best_similarity
            
            return JSONResponse(result)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails - voice optimized
            if best_similarity > 0.85:
                feedback = "ممتاز! قراءتك صحيحة تماماً."
            else:
                feedback = "قراءتك قريبة من الصحيح، لكن تحتاج إلى بعض التحسينات."
            
            if best_match:
                feedback += f" هذه الآية {matched_verse_key} من سورة {matched_surah_name}."
            
            # Voice-optimized response
            return JSONResponse({
                "is_correct": best_similarity > 0.85,
                "feedback": feedback,
                "feedback_voice_optimized": True,
                "corrections": [],
                "matched_verse": matched_verse_text if best_match else "",
                "surah_name": matched_surah_name if best_match else "",
                "verse_key": matched_verse_key if best_match else ""
            })

    except Exception as e:
        logger.error(f"Error in recitation validation: {e}", exc_info=True)
        return JSONResponse(
            {"error": str(e), "is_correct": False, "feedback": "حدث خطأ في التحقق من التلاوة."},
            status_code=500
        )

@app.post("/classify_intent")
async def classify_intent(request: IntentRequest):
    """
    Classify user intent from text
    
    Args:
        request: IntentRequest with text and optional context
    
    Returns:
        Intent classification result
    """
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS["intent_classification"]},
            {"role": "user", "content": f"Classify this text: {request.text}"}
        ]
        
        if request.context:
            messages.append({
                "role": "system",
                "content": f"Context: {request.context}"
            })
        
        logger.info(f"Classifying intent for text: {request.text[:50]}...")
        
        # Use exact model card format
        model_name = "openai/gpt-oss-20b"
        
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.3,  # Lower temperature for classification
                max_tokens=50
            )
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return JSONResponse(
                {"error": str(e), "intent": "general_qa", "status": "error"},
                status_code=503
            )
        
        intent_content = completion.choices[0].message.content
        if not intent_content:
            logger.warning("LLM returned None intent, using default")
            intent_content = "general_qa"
        # Note: Intent should be in English, so .lower() is appropriate here
        intent = intent_content.strip().lower()
        
        # Validate intent
        valid_intents = [
            "recitation_validation", "translation_request", "tafsir_query",
            "general_qa", "verse_lookup", "other_nlp_tasks"
        ]
        
        # Extract intent from response (handle variations)
        detected_intent = None
        for valid_intent in valid_intents:
            if valid_intent in intent or valid_intent.replace("_", " ") in intent:
                detected_intent = valid_intent
                break
        
        if not detected_intent:
            detected_intent = "general_qa"  # Default fallback
        
        logger.info(f"Detected intent: {detected_intent}")
        
        return JSONResponse({
            "intent": detected_intent,
            "confidence": 0.9,  # Could be improved with probability scores
            "original_response": intent,
            "status": "success"
        })
    
    except Exception as e:
        logger.error(f"Intent classification error: {e}", exc_info=True)
        return JSONResponse(
            {"error": str(e), "status": "error"},
            status_code=500
        )

@app.post("/route")
async def route_request(request: RoutingRequest):
    """
    Route request to appropriate services
    
    Args:
        request: RoutingRequest with intent and context
    
    Returns:
        Routing plan with services to invoke
    """
    try:
        routing_prompt = f"""Based on intent '{request.intent}' and query '{request.text}',
determine which services to invoke. Available services: quran_validator, tafsir_rag, translation, verse_search.
Respond with JSON only: {{"services": ["service1"], "reasoning": "explanation"}}"""
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS["routing"]},
            {"role": "user", "content": routing_prompt}
        ]
        
        # Use exact model card format
        model_name = "openai/gpt-oss-20b"
        
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.5,
            max_tokens=200
        )
        
        response = completion.choices[0].message.content
        
        # Handle None response
        if not response:
            logger.warning("LLM returned None response in route")
            response = '{"services": [], "reasoning": "No response from LLM"}'
        
        # Parse JSON from response (simple extraction)
        import json
        import re
        json_match = re.search(r'\{[^}]+\}', response)
        if json_match:
            routing_plan = json.loads(json_match.group())
        else:
            # Fallback routing based on intent
            routing_plan = {
                "services": get_default_services(request.intent),
                "reasoning": "Default routing based on intent"
            }
        
        return JSONResponse({
            "routing_plan": routing_plan,
            "intent": request.intent,
            "status": "success"
        })
    
    except Exception as e:
        logger.error(f"Routing error: {e}", exc_info=True)
        return JSONResponse(
            {"error": str(e), "status": "error"},
            status_code=500
        )

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Voice Assistant Chat Endpoint
    The LLM acts as the "brain" between STT and TTS
    Responses are optimized for voice (natural, conversational, clear for TTS)
    
    Args:
        request: ChatRequest with messages and parameters
    
    Returns:
        LLM response optimized for voice/TTS in Arabic
    """
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Voice Assistant System Prompt - optimized for TTS
        voice_assistant_prompt = """أنت مساعد صوتي ذكي متخصص في مساعدة الناس في حفظ القرآن الكريم وتعلمه.

مهمتك:
1. أنت العقل (الدماغ) بين تحويل الصوت إلى نص (STT) وتحويل النص إلى صوت (TTS)
2. استجاباتك ستُقرأ بصوت عالي، لذا يجب أن تكون:
   - طبيعية ومحادثة (كما تتحدث مع صديق)
   - واضحة وسهلة النطق
   - مختصرة ومناسبة للصوت (تجنب الجمل الطويلة جداً)
   - مشجعة ومحترمة
   - مفيدة لمساعدة المستخدم في حفظ القرآن

قواعد الاستجابة:
- أجب دائماً بالعربية الفصحى الواضحة
- استخدم لغة محادثة طبيعية (ليس رسمية جداً)
- كن مشجعاً ومحفزاً
- إذا سأل عن آية، اذكرها بدقة
- إذا طلب التحقق من قراءة، قدم ملاحظات مفيدة
- إذا طلب تفسير، اشرح بطريقة بسيطة تساعد على الحفظ
- تجنب الأرقام والرموز المعقدة (استخدم كلمات)
- اجعل الجمل قصيرة ومناسبة للقراءة الصوتية

تذكر: استجاباتك ستُقرأ بصوت، لذا اجعلها طبيعية وواضحة!"""

        # Ensure voice assistant prompt is present
        has_system = any(msg.get("role") == "system" for msg in messages)
        if not has_system:
            messages.insert(0, {
                "role": "system",
                "content": voice_assistant_prompt
            })
        else:
            # Update existing system prompt to include voice assistant context
            for i, msg in enumerate(messages):
                if msg.get("role") == "system":
                    existing_content = msg.get("content") or ""
                    messages[i]["content"] = voice_assistant_prompt + "\n\n" + existing_content
                    break
        
        # Optimize temperature for voice responses (slightly higher for naturalness)
        temperature = request.temperature if request.temperature else 0.75
        
        # Use exact model card format
        model_name = "openai/gpt-oss-20b"
        
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=request.max_tokens or 300  # Shorter for voice (default 300)
            )
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return JSONResponse(
                {
                    "error": str(e),
                    "response": "عذراً، حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.",
                    "status": "error"
                },
                status_code=503
            )
        
        response = completion.choices[0].message.content
        
        # Handle None response
        if not response:
            logger.warning("LLM returned None or empty response")
            response = "عذراً، لم أتمكن من الحصول على استجابة. يرجى المحاولة مرة أخرى."
        
        # Clean response for TTS (remove special characters that don't read well)
        import re
        # Remove excessive punctuation but keep sentence endings (only if response is not None)
        if response:
            response = re.sub(r'[.]{2,}', '.', response)  # Multiple dots to single
            response = re.sub(r'[!]{2,}', '!', response)  # Multiple exclamations to single
            response = re.sub(r'[?]{2,}', '?', response)  # Multiple questions to single
        
        return JSONResponse({
            "response": response,
            "response_arabic": response,  # Explicitly mark as Arabic
            "response_voice_optimized": True,  # Mark as optimized for voice
            "model": LLM_MODEL,
            "status": "success"
        })
    
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return JSONResponse(
            {"error": str(e), "status": "error"},
            status_code=500
        )

def get_default_services(intent: IntentType) -> List[str]:
    """Get default services for each intent"""
    mapping = {
        "recitation_validation": ["quran_validator"],
        "translation_request": ["translation"],
        "tafsir_query": ["tafsir_rag"],
        "verse_lookup": ["verse_search"],
        "general_qa": [],
        "other_nlp_tasks": []
    }
    return mapping.get(intent, [])

if __name__ == "__main__":
    import uvicorn
    
    # Get port from config or use default
    try:
        from config import LLM_SERVICE_PORT
        port = LLM_SERVICE_PORT
    except ImportError:
        port = 8002
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

