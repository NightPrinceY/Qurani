"""
API Gateway
Main entry point for the multi-agent Quran assistant system
Orchestrates requests across all microservices
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import httpx
import logging
from config import (
    STT_SERVICE_PORT, LLM_SERVICE_PORT, VALIDATOR_SERVICE_PORT,
    TAFSIR_SERVICE_PORT, TTS_SERVICE_PORT, API_GATEWAY_PORT
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Agent Voice Quran Assistant API",
    description="API Gateway for Quranic voice assistant system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICE_URLS = {
    "stt": f"http://localhost:{STT_SERVICE_PORT}",
    "llm": f"http://localhost:{LLM_SERVICE_PORT}",
    "validator": f"http://localhost:{VALIDATOR_SERVICE_PORT}",
    "tafsir": f"http://localhost:{TAFSIR_SERVICE_PORT}",
    "tts": f"http://localhost:{TTS_SERVICE_PORT}"
}

class VoiceRequest(BaseModel):
    audio_file: Optional[str] = None
    text: Optional[str] = None
    intent: Optional[str] = None

class QueryRequest(BaseModel):
    text: str
    context: Optional[Dict] = None

async def check_service_health(service_name: str, url: str) -> bool:
    """Check if a service is healthy"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{url}/health")
            return response.status_code == 200
    except Exception as e:
        logger.warning(f"Service {service_name} health check failed: {e}")
        return False

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Multi-Agent Voice Quran Assistant API Gateway",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "voice_query": "/voice_query",
            "text_query": "/text_query",
            "transcribe": "/transcribe",
            "validate": "/validate",
            "tafsir": "/tafsir"
        }
    }

@app.get("/health")
async def health():
    """Health check for all services"""
    services_status = {}
    
    for service_name, url in SERVICE_URLS.items():
        services_status[service_name] = await check_service_health(service_name, url)
    
    all_healthy = all(services_status.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": services_status,
        "gateway": "healthy"
    }

