"""
Tafsir RAG (Retrieval-Augmented Generation) Service
Provides verse interpretation using RAG with classical sources
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import json
import os

# Try to import from config, use defaults if not available
try:
    from config import (
        HF_TOKEN, LLM_MODEL, EMBEDDING_MODEL, VECTOR_DB_PATH,
        RAG_TOP_K, RAG_SIMILARITY_THRESHOLD, RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP
    )
except ImportError:
    HF_TOKEN = os.getenv("HF_TOKEN", "")
    LLM_MODEL = "openai/gpt-oss-20b"
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    BASE_DIR = Path(__file__).parent.parent
    VECTOR_DB_PATH = BASE_DIR / "vector_db"
    RAG_TOP_K = 5
    RAG_SIMILARITY_THRESHOLD = 0.7
    RAG_CHUNK_SIZE = 300
    RAG_CHUNK_OVERLAP = 50

# Import optional dependencies
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import faiss
    from huggingface_hub import InferenceClient
    HAS_DEPENDENCIES = True
except ImportError as e:
    HAS_DEPENDENCIES = False
    logging.warning(f"Some dependencies not available: {e}. RAG features will be limited.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tafsir RAG Service",
    description="Retrieval-Augmented Generation for Quranic interpretation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TafsirRequest(BaseModel):
    query: str
    surah_index: Optional[str] = None
    verse_key: Optional[str] = None
    top_k: Optional[int] = RAG_TOP_K

# Initialize models
embedding_model = None
llm_client = None
vector_index = None
passage_metadata = []

def load_embedding_model():
    """Load sentence transformer model for embeddings"""
    global embedding_model
    if not HAS_DEPENDENCIES:
        logger.warning("Dependencies not available. Embedding model not loaded.")
        return
    
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
    try:
        embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        embedding_model = None

def load_llm_client():
    """Initialize HF Inference client for LLM"""
    global llm_client
    if not HAS_DEPENDENCIES:
        logger.warning("Dependencies not available. LLM client not initialized.")
        return
    
    if not HF_TOKEN:
        logger.warning("HF_TOKEN not set. LLM client not initialized.")
        return
    
    try:
        llm_client = InferenceClient(api_key=HF_TOKEN)
        logger.info("LLM client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}")
        llm_client = None

def build_vector_index():
    """Build or load vector index for tafsir passages"""
    global vector_index, passage_metadata
    
    if embedding_model is None:
        logger.warning("Embedding model not loaded. Skipping vector index creation.")
        vector_index = None
        passage_metadata = []
        return
    
    try:
        VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
        index_file = VECTOR_DB_PATH / "tafsir_index.faiss"
        metadata_file = VECTOR_DB_PATH / "tafsir_metadata.json"
        
        if index_file.exists() and metadata_file.exists():
            # Load existing index
            logger.info("Loading existing vector index...")
            vector_index = faiss.read_index(str(index_file))
            with open(metadata_file, "r", encoding="utf-8") as f:
                passage_metadata = json.load(f)
            logger.info(f"Loaded {len(passage_metadata)} passages from index")
        else:
            # Build new index (placeholder - would need actual tafsir sources)
            logger.warning("No vector index found. Building placeholder index...")
            logger.warning("Note: You need to provide tafsir source texts to build the index")
            
            # Create empty index
            dimension = embedding_model.get_sentence_embedding_dimension()
            vector_index = faiss.IndexFlatL2(dimension)
            passage_metadata = []
            
            # Save empty index
            faiss.write_index(vector_index, str(index_file))
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(passage_metadata, f, ensure_ascii=False, indent=2)
            
            logger.info("Placeholder index created. Add tafsir sources to build the index.")
    except Exception as e:
        logger.error(f"Error building vector index: {e}", exc_info=True)
        vector_index = None
        passage_metadata = []

# Initialize at startup
try:
    load_embedding_model()
    load_llm_client()
    if embedding_model is not None:
        build_vector_index()
    else:
        logger.warning("Tafsir service will work in LLM-only mode (no RAG)")
except Exception as e:
    logger.error(f"Initialization error: {e}", exc_info=True)

def retrieve_relevant_passages(query: str, top_k: int = RAG_TOP_K) -> List[Dict]:
    """
    Retrieve relevant tafsir passages using semantic search
    
    Args:
        query: User query
        top_k: Number of passages to retrieve
    
    Returns:
        List of relevant passages with metadata
    """
    if vector_index is None or len(passage_metadata) == 0:
        return []
    
    try:
        # Generate query embedding
        query_embedding = embedding_model.encode([query], convert_to_numpy=True)
        query_embedding = query_embedding.astype('float32')
        
        # Search in vector index
        k = min(top_k, len(passage_metadata))
        distances, indices = vector_index.search(query_embedding, k)
        
        # Format results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(passage_metadata):
                similarity = 1 / (1 + distance)  # Convert distance to similarity
                if similarity >= RAG_SIMILARITY_THRESHOLD:
                    passage = passage_metadata[idx].copy()
                    passage["similarity"] = float(similarity)
                    passage["rank"] = i + 1
                    results.append(passage)
        
        return results
    
    except Exception as e:
        logger.error(f"Retrieval error: {e}", exc_info=True)
        return []

def generate_tafsir(query: str, passages: List[Dict], verse_context: Optional[Dict] = None) -> str:
    """
    Generate tafsir response using RAG or LLM-only mode
    
    Args:
        query: User query
        passages: Retrieved relevant passages
        verse_context: Optional verse context
    
    Returns:
        Generated tafsir response (voice-optimized for TTS)
    """
    if llm_client is None:
        return "عذراً، خدمة التفسير غير متاحة حالياً. يرجى المحاولة لاحقاً."
    
    # Build prompt with retrieved context
    context_text = ""
    if passages:
        context_text = "\n\n".join([
            f"Source: {p.get('source', 'Unknown')}\n"
            f"Passage: {p.get('text', '')}"
            for p in passages[:3]  # Use top 3 passages
        ])
    
    verse_text = ""
    if verse_context:
        verse_text = f"\nVerse: {verse_context.get('verse_text', '')}"
    
    # Voice-optimized prompt for TTS
    prompt = f"""أنت خبير في تفسير القرآن الكريم. مهمتك هي تقديم تفسير واضح ومفيد لمساعدة الناس في حفظ القرآن.

