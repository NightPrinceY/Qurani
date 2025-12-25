"""
Quran Validator Microservice - LLM-based Validation
Uses LLM to validate Quranic recitation and provide teacher-like feedback
The LLM has knowledge of the Quran and can validate recitations directly
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
import logging
import httpx

# Try to import from config, use defaults if not available
try:
    from config import LLM_SERVICE_PORT
except ImportError:
    LLM_SERVICE_PORT = 8002

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Quran Validator Service",
    description="LLM-based validation of Quranic recitation with teacher-like feedback",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ValidationRequest(BaseModel):
    text: str
    surah_index: Optional[str] = None
    verse_number: Optional[str] = None
    use_teacher_mode: Optional[bool] = True  # Enable teacher-like detailed feedback

LLM_SERVICE_URL = f"http://localhost:{LLM_SERVICE_PORT}"

async def validate_with_llm(user_text: str, surah_index: Optional[str] = None, verse_number: Optional[str] = None, use_teacher_mode: bool = True) -> Dict:
    """
    Validate recitation using LLM directly
    The LLM knows the Quran and can validate recitations
    """
    try:
        logger.info(f"Validating with LLM: {user_text[:50]}... (surah: {surah_index}, verse: {verse_number})")
        # Build validation prompt for LLM
        context_info = ""
        if surah_index:
            context_info += f" من سورة رقم {surah_index}"
        if verse_number:
            context_info += f" الآية رقم {verse_number}"
        
        system_prompt = """أنت معلم قرآن كريم محترف (مُعَلِّم) متخصص في تصحيح تلاوة القرآن الكريم.

مهمتك:
1. تحقق من صحة القراءة المدخلة مقابل النص الصحيح من القرآن الكريم
2. إذا كانت القراءة صحيحة: امدح المتعلم وشجعه بطريقة إسلامية محترمة (مثل: بارك الله فيك، جزاك الله خيراً، ممتاز)
3. إذا كانت هناك أخطاء: اشرح الخطأ بوضوح، واذكر النص الصحيح، وأعط نصائح لتحسين القراءة
4. كن مشجعاً ومحترماً في النبرة
5. استخدم لغة عربية إسلامية واضحة ومهذبة

أجب دائماً بالعربية فقط."""

        user_prompt = f"""الرجاء التحقق من صحة هذه التلاوة:
"{user_text}"
{context_info if context_info else ""}

قدم لي:
1. هل القراءة صحيحة أم لا
2. إذا كانت صحيحة: امدح المتعلم بطريقة إسلامية مشجعة
3. إذا كانت خاطئة: اذكر النص الصحيح من القرآن، واشرح الأخطاء، وأعط نصائح للتحسين
4. اذكر اسم السورة ورقم الآية إذا أمكن

