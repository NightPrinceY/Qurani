"""
Configuration file for Multi-Agent Voice Quran Assistant
Voice Assistant System for Quran Memorization
"""
import os
from pathlib import Path

# System Identity
SYSTEM_NAME = "Multi-Agent Voice Quran Assistant"
SYSTEM_TYPE = "voice_assistant"  # voice_assistant, api_service, etc.
SYSTEM_PURPOSE = "Quran memorization and learning assistance through voice interaction"

# Hugging Face Configuration
# Get token from environment variable or use default (for development)
HF_TOKEN = os.getenv("HF_TOKEN", "your_huggingface_token_here")
HF_API_BASE = "https://api-inference.huggingface.co"

# Validate token
if not HF_TOKEN or HF_TOKEN == "your_huggingface_token_here":
    import warnings
    warnings.warn("HF_TOKEN not set! Please set it as an environment variable.")

# Model Paths
STT_MODEL = "nvidia/stt_ar_fastconformer_hybrid_large_pcd_v1.0"
LLM_MODEL = "openai/gpt-oss-20b"  # The "brain" between STT and TTS (via Hugging Face Inference API)
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
TTS_MODEL = "AhmedEladl/saudi-tts"  # Placeholder until API found

# Voice Assistant Configuration
VOICE_ASSISTANT_MODE = True  # System operates as voice assistant
RESPONSE_OPTIMIZED_FOR_TTS = True  # Responses optimized for text-to-speech
CONVERSATIONAL_MODE = True  # Natural, conversational responses
LANGUAGE = "ar"  # Primary language: Arabic

# Data Paths
BASE_DIR = Path(__file__).parent
QURAN_DATA_DIR = BASE_DIR / "Quran_Data" / "data"
SURAH_DIR = QURAN_DATA_DIR / "surah"
JUZ_FILE = QURAN_DATA_DIR / "juz.json"
SURAH_INDEX_FILE = QURAN_DATA_DIR / "surah.json"
AUDIO_DIR = QURAN_DATA_DIR / "audio"
TAJWEED_DIR = QURAN_DATA_DIR / "tajweed"
TRANSLATION_DIR = QURAN_DATA_DIR / "translation"

# Service Configuration
STT_SERVICE_PORT = 8001
LLM_SERVICE_PORT = 8002
VALIDATOR_SERVICE_PORT = 8003
TAFSIR_SERVICE_PORT = 8004
TTS_SERVICE_PORT = 8005
API_GATEWAY_PORT = 8000

# Device Configuration (optimized for 4GB GPU)
USE_CUDA = True
DEVICE = "cuda" if USE_CUDA else "cpu"
MAX_BATCH_SIZE = 1  # Reduced for 4GB GPU
USE_QUANTIZATION = True  # Enable quantization to fit in 4GB

# Vector Database Configuration
VECTOR_DB_TYPE = "faiss"  # Options: faiss, chroma, weaviate
VECTOR_DB_PATH = BASE_DIR / "vector_db"
EMBEDDING_DIM = 768  # multilingual-mpnet-base-v2 dimension

# Validation Configuration
LEVENSHTEIN_THRESHOLD = 0.85
TOP_K_VERSES = 5
FUZZY_MATCH_ENABLED = True

# RAG Configuration
RAG_TOP_K = 5
RAG_SIMILARITY_THRESHOLD = 0.7
RAG_CHUNK_SIZE = 300
RAG_CHUNK_OVERLAP = 50

# Cache Configuration
CACHE_ENABLED = True
CACHE_TTL = 3600  # 1 hour in seconds
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "logs" / "quran_assistant.log"