{context_text if context_text else ""}
{verse_text if verse_text else ""}

سؤال المستخدم: {query}

قدم تفسيراً:
1. اشرح معنى الآية (الآيات) بطريقة بسيطة وواضحة
2. استخدم لغة محادثة طبيعية (مناسبة للقراءة الصوتية)
3. كن مشجعاً ومحترماً
4. اجعل الجمل قصيرة ومناسبة للصوت
5. ركز على مساعدة المستخدم في فهم الآية وحفظها

التفسير:"""
    
    try:
        messages = [
            {
                "role": "system", 
                "content": "أنت خبير في تفسير القرآن الكريم. استجاباتك ستُقرأ بصوت عالي، لذا اجعلها طبيعية وواضحة ومناسبة للصوت."
            },
            {"role": "user", "content": prompt}
        ]
        
        # Use exact model card format
        model_name = "openai/gpt-oss-20b"
        
        try:
            completion = llm_client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.5,  # Slightly higher for natural voice
                max_tokens=400  # Shorter for voice responses
            )
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return f"عذراً، حدث خطأ في توليد التفسير: {str(e)}"
        
        response = completion.choices[0].message.content
        
        # Clean response for TTS
        import re
        response = re.sub(r'[.]{2,}', '.', response)
        response = re.sub(r'[!]{2,}', '!', response)
        response = re.sub(r'[?]{2,}', '?', response)
        
        return response
    
    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        return f"عذراً، حدث خطأ في توليد التفسير. يرجى المحاولة مرة أخرى."

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = "healthy"
    if llm_client is None:
        status = "degraded"
    
    return {
        "status": status,
        "embedding_model_loaded": embedding_model is not None,
        "llm_client_initialized": llm_client is not None,
        "vector_index_ready": vector_index is not None and len(passage_metadata) > 0,
        "embedding_model": EMBEDDING_MODEL,
        "llm_model": LLM_MODEL,
        "indexed_passages": len(passage_metadata),
        "mode": "rag" if (embedding_model and vector_index) else "llm_only",
        "service": "tafsir_rag"
    }

@app.post("/tafsir")
async def get_tafsir(request: TafsirRequest):
    """
    Get tafsir (interpretation) for a query
    Works in RAG mode (if available) or LLM-only mode
    
    Args:
        request: TafsirRequest with query and optional verse context
    
    Returns:
        Tafsir response (voice-optimized) with sources
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Check if LLM client is available
        if llm_client is None:
            return JSONResponse(
                {
                    "tafsir": "عذراً، خدمة التفسير غير متاحة حالياً. يرجى التحقق من إعدادات الخدمة.",
                    "sources": [],
                    "retrieved_passages": 0,
                    "status": "error",
                    "message": "LLM client not initialized"
                },
                status_code=503
            )
        
        # Get verse context if provided
        verse_context = None
        if request.surah_index and request.verse_key:
            # Try to load actual verse text from Quran database
            try:
                from config import SURAH_DIR
                surah_file = SURAH_DIR / f"surah_{request.surah_index}.json"
                if surah_file.exists():
                    with open(surah_file, "r", encoding="utf-8") as f:
                        surah_data = json.load(f)
                        if "verse" in surah_data and request.verse_key in surah_data["verse"]:
                            verse_context = {
                                "surah_index": request.surah_index,
                                "verse_key": request.verse_key,
                                "verse_text": surah_data["verse"][request.verse_key]
                            }
            except Exception as e:
                logger.debug(f"Could not load verse context: {e}")
                verse_context = {
                    "surah_index": request.surah_index,
                    "verse_key": request.verse_key
                }
        
        # Retrieve relevant passages (if RAG is available)
        passages = []
        if embedding_model is not None and vector_index is not None:
            logger.info(f"Retrieving passages for query: {request.query[:50]}...")
            passages = retrieve_relevant_passages(request.query, request.top_k)
        else:
            logger.info("RAG not available, using LLM-only mode")
        
        # Generate tafsir (works in both RAG and LLM-only modes)
        logger.info("Generating tafsir response...")
        tafsir_response = generate_tafsir(request.query, passages, verse_context)
        
        return JSONResponse({
            "tafsir": tafsir_response,
            "response_voice_optimized": True,  # Mark as voice-optimized
            "sources": [p.get("source", "Unknown") for p in passages] if passages else [],
            "retrieved_passages": len(passages),
            "mode": "rag" if passages else "llm_only",
            "status": "success"
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tafsir error: {e}", exc_info=True)
        return JSONResponse(
            {
                "error": str(e),
                "tafsir": "عذراً، حدث خطأ في خدمة التفسير. يرجى المحاولة مرة أخرى.",
                "status": "error"
            },
            status_code=500
        )

@app.post("/add_passages")
async def add_passages(passages: List[Dict]):
    """
    Add tafsir passages to the vector index (for building the knowledge base)
    
    Args:
        passages: List of passage dictionaries with 'text' and 'source' fields
    
    Returns:
        Confirmation of added passages
    """
    try:
        if embedding_model is None:
            raise HTTPException(status_code=503, detail="Embedding model not loaded")
        
        # Generate embeddings
        texts = [p.get("text", "") for p in passages]
        embeddings = embedding_model.encode(texts, convert_to_numpy=True)
        embeddings = embeddings.astype('float32')
        
        # Add to index
        if vector_index is None:
            dimension = embedding_model.get_sentence_embedding_dimension()
            vector_index = faiss.IndexFlatL2(dimension)
        
        vector_index.add(embeddings)
        
        # Add metadata
        for passage in passages:
            passage_metadata.append(passage)
        
        # Save index
        VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
        index_file = VECTOR_DB_PATH / "tafsir_index.faiss"
        metadata_file = VECTOR_DB_PATH / "tafsir_metadata.json"
        
        faiss.write_index(vector_index, str(index_file))
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(passage_metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Added {len(passages)} passages to index")
        
        return JSONResponse({
            "added": len(passages),
            "total_passages": len(passage_metadata),
            "status": "success"
        })
    
    except Exception as e:
        logger.error(f"Add passages error: {e}", exc_info=True)
        return JSONResponse(
            {"error": str(e), "status": "error"},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    
    # Get port from config or use default
    try:
        from config import TAFSIR_SERVICE_PORT
        port = TAFSIR_SERVICE_PORT
    except ImportError:
        port = 8004
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

