# Multi-Agent Voice Quran Assistant - Complete System Documentation

**Author:** Yahya Alnwsany  
**Version:** 1.0.0  
**Date:** 2025

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Configuration System](#configuration-system)
4. [Core Services](#core-services)
5. [API Gateway](#api-gateway)
6. [Web Interface](#web-interface)
7. [Data Flow](#data-flow)
8. [Setup and Deployment](#setup-and-deployment)

---

## System Overview

The **Multi-Agent Voice Quran Assistant** is a comprehensive voice-enabled system designed to help users memorize and learn the Quran through interactive voice interaction. The system uses a microservices architecture with specialized agents for different tasks:

- **Speech-to-Text (STT)**: Converts Arabic speech to text with diacritics
- **LLM Router**: Acts as the "brain" - classifies intents, routes requests, and provides intelligent responses
- **Quran Validator**: Validates recitation accuracy using LLM as a specialized Quran expert
- **Tafsir RAG**: Provides verse interpretation using Retrieval-Augmented Generation
- **Text-to-Speech (TTS)**: Converts Arabic text responses to speech (placeholder)

The system is optimized for:
- **Voice Assistant Mode**: Natural, conversational Arabic responses optimized for TTS
- **4GB GPU**: Quantized models and optimized batch sizes
- **Arabic Language**: Full support for Arabic text, speech, and responses
- **Quran Memorization**: Specialized feedback for correct/incorrect recitation

---

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│  Web Interface  │ (Port 8080)
│  (User Browser) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API Gateway    │ (Port 8000)
│  (Orchestrator) │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┬──────────┐
    │         │          │          │          │
    ▼         ▼          ▼          ▼          ▼
┌──────┐ ┌────────┐ ┌──────────┐ ┌────────┐ ┌──────┐
│ STT  │ │  LLM   │ │ Validator│ │ Tafsir │ │ TTS  │
│ 8001 │ │ 8002   │ │   8003   │ │  8004  │ │ 8005 │
└──────┘ └────────┘ └──────────┘ └────────┘ └──────┘
```

### Request Flow

1. **User Input** (Voice/Text) → Web Interface
2. **Web Interface** → API Gateway
3. **API Gateway** → STT Service (if voice)
4. **API Gateway** → LLM Router (intent classification)
5. **API Gateway** → Appropriate Service (Validator/Tafsir/LLM)
6. **Service** → Response (Arabic text)
7. **API Gateway** → Web Interface
8. **Web Interface** → User Display

---

## Configuration System

### File: `config.py`

This is the central configuration file that defines all system parameters, paths, and settings.

#### System Identity (Lines 8-11)

```python
SYSTEM_NAME = "Multi-Agent Voice Quran Assistant"
SYSTEM_TYPE = "voice_assistant"  # voice_assistant, api_service, etc.
SYSTEM_PURPOSE = "Quran memorization and learning assistance through voice interaction"
```

**Explanation:**
- `SYSTEM_NAME`: Human-readable name for the system
- `SYSTEM_TYPE`: Defines the operational mode (voice assistant vs API service)
- `SYSTEM_PURPOSE`: Describes the primary goal of the system

#### Hugging Face Configuration (Lines 13-21)

```python
HF_TOKEN = os.getenv("HF_TOKEN", "your_huggingface_token_here")
HF_API_BASE = "https://api-inference.huggingface.co"

if not HF_TOKEN or HF_TOKEN == "your_huggingface_token_here":
    import warnings
    warnings.warn("HF_TOKEN not set! Please set it as an environment variable.")
```

**Explanation:**
- `HF_TOKEN`: Hugging Face API token for accessing models
  - First tries to get from environment variable `HF_TOKEN`
  - Falls back to default token if not set
  - This token is required for LLM and other HF model access
- `HF_API_BASE`: Base URL for Hugging Face Inference API
- **Warning System**: If token is not properly set, a warning is issued

#### Model Paths (Lines 23-27)

```python
STT_MODEL = "nvidia/stt_ar_fastconformer_hybrid_large_pcd_v1.0"
LLM_MODEL = "openai/gpt-oss-20b"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
TTS_MODEL = "AhmedEladl/saudi-tts"
```

**Explanation:**
- `STT_MODEL`: NVIDIA's Arabic FastConformer model for speech recognition
  - Hybrid architecture (RNN-T + CTC)
  - Large model with punctuation and diacritics
  - Optimized for Arabic Quranic recitation
- `LLM_MODEL`: OpenAI's GPT-OSS-20B model
  - Acts as the "brain" of the system
  - Handles intent classification, routing, and text generation
  - Accessed via Hugging Face Inference API
- `EMBEDDING_MODEL`: Multilingual sentence transformer
  - Used for RAG (Retrieval-Augmented Generation) in Tafsir service
  - Supports Arabic and other languages
  - 768-dimensional embeddings
- `TTS_MODEL`: Saudi TTS model (placeholder)
  - Currently not integrated
  - Will be used for Arabic speech synthesis

#### Voice Assistant Configuration (Lines 29-33)

```python
VOICE_ASSISTANT_MODE = True
RESPONSE_OPTIMIZED_FOR_TTS = True
CONVERSATIONAL_MODE = True
LANGUAGE = "ar"
```

**Explanation:**
- `VOICE_ASSISTANT_MODE`: Enables voice assistant behavior
  - System responds as a voice assistant, not just an API
  - Responses are conversational and natural
- `RESPONSE_OPTIMIZED_FOR_TTS`: Responses are designed for text-to-speech
  - Shorter sentences
  - Clear pronunciation
  - Natural flow for voice
- `CONVERSATIONAL_MODE`: Enables natural conversation
  - Not formal/robotic responses
  - Encouraging and helpful tone
- `LANGUAGE`: Primary language is Arabic ("ar")

#### Data Paths (Lines 35-43)

```python
BASE_DIR = Path(__file__).parent
QURAN_DATA_DIR = BASE_DIR / "Quran_Data" / "data"
SURAH_DIR = QURAN_DATA_DIR / "surah"
JUZ_FILE = QURAN_DATA_DIR / "juz.json"
SURAH_INDEX_FILE = QURAN_DATA_DIR / "surah.json"
AUDIO_DIR = QURAN_DATA_DIR / "audio"
TAJWEED_DIR = QURAN_DATA_DIR / "tajweed"
TRANSLATION_DIR = QURAN_DATA_DIR / "translation"
```

**Explanation:**
- `BASE_DIR`: Root directory of the project
  - Uses `Path(__file__).parent` to get directory containing config.py
- `QURAN_DATA_DIR`: Main data directory containing all Quran data
- `SURAH_DIR`: Directory with individual surah JSON files (surah_001.json, etc.)
- `JUZ_FILE`: JSON file mapping juz (30 parts) to surahs and verses
- `SURAH_INDEX_FILE`: JSON file with metadata for all 114 surahs
- `AUDIO_DIR`: Directory containing audio files for each verse
- `TAJWEED_DIR`: Directory with tajweed rules for each surah
- `TRANSLATION_DIR`: Directory with translations in multiple languages

#### Service Configuration (Lines 45-51)

```python
STT_SERVICE_PORT = 8001
LLM_SERVICE_PORT = 8002
VALIDATOR_SERVICE_PORT = 8003
TAFSIR_SERVICE_PORT = 8004
TTS_SERVICE_PORT = 8005
API_GATEWAY_PORT = 8000
```

**Explanation:**
- Each microservice runs on a dedicated port
- Ports are non-conflicting and sequential for easy management
- API Gateway (8000) is the main entry point

#### Device Configuration (Lines 53-57)

```python
USE_CUDA = True
DEVICE = "cuda" if USE_CUDA else "cpu"
MAX_BATCH_SIZE = 1
USE_QUANTIZATION = True
```

**Explanation:**
- `USE_CUDA`: Enable GPU acceleration if available
- `DEVICE`: Automatically selects CUDA or CPU
- `MAX_BATCH_SIZE = 1`: Optimized for 4GB GPU (reduced batch size)
- `USE_QUANTIZATION`: Enable model quantization to fit in 4GB GPU memory

#### Vector Database Configuration (Lines 59-62)

```python
VECTOR_DB_TYPE = "faiss"
VECTOR_DB_PATH = BASE_DIR / "vector_db"
EMBEDDING_DIM = 768
```

**Explanation:**
- `VECTOR_DB_TYPE`: Uses FAISS for vector similarity search
- `VECTOR_DB_PATH`: Directory where vector index is stored
- `EMBEDDING_DIM`: Dimension of embeddings (768 for multilingual-mpnet-base-v2)

#### Validation Configuration (Lines 64-67)

```python
LEVENSHTEIN_THRESHOLD = 0.85
TOP_K_VERSES = 5
FUZZY_MATCH_ENABLED = True
```

**Explanation:**
- `LEVENSHTEIN_THRESHOLD`: Similarity threshold for fuzzy matching (85% match)
- `TOP_K_VERSES`: Number of top matching verses to return
- `FUZZY_MATCH_ENABLED`: Enable fuzzy string matching (currently deprecated in favor of LLM validation)

#### RAG Configuration (Lines 69-73)

```python
RAG_TOP_K = 5
RAG_SIMILARITY_THRESHOLD = 0.7
RAG_CHUNK_SIZE = 300
RAG_CHUNK_OVERLAP = 50
```

**Explanation:**
- `RAG_TOP_K`: Number of relevant passages to retrieve for RAG
- `RAG_SIMILARITY_THRESHOLD`: Minimum similarity score for retrieved passages
- `RAG_CHUNK_SIZE`: Size of text chunks for embedding (300 characters)
- `RAG_CHUNK_OVERLAP`: Overlap between chunks to preserve context (50 characters)

---

## Core Services

### 1. STT Service (`services/stt_service.py`)

**Purpose:** Converts Arabic speech to text with diacritics (tashkeel)

#### Key Components

**Lines 1-9: Imports and Path Setup**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Explanation:**
- Adds parent directory to Python path so `config.py` can be imported
- This is necessary because services are in a subdirectory

**Lines 11-17: NeMo ASR Import**
```python
import nemo.collections.asr as nemo_asr
import torch
```

**Explanation:**
- `nemo.collections.asr`: NVIDIA NeMo's Automatic Speech Recognition collection
- `torch`: PyTorch for tensor operations

**Lines 20-27: Configuration Loading**
```python
try:
    from config import STT_MODEL, DEVICE
    MODEL_NAME = STT_MODEL
    USE_DEVICE = DEVICE
except ImportError:
    MODEL_NAME = "nvidia/stt_ar_fastconformer_hybrid_large_pcd_v1.0"
    USE_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
```

**Explanation:**
- Tries to import from config.py
- Falls back to defaults if config not found
- Ensures service can start even if config is missing

**Lines 32-48: Model Loading**
```python
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE}")

logger.info(f"Loading Arabic NeMo model: {MODEL_NAME}")
try:
    model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel.from_pretrained(
        model_name=MODEL_NAME,
        map_location=DEVICE
    )
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load STT model: {e}", exc_info=True)
    model = None
    logger.warning("STT service will start but model is not available")
```

**Explanation:**
- **Device Selection**: Automatically detects CUDA availability
- **Model Loading**: Uses `EncDecHybridRNNTCTCBPEModel` - hybrid architecture combining:
  - **RNN-T (Recurrent Neural Network Transducer)**: For streaming recognition
  - **CTC (Connectionist Temporal Classification)**: For alignment
  - **BPE (Byte Pair Encoding)**: For subword tokenization
- **Error Handling**: If model fails to load, service still starts but marks model as unavailable
- **Graceful Degradation**: Service can report its status even if model isn't loaded

**Lines 50-54: FastAPI App Initialization**
```python
app = FastAPI(
    title="Arabic STT Service",
    description="Speech-to-Text service for Arabic Quranic recitation",
    version="1.0.0"
)
```

**Explanation:**
- Creates FastAPI application
- Sets metadata for API documentation

**Lines 56-63: CORS Middleware**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Explanation:**
- **CORS (Cross-Origin Resource Sharing)**: Allows web interface to call the service
- `allow_origins=["*"]`: Allows requests from any origin (development mode)
- In production, should restrict to specific domains

**Lines 65-73: Health Check Endpoint**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if model is not None else "model_unavailable",
        "model": MODEL_NAME,
        "device": DEVICE,
        "model_loaded": model is not None
    }
```

**Explanation:**
- Returns service health status
- Indicates if model is loaded
- Used by API Gateway to check service availability

**Lines 75-117: Transcription Endpoint**
```python
@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    if model is None:
        return JSONResponse(
            {"error": "STT model not loaded. Please check service logs."},
            status_code=503
        )
    
    try:
        # Save uploaded file temporarily
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        try:
            # Run transcription
            logger.info(f"Transcribing file: {file.filename}")
            result = model.transcribe([tmp_path])
            transcript = result[0].text

            logger.info(f"Transcription successful: {len(transcript)} characters")

            return JSONResponse({
                "transcript": transcript,
                "status": "success"
            })

        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
```

**Explanation:**
- **Input**: Accepts audio file upload (MP3, WAV, etc.)
- **Temporary File**: Saves uploaded file to disk temporarily
  - Preserves original file extension
  - Uses `tempfile.NamedTemporaryFile` for secure temporary storage
- **Transcription**: Calls `model.transcribe()` with file path
  - Model returns list of transcription results
  - Extracts text from first result
- **Cleanup**: Always removes temporary file, even if error occurs
- **Response**: Returns JSON with transcript and status

### 2. LLM Router Service (`services/llm_router.py`)

**Purpose:** Acts as the "brain" of the system - classifies intents, routes requests, and provides intelligent responses

#### Key Components

**Lines 17-27: Hugging Face Client Initialization**
```python
from huggingface_hub import InferenceClient

try:
    from config import HF_TOKEN, LLM_MODEL
except ImportError:
    HF_TOKEN = os.getenv("HF_TOKEN", "")
    LLM_MODEL = "openai/gpt-oss-20b"

client = InferenceClient(api_key=HF_TOKEN)
```

**Explanation:**
- `InferenceClient`: Hugging Face's client for accessing models via API
- Initializes client with API token
- Falls back to environment variable if config not found

**Lines 50-58: Intent Types**
```python
IntentType = Literal[
    "recitation_validation",
    "translation_request",
    "tafsir_query",
    "general_qa",
    "verse_lookup",
    "other_nlp_tasks"
]
```

**Explanation:**
- Defines all possible user intents
- `Literal`: Type hint for exact string values
- Used for type checking and validation

**Lines 79-90: System Prompts**
```python
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
```

**Explanation:**
- **Arabic System Prompts**: All prompts are in Arabic for better LLM understanding
- **Intent Classification Prompt**: Instructs LLM to classify user intent
- **Clear Instructions**: Lists all possible intents with descriptions
- **Output Format**: Asks for intent name only

**Lines 100-150: Intent Classification Endpoint**
```python
@app.post("/classify_intent")
async def classify_intent(request: IntentRequest):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPTS["intent_classification"]},
        {"role": "user", "content": request.text}
    ]
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        max_tokens=20,
        temperature=0.1
    )
    
    intent = completion.choices[0].message.content.strip()
    return JSONResponse({"intent": intent})
```

**Explanation:**
- **Input**: User text
- **Messages Format**: OpenAI-compatible chat format
  - `system`: Instructions for the LLM
  - `user`: User's input text
- **Model Call**: Uses `client.chat.completions.create()`
  - `model`: Hardcoded to "openai/gpt-oss-20b" (exact model card format)
  - `max_tokens=20`: Short response (just intent name)
  - `temperature=0.1`: Low temperature for consistent classification
- **Response**: Returns classified intent

**Lines 200-400: Validation Endpoint (`/validate_recitation`)**

This is the most complex endpoint. Let's break it down:

**Lines 200-250: Database Search**
```python
# Load Quran database
BASE_DIR = Path(__file__).parent.parent
QURAN_DATA_DIR = BASE_DIR / "Quran_Data" / "data"
SURAH_DIR = QURAN_DATA_DIR / "surah"

# Find best matching verse from database
best_match = None
best_similarity = 0.0

# Normalize user text for comparison
def normalize_text(text):
    # Remove diacritics for comparison
    text = re.sub(r'[\u064B-\u0652\u0654-\u065F\u0670]', '', text)
    # Normalize Arabic characters
    text = text.replace('\u0623', '\u0627').replace('\u0625', '\u0627')
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

user_text_normalized = normalize_text(request.text)

# Search through all surahs
for surah_file in SURAH_DIR.glob("surah_*.json"):
    with open(surah_file, "r", encoding="utf-8") as f:
        surah_data = json.load(f)
        if "verse" in surah_data:
            for verse_key, verse_text in surah_data["verse"].items():
                verse_normalized = normalize_text(verse_text)
                similarity = SequenceMatcher(None, user_text_normalized, verse_normalized).ratio()
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = {...}
```

**Explanation:**
- **Database Loading**: Loads all surah JSON files
- **Text Normalization**: 
  - Removes diacritics (tashkeel) for comparison
  - Normalizes Arabic character variants (أ, إ, آ → ا)
  - Removes extra spaces
- **Similarity Search**: Uses `SequenceMatcher` (Levenshtein distance) to find best match
- **Best Match Tracking**: Keeps track of highest similarity score and matching verse

**Lines 250-300: Tajweed Rules Loading**
```python
tajweed_info = ""
tajweed_rules_list = []
if matched_surah_index and matched_verse_key:
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
                    # Translate rule names to Arabic
                    rule_translations = {
                        "hamzat_wasl": "همزة الوصل",
                        "madd_2": "مد طبيعي (مدتين)",
                        ...
                    }
```

**Explanation:**
- **Tajweed Loading**: Loads tajweed rules for matched verse
- **Rule Translation**: Translates English rule names to Arabic
- **Formatting**: Formats rules for LLM context

**Lines 300-400: LLM Validation Prompt**
```python
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
   ...

أجب بصيغة JSON فقط:
{{"is_correct": true/false, "feedback": "ردك بالعربية", ...}}"""
```

**Explanation:**
- **Specialized Expert Prompt**: Instructs LLM to act as Quran expert
- **Context Injection**: Includes matched verse from database
- **Tajweed Instructions**: Detailed instructions on tajweed rules
- **JSON Format**: Requests structured JSON response

**Lines 400-500: LLM Call and Response Parsing**
```python
try:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        max_tokens=600,
        temperature=0.1,
        response_format={"type": "json_object"}
    )
except Exception as e:
    # Fallback: ask LLM to return JSON in text
    messages_with_json_instruction = messages.copy()
    messages_with_json_instruction[-1]["content"] += "\n\nأجب بصيغة JSON فقط: ..."
    completion = client.chat.completions.create(...)

llm_response = completion.choices[0].message.content
result = json.loads(llm_response)
```

**Explanation:**
- **JSON Format Request**: Tries to get structured JSON response
- **Fallback Mechanism**: If JSON format fails, adds instruction to prompt
- **Response Parsing**: Parses JSON response
- **Error Handling**: Graceful fallback if parsing fails

### 3. Quran Validator Service (`services/quran_validator.py`)

**Purpose:** Validates Quranic recitation using fuzzy matching (currently deprecated in favor of LLM validation)

**Note:** This service is kept for reference but the main validation now happens in LLM Router's `/validate_recitation` endpoint.

#### Key Components

**Lines 71-100: Database Loading**
```python
def load_quran_database():
    global quran_database, verse_index
    
    logger.info("Loading Quran database...")
    
    # Load surah index
    with open(QURAN_DATA_DIR / "surah.json", "r", encoding="utf-8") as f:
        surah_index = json.load(f)
    
    # Load all surahs
    for surah_file in SURAH_DIR.glob("surah_*.json"):
        with open(surah_file, "r", encoding="utf-8") as f:
            surah_data = json.load(f)
            surah_num = surah_data["index"]
            quran_database[surah_num] = surah_data
            
            # Index all verses for fast lookup
            if "verse" in surah_data:
                for verse_key, verse_text in surah_data["verse"].items():
                    verse_index[verse_text] = {
                        "surah_index": surah_num,
                        "surah_name": surah_data.get("name", ""),
                        "verse_key": verse_key
                    }
```

**Explanation:**
- **Database Loading**: Loads all surah files into memory
- **Verse Indexing**: Creates fast lookup dictionary
- **Memory Optimization**: Stores all verses for quick access

**Lines 100-200: Fuzzy Matching**
```python
def find_best_match(user_text: str, threshold: float = LEVENSHTEIN_THRESHOLD):
    best_matches = []
    
    # Normalize text
    user_normalized = normalize_arabic_text(user_text)
    
    for verse_text, verse_info in verse_index.items():
        verse_normalized = normalize_arabic_text(verse_text)
        similarity = SequenceMatcher(None, user_normalized, verse_normalized).ratio()
        
        if similarity >= threshold:
            best_matches.append({
                "verse_text": verse_text,
                "similarity": similarity,
                **verse_info
            })
    
    # Sort by similarity
    best_matches.sort(key=lambda x: x["similarity"], reverse=True)
    return best_matches[:TOP_K_VERSES]
```

**Explanation:**
- **Text Normalization**: Normalizes both user text and verse text
- **Similarity Calculation**: Uses SequenceMatcher (Levenshtein distance)
- **Threshold Filtering**: Only returns matches above threshold
- **Top-K Selection**: Returns top K matches sorted by similarity

### 4. Tafsir RAG Service (`services/tafsir_rag.py`)

**Purpose:** Provides verse interpretation using Retrieval-Augmented Generation

#### Key Components

**Lines 37-46: Optional Dependencies**
```python
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import faiss
    from huggingface_hub import InferenceClient
    HAS_DEPENDENCIES = True
except ImportError as e:
    HAS_DEPENDENCIES = False
    logging.warning(f"Some dependencies not available: {e}. RAG features will be limited.")
```

**Explanation:**
- **Graceful Degradation**: Service can run even if RAG dependencies are missing
- **LLM-Only Mode**: Falls back to LLM-only generation if RAG components unavailable
- **Dependency Check**: Tracks which components are available

**Lines 77-90: Embedding Model Loading**
```python
def load_embedding_model():
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
```

**Explanation:**
- **Model Loading**: Loads sentence transformer for embeddings
- **Error Handling**: Sets model to None if loading fails
- **Service Continuity**: Service can still run in LLM-only mode

**Lines 110-150: Vector Index Building**
```python
def build_vector_index():
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
            # Build new index (placeholder)
            logger.warning("No vector index found. Building placeholder index...")
            dimension = embedding_model.get_sentence_embedding_dimension()
            vector_index = faiss.IndexFlatL2(dimension)
            passage_metadata = []
```

**Explanation:**
- **Index Persistence**: Saves/loads vector index from disk
- **FAISS Index**: Uses FAISS for efficient similarity search
- **Metadata Storage**: Stores passage metadata separately
- **Placeholder Mode**: Creates empty index if no data available

**Lines 200-300: RAG Retrieval**
```python
def retrieve_relevant_passages(query: str, top_k: int = RAG_TOP_K):
    if vector_index is None or embedding_model is None:
        return []
    
    # Embed query
    query_embedding = embedding_model.encode(query, convert_to_numpy=True)
    query_embedding = query_embedding.reshape(1, -1)
    
    # Search
    distances, indices = vector_index.search(query_embedding, top_k)
    
    # Filter by similarity threshold
    passages = []
    for i, idx in enumerate(indices[0]):
        if distances[0][i] <= RAG_SIMILARITY_THRESHOLD:
            if idx < len(passage_metadata):
                passages.append(passage_metadata[idx])
    
    return passages
```

**Explanation:**
- **Query Embedding**: Converts query text to vector
- **Similarity Search**: Searches vector index for similar passages
- **Threshold Filtering**: Only returns passages above similarity threshold
- **Metadata Retrieval**: Returns full passage metadata, not just indices

**Lines 300-400: Tafsir Generation**
```python
@app.post("/tafsir")
async def get_tafsir(request: TafsirRequest):
    # Determine if RAG is fully functional
    is_rag_functional = (embedding_model is not None and 
                        vector_index is not None and 
                        len(passage_metadata) > 0)

    if is_rag_functional:
        # Retrieve relevant passages
        passages = retrieve_relevant_passages(request.query, request.top_k)
        
        # Generate tafsir using RAG
        tafsir_response = generate_tafsir(request.query, passages, verse_context)
        
        return JSONResponse({
            "tafsir": tafsir_response,
            "mode": "rag",
            "sources": [p.get("source", "Unknown") for p in passages]
        })
    else:
        # Fallback to LLM-only mode
        logger.warning("RAG components not fully available. Falling back to LLM-only mode.")
        
        system_prompt = """أنت خبير في تفسير القرآن الكريم..."""
        
        completion = llm_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"اشرح لي معنى: {request.query}"}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        return JSONResponse({
            "tafsir": completion.choices[0].message.content,
            "mode": "llm_only"
        })
```

**Explanation:**
- **Mode Detection**: Checks if RAG is fully functional
- **RAG Mode**: If available, retrieves passages and generates with context
- **LLM-Only Mode**: Falls back to direct LLM generation if RAG unavailable
- **Voice Optimization**: System prompts optimized for voice/TTS

### 5. TTS Service (`services/tts_service.py`)

**Purpose:** Text-to-Speech synthesis (currently placeholder)

**Note:** This service is a placeholder until TTS API integration is completed.

#### Key Components

**Lines 49-73: Placeholder Endpoint**
```python
@app.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Placeholder response
        logger.warning("TTS service is a placeholder. API integration needed.")
        
        return JSONResponse({
            "status": "placeholder",
            "message": "TTS service is not yet implemented. Please integrate AhmedEladl/saudi-tts API when available.",
            "text": request.text,
            "voice": request.voice,
            "speed": request.speed
        })
```

**Explanation:**
- **Placeholder Implementation**: Returns placeholder response
- **Future Integration**: Will integrate AhmedEladl/saudi-tts when API is available
- **Request Validation**: Still validates input for future implementation

---

## API Gateway

### File: `api_gateway.py`

**Purpose:** Main entry point that orchestrates requests across all microservices

#### Key Components

**Lines 13-16: Service URL Configuration**
```python
from config import (
    STT_SERVICE_PORT, LLM_SERVICE_PORT, VALIDATOR_SERVICE_PORT,
    TAFSIR_SERVICE_PORT, TTS_SERVICE_PORT, API_GATEWAY_PORT
)
```

**Explanation:**
- Imports service ports from config
- Centralized configuration

**Lines 35-42: Service URLs**
```python
SERVICE_URLS = {
    "stt": f"http://localhost:{STT_SERVICE_PORT}",
    "llm": f"http://localhost:{LLM_SERVICE_PORT}",
    "validator": f"http://localhost:{VALIDATOR_SERVICE_PORT}",
    "tafsir": f"http://localhost:{TAFSIR_SERVICE_PORT}",
    "tts": f"http://localhost:{TTS_SERVICE_PORT}"
}
```

**Explanation:**
- Maps service names to URLs
- Uses localhost for local deployment
- Easy to change for distributed deployment

**Lines 95-197: Voice Query Endpoint**

This is the main endpoint that handles complete voice queries:

**Step 1: Speech-to-Text (Lines 115-132)**
```python
logger.info("Step 1: Converting speech to text...")
async with httpx.AsyncClient(timeout=30.0) as client:
    files = {"file": (file.filename, await file.read(), file.content_type)}
    stt_response = await client.post(
        f"{SERVICE_URLS['stt']}/transcribe",
        files=files
    )
    
    if stt_response.status_code != 200:
        raise HTTPException(...)
    
    stt_data = stt_response.json()
    transcript = stt_data.get("transcript", "")
```

**Explanation:**
- **Async HTTP Client**: Uses `httpx.AsyncClient` for async requests
- **File Upload**: Forwards audio file to STT service
- **Error Handling**: Raises exception if STT fails
- **Transcript Extraction**: Gets transcript from response

**Step 2: Intent Classification (Lines 142-156)**
```python
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
```

**Explanation:**
- **Intent Detection**: Sends transcript to LLM Router
- **Fallback**: Uses default intent if classification fails
- **Error Resilience**: System continues even if intent classification fails

**Step 3: Processing (Lines 159-161)**
```python
logger.info("Step 3: Processing request...")
result = await process_intent(intent, transcript)
```

**Explanation:**
- Calls `process_intent` function to handle the request
- See below for details

**Lines 254-383: Process Intent Function**

This function routes requests to appropriate services based on intent:

**Recitation Validation (Lines 267-307)**
```python
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
```

**Explanation:**
- **Direct LLM Validation**: Uses LLM Router's `/validate_recitation` endpoint
- **Response Extraction**: Extracts feedback, corrections, and matched verse
- **Arabic Response**: Ensures response is in Arabic
- **Fallback Messages**: Provides default messages if LLM doesn't return feedback

**Tafsir Query (Lines 309-346)**
```python
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
                            "content": "أنت مساعد لمساعدة الناس في حفظ القرآن..."
                        },
                        {"role": "user", "content": f"اشرح لي هذه الآية: {text}"}
                    ]
                }
            )
            ...
```

**Explanation:**
- **Tafsir Service Call**: Calls Tafsir RAG service
- **Fallback to LLM**: If Tafsir fails, uses LLM directly
- **Memorization Focus**: System prompts emphasize helping with memorization

**General QA (Lines 356-378)**
```python
elif intent == "general_qa":
    # General QA using LLM - Arabic responses for memorization help
    llm_response = await client.post(
        f"{SERVICE_URLS['llm']}/chat",
        json={
            "messages": [
                {
                    "role": "system", 
                    "content": "أنت مساعد ذكي لمساعدة الناس في حفظ القرآن الكريم..."
                },
                {"role": "user", "content": text}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
    )
```

**Explanation:**
- **Direct LLM Chat**: Uses LLM Router's `/chat` endpoint
- **Voice Assistant Prompt**: System prompt configures LLM as voice assistant
- **Arabic Responses**: Ensures all responses are in Arabic

---

## Web Interface

### File: `web_interface/index.html`

**Purpose:** User-facing web interface for interacting with the system

#### Key Components

**HTML Structure:**
- Input fields for text and audio
- Buttons for validation and chat
- Display area for responses
- Service status indicators

### File: `web_interface/app.js`

**Purpose:** Client-side JavaScript for handling user interactions

#### Key Components

**Lines 1-3: API Configuration**
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

**Explanation:**
- Base URL for API Gateway
- All requests go through API Gateway

**Lines 28-42: Health Check**
```javascript
async function checkServiceHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy' || data.status === 'degraded') {
            updateStatus('ready', 'جاهز - Ready');
        } else {
            updateStatus('error', 'خدمة غير متاحة - Service Unavailable');
        }
    } catch (error) {
        updateStatus('error', 'لا يمكن الاتصال بالخادم - Cannot connect to server');
    }
}
```

**Explanation:**
- **Health Check**: Checks if API Gateway and services are running
- **Status Updates**: Updates UI based on health status
- **Error Handling**: Shows error message if connection fails

**Lines 99-150: Validation Function**
```javascript
async function validateText() {
    const text = verseText.value.trim();
    if (!text) {
        showError('يرجى إدخال نص للتحقق');
        return;
    }
    
    updateStatus('loading', 'جاري التحقق...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/text_query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });
        
        const data = await response.json();
        
        if (data.intent === 'recitation_validation') {
            // Parse validation response
            const result = data.result;
            displayValidationResult(result);
        } else {
            // General response
            displayResponse(data.response);
        }
    } catch (error) {
        showError('حدث خطأ أثناء التحقق');
    }
}
```

**Explanation:**
- **Text Validation**: Sends text to API Gateway
- **Intent Detection**: Checks if response is validation or general
- **Response Display**: Displays appropriate response format
- **Error Handling**: Shows error message if request fails

**Lines 150-200: Response Display**
```javascript
function displayValidationResult(result) {
    const feedback = result.feedback || result.response_arabic || '';
    const isCorrect = result.is_correct || false;
    const corrections = result.corrections || [];
    const matchedVerse = result.matched_verse || '';
    
    let html = `
        <div class="result ${isCorrect ? 'correct' : 'incorrect'}">
            <h3>${isCorrect ? '✓ صحيح' : '✗ يحتاج تحسين'}</h3>
            <p>${feedback}</p>
            ${matchedVerse ? `<p class="verse">${matchedVerse}</p>` : ''}
            ${corrections.length > 0 ? `<ul>${corrections.map(c => `<li>${c}</li>`).join('')}</ul>` : ''}
        </div>
    `;
    
    validationResult.innerHTML = html;
}
```

**Explanation:**
- **Result Parsing**: Extracts feedback, corrections, and matched verse
- **Visual Feedback**: Shows green for correct, red for incorrect
- **Arabic Display**: All text displayed in Arabic
- **Structured Display**: Shows corrections as list if available

---

## Data Flow

### Complete Request Flow

1. **User Input** (Voice or Text)
   - User speaks or types in web interface

2. **Web Interface** (`web_interface/app.js`)
   - Captures input
   - Sends to API Gateway

3. **API Gateway** (`api_gateway.py`)
   - Receives request
   - If voice: forwards to STT service
   - Gets transcript

4. **Intent Classification** (`services/llm_router.py`)
   - API Gateway sends transcript to LLM Router
   - LLM classifies intent (recitation_validation, tafsir_query, etc.)

5. **Service Routing** (`api_gateway.py` → `process_intent()`)
   - Based on intent, routes to appropriate service:
     - `recitation_validation` → LLM Router `/validate_recitation`
     - `tafsir_query` → Tafsir RAG service
     - `general_qa` → LLM Router `/chat`

6. **Service Processing**
   - Service processes request
   - Returns Arabic response

7. **Response Return**
   - API Gateway formats response
   - Returns to web interface
   - Web interface displays to user

### Data Structures

#### Quran Data Structure

**Surah File** (`Quran_Data/data/surah/surah_001.json`):
```json
{
    "index": "001",
    "name": "al-Fatihah",
    "verse": {
        "verse_1": "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ",
        "verse_2": "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ",
        ...
    },
    "count": 7,
    "juz": [
        {
            "index": "01",
            "verse": {
                "start": "verse_1",
                "end": "verse_7"
            }
        }
    ]
}
```

**Tajweed File** (`Quran_Data/data/tajweed/surah_001.json`):
```json
{
    "verse": {
        "verse_1": [
            {
                "rule": "hamzat_wasl",
                "start": 0,
                "end": 1
            },
            {
                "rule": "madd_2",
                "start": 5,
                "end": 6
            }
        ]
    }
}
```

---

## Setup and Deployment

### Prerequisites

1. **Python 3.8+**
2. **CUDA-capable GPU** (4GB+ VRAM recommended)
3. **WSL (Windows Subsystem for Linux)** for Windows users
4. **Hugging Face Token** (for LLM access)

### Installation Steps

1. **Clone/Download Project**
   ```bash
   cd /path/to/Qurani
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**
   ```bash
   export HF_TOKEN="your_huggingface_token_here"
   ```

5. **Start Services**
   ```bash
   python start_services.py
   ```

   Or use the startup script:
   ```bash
   ./scripts/start_system.sh
   ```

6. **Start Web Interface**
   ```bash
   python web_server.py
   ```

7. **Access Interface**
   - Main Interface: http://localhost:8080
   - Test Interface: http://localhost:8080/test
   - API Docs: http://localhost:8000/docs

### Service Management

**Start All Services:**
```bash
./scripts/start_system.sh
```

**Stop All Services:**
```bash
./scripts/stop_all.sh
```

**Check Service Health:**
```bash
./scripts/check_services.sh
```

### Troubleshooting

See `docs/TROUBLESHOOTING.md` for common issues and solutions.

---

## Summary

This system is a comprehensive multi-agent voice assistant for Quran memorization. It uses:

- **Microservices Architecture**: Separate services for different tasks
- **LLM as Brain**: GPT-OSS-20B acts as intelligent router and validator
- **Arabic-First**: All responses and processing in Arabic
- **Voice-Optimized**: Responses designed for text-to-speech
- **Quran Database**: Complete Quran data with tajweed rules
- **Graceful Degradation**: Services can run even if some components fail

The system is designed to be:
- **Scalable**: Microservices can be deployed separately
- **Maintainable**: Clear separation of concerns
- **Extensible**: Easy to add new services or features
- **User-Friendly**: Simple web interface for interaction

---

**End of Documentation**