@app.post("/voice_query")
async def voice_query(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Complete voice query pipeline:
    1. STT: Convert audio to text
    2. Intent Classification: Determine user intent
    3. Routing: Route to appropriate services
    4. Processing: Execute service logic
    5. TTS: Convert response to speech (optional)
    
    Args:
        file: Audio file with user's voice query
    
    Returns:
        Complete response with text and optional audio
    """
    try:
        # Step 1: Speech-to-Text
        logger.info("Step 1: Converting speech to text...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Forward audio file to STT service
            files = {"file": (file.filename, await file.read(), file.content_type)}
            stt_response = await client.post(
                f"{SERVICE_URLS['stt']}/transcribe",
                files=files
            )
            
            if stt_response.status_code != 200:
                raise HTTPException(
                    status_code=stt_response.status_code,
                    detail=f"STT service error: {stt_response.text}"
                )
            
            stt_data = stt_response.json()
            transcript = stt_data.get("transcript", "")
        
        if not transcript:
            return JSONResponse({
                "error": "No transcript generated",
                "status": "error"
            }, status_code=400)
        
        logger.info(f"Transcript: {transcript[:100]}...")
        
        # Step 2: Intent Classification
        logger.info("Step 2: Classifying intent...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            intent_response = await client.post(
                f"{SERVICE_URLS['llm']}/classify_intent",
                json={"text": transcript}
            )
            
            if intent_response.status_code != 200:
                logger.warning("Intent classification failed, using default")
                intent = "general_qa"
            else:
                intent_data = intent_response.json()
                intent = intent_data.get("intent", "general_qa")
        
        logger.info(f"Detected intent: {intent}")
        
        # Step 3: Route and Process
        logger.info("Step 3: Processing request...")
        result = await process_intent(intent, transcript)
        
        # Step 4: Generate response text
        response_text = result.get("response", "I'm sorry, I couldn't process your request.")
        
        # Step 5: Text-to-Speech (optional - can be done async)
        audio_url = None
        if result.get("generate_audio", False):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    tts_response = await client.post(
                        f"{SERVICE_URLS['tts']}/synthesize",
                        json={"text": response_text}
                    )
                    if tts_response.status_code == 200:
                        # Handle audio response
                        audio_url = "audio_generated"
            except Exception as e:
                logger.warning(f"TTS generation failed: {e}")
        
        return JSONResponse({
            "transcript": transcript,
            "intent": intent,
            "response": response_text,
            "result": result,
            "audio_url": audio_url,
            "status": "success"
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice query error: {e}", exc_info=True)
        return JSONResponse(
            {"error": str(e), "status": "error"},
            status_code=500
        )

@app.post("/text_query")
async def text_query(request: QueryRequest):
    """
    Process text query (skips STT step)
    
    Args:
        request: QueryRequest with text and optional context
    
    Returns:
        Response with processed result
    """
    try:
        # Intent Classification - detect if it's a recitation validation
        # Simple heuristic: if text contains Arabic and looks like Quranic recitation
        import re
        arabic_pattern = re.compile(r'[\u0600-\u06FF]+')
        has_arabic = bool(arabic_pattern.search(request.text))
        
        # If it's Arabic text, assume it's recitation validation
        if has_arabic and len(request.text.strip()) > 5:
            intent = "recitation_validation"
        else:
            # Try LLM classification for other cases
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    intent_response = await client.post(
                        f"{SERVICE_URLS['llm']}/classify_intent",
                        json={"text": request.text, "context": request.context}
                    )
                    
                    if intent_response.status_code == 200:
                        intent_data = intent_response.json()
                        intent = intent_data.get("intent", "recitation_validation" if has_arabic else "general_qa")
                    else:
                        intent = "recitation_validation" if has_arabic else "general_qa"
                except:
                    intent = "recitation_validation" if has_arabic else "general_qa"
        
        # Process intent
        result = await process_intent(intent, request.text, request.context)
        
        return JSONResponse({
            "intent": intent,
            "response": result.get("response", ""),
            "result": result,
            "status": "success"
        })
    
    except Exception as e:
        logger.error(f"Text query error: {e}", exc_info=True)
        return JSONResponse(
            {"error": str(e), "status": "error"},
            status_code=500
        )

async def process_intent(intent: str, text: str, context: Optional[Dict] = None) -> Dict:
    """
    Process request based on intent
    
    Args:
        intent: Detected intent
        text: User text
        context: Optional context
    
    Returns:
        Processing result
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        if intent == "recitation_validation":
            # Validate recitation using LLM directly as Quran specialist
            llm_validation_response = await client.post(
                f"{SERVICE_URLS['llm']}/validate_recitation",
                json={"text": text}
            )
            
            if llm_validation_response.status_code == 200:
                validation_data = llm_validation_response.json()
                
                # Use Arabic feedback from LLM
                response = validation_data.get("feedback", "")
                is_correct = validation_data.get("is_correct", False)
                corrections = validation_data.get("corrections", [])
                matched_verse = validation_data.get("matched_verse", "")
                
                # Format response for display
                if not response:
                    if is_correct:
                        response = "ممتاز! قراءتك صحيحة تماماً."
                    else:
                        response = "قراءتك تحتاج إلى بعض التحسينات."
                
                return {
                    "response": response,
                    "response_arabic": response,
                    "is_correct": is_correct,
                    "corrections": corrections,
                    "matched_verse": matched_verse,
                    "validation_result": validation_data,
                    "generate_audio": False
                }
            else:
                # Fallback if LLM validation fails
                return {
                    "response": "عذراً، حدث خطأ في التحقق من التلاوة. يرجى المحاولة مرة أخرى.",
                    "response_arabic": "عذراً، حدث خطأ في التحقق من التلاوة. يرجى المحاولة مرة أخرى.",
                    "is_correct": False,
                    "corrections": [],
                    "generate_audio": False
                }
        
        elif intent == "tafsir_query":
            # Get tafsir - for memorization help, explain meaning
            tafsir_response = await client.post(
                f"{SERVICE_URLS['tafsir']}/tafsir",
                json={"query": text}
            )
            
            if tafsir_response.status_code == 200:
                tafsir_data = tafsir_response.json()
                tafsir_text = tafsir_data.get("tafsir", "")
                
                # Ensure response is helpful for memorization
                if not tafsir_text or "Error" in tafsir_text:
                    # Fallback to LLM for explanation
                    llm_response = await client.post(
                        f"{SERVICE_URLS['llm']}/chat",
                        json={
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "أنت مساعد لمساعدة الناس في حفظ القرآن. اشرح معنى الآيات بالعربية بطريقة بسيطة تساعد على الحفظ."
                                },
                                {"role": "user", "content": f"اشرح لي هذه الآية أو السؤال: {text}"}
                            ],
                            "temperature": 0.7,
                            "max_tokens": 300
                        }
                    )
                    if llm_response.status_code == 200:
                        llm_data = llm_response.json()
                        tafsir_text = llm_data.get("response_arabic") or llm_data.get("response", "")
                
                return {
                    "response": tafsir_text,
                    "response_arabic": tafsir_text,
                    "sources": tafsir_data.get("sources", []),
                    "generate_audio": False  # Text only for now
                }
        
        elif intent == "translation_request":
            # Translation - help with understanding for memorization
            return {
                "response": "خدمة الترجمة قيد التطوير. يمكنك استخدام خدمة التفسير للحصول على شرح الآيات.",
                "response_arabic": "خدمة الترجمة قيد التطوير. يمكنك استخدام خدمة التفسير للحصول على شرح الآيات.",
                "generate_audio": False
            }
        
        elif intent == "general_qa":
            # General QA using LLM - Arabic responses for memorization help
            llm_response = await client.post(
                f"{SERVICE_URLS['llm']}/chat",
                json={
                    "messages": [
                        {
                            "role": "system", 
                            "content": "أنت مساعد ذكي لمساعدة الناس في حفظ القرآن الكريم. أجب دائماً بالعربية بطريقة واضحة ومفيدة. كن مشجعاً ومحترماً. ركز على مساعدة المستخدم في حفظ القرآن."
                        },
                        {"role": "user", "content": text}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            
            if llm_response.status_code == 200:
                llm_data = llm_response.json()
                return {
                    "response": llm_data.get("response_arabic") or llm_data.get("response", ""),
                    "generate_audio": False  # Text only for now
                }
    
    return {
        "response": "I'm sorry, I couldn't process your request.",
        "generate_audio": False
    }

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Direct STT transcription endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        files = {"file": (file.filename, await file.read(), file.content_type)}
        response = await client.post(
            f"{SERVICE_URLS['stt']}/transcribe",
            files=files
        )
        return JSONResponse(response.json(), status_code=response.status_code)

@app.post("/validate")
async def validate(request: QueryRequest):
    """Direct validation endpoint - uses LLM as Quran specialist"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{SERVICE_URLS['llm']}/validate_recitation",
            json={"text": request.text}
        )
        if response.status_code == 200:
            data = response.json()
            return JSONResponse({
                "is_correct": data.get("is_correct", False),
                "feedback": data.get("feedback", ""),
                "corrections": data.get("corrections", []),
                "matched_verse": data.get("matched_verse", ""),
                "result": data
            })
        return JSONResponse(response.json(), status_code=response.status_code)

@app.post("/tafsir")
async def tafsir(request: QueryRequest):
    """Direct tafsir endpoint"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{SERVICE_URLS['tafsir']}/tafsir",
            json={"query": request.text}
        )
        return JSONResponse(response.json(), status_code=response.status_code)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=API_GATEWAY_PORT,
        log_level="info"
    )