أجب بطريقة المعلم المحترف والمشجع."""

        async with httpx.AsyncClient(timeout=60.0) as client:
            logger.debug(f"Calling LLM service at {LLM_SERVICE_URL}/chat")
            response = await client.post(
                f"{LLM_SERVICE_URL}/chat",
                json={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            
            logger.debug(f"LLM service response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                llm_feedback = data.get("response_arabic") or data.get("response") or ""
                
                # Ensure llm_feedback is a string
                if not isinstance(llm_feedback, str):
                    llm_feedback = str(llm_feedback) if llm_feedback else ""
                
                # Try to parse LLM response to determine if correct
                # Simple heuristic: look for positive/negative indicators
                # Note: Arabic doesn't have case, so we check directly without .lower()
                if llm_feedback:
                    is_correct = any(word in llm_feedback for word in [
                        "صحيح", "صحيحة", "ممتاز", "جيد", "بارك", "جزاك", "تمام", "صحيح تمام"
                    ])
                    is_incorrect = any(word in llm_feedback for word in [
                        "خطأ", "خاطئ", "خاطئة", "يجب", "الصحيح", "تصحيح"
                    ])
                    
                    # If LLM says it's correct and doesn't mention errors, mark as correct
                    if is_correct and not is_incorrect:
                        is_correct_flag = True
                    elif is_incorrect:
                        is_correct_flag = False
                    else:
                        # Ambiguous - default to checking if feedback is positive
                        is_correct_flag = len(llm_feedback) > 50 and ("ممتاز" in llm_feedback or "صحيح" in llm_feedback)
                else:
                    # No feedback received
                    logger.warning("LLM returned empty feedback")
                    llm_feedback = "عذراً، لم أتمكن من الحصول على استجابة من خدمة التحقق. يرجى المحاولة مرة أخرى."
                    is_correct_flag = False
                
                return {
                    "is_correct": is_correct_flag,
                    "is_close": not is_incorrect,  # If no clear errors, consider it close
                    "feedback_arabic": llm_feedback,
                    "feedback_english": llm_feedback,  # Same for now
                    "matched_verse": None,  # LLM doesn't return structured verse info
                    "corrections": [],
                    "match_count": 1 if is_correct_flag else 0,
                    "status": "success"
                }
            else:
                logger.error(f"LLM service error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"LLM service error: {response.text}"
                )
    
    except httpx.TimeoutException:
        logger.error("LLM service timeout")
        return {
            "is_correct": False,
            "is_close": False,
            "feedback_arabic": "عذراً، انتهت مهلة الاستجابة. يرجى المحاولة مرة أخرى.",
            "feedback_english": "Timeout error. Please try again.",
            "matched_verse": None,
            "corrections": [],
            "match_count": 0,
            "status": "timeout"
        }
    except httpx.ConnectError as e:
        logger.error(f"Cannot connect to LLM service: {e}")
        return {
            "is_correct": False,
            "is_close": False,
            "feedback_arabic": "عذراً، لا يمكن الاتصال بخدمة التحقق. يرجى التأكد من أن خدمة LLM تعمل.",
            "feedback_english": "Cannot connect to LLM service. Please ensure the service is running.",
            "matched_verse": None,
            "corrections": [],
            "match_count": 0,
            "status": "connection_error"
        }
    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        return {
            "is_correct": False,
            "is_close": False,
            "feedback_arabic": f"عذراً، حدث خطأ: {str(e)[:100]}. يرجى المحاولة مرة أخرى.",
            "feedback_english": f"Error: {str(e)}",
            "matched_verse": None,
            "corrections": [],
            "match_count": 0,
            "status": "error"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if LLM service is available
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{LLM_SERVICE_URL}/health")
            llm_available = response.status_code == 200
    except:
        llm_available = False
    
    return {
        "status": "healthy" if llm_available else "degraded",
        "llm_service_available": llm_available,
        "service": "quran_validator_llm",
        "version": "3.0.0"
    }

@app.post("/validate")
async def validate_recitation(request: ValidationRequest):
    """
    Validate recitation text using LLM
    The LLM validates directly without needing database lookup
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        user_text = request.text.strip()
        logger.info(f"Validating recitation: {user_text[:50]}...")
        
        # Validate using LLM
        result = await validate_with_llm(
            user_text,
            request.surah_index,
            request.verse_number,
            request.use_teacher_mode
        )
        
        return JSONResponse({
            "matches": [] if not result.get("is_correct") else [{"status": "correct"}],
            "best_match": None,  # LLM doesn't return structured match info
            "match_count": result.get("match_count", 0),
            "is_correct": result.get("is_correct", False),
            "is_close": result.get("is_close", False),
            "feedback_arabic": result.get("feedback_arabic", ""),
            "feedback_english": result.get("feedback_english", ""),
            "matched_verse": result.get("matched_verse"),
            "corrections": result.get("corrections", []),
            "tajweed_rules": [],  # LLM-based, no structured tajweed rules
            "status": "success",
            "validation_method": "llm_direct"
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        return JSONResponse(
            {"error": str(e), "status": "error"},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    
    # Get port from config or use default
    try:
        from config import VALIDATOR_SERVICE_PORT
        port = VALIDATOR_SERVICE_PORT
    except ImportError:
        port = 8003
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
