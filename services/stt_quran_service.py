"""
Quran STT Service - Specialized Arabic Quran Transcription
Uses fine-tuned Whisper model for accurate Quranic Arabic transcription
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
try:
    import torchaudio
    TORCHAUDIO_AVAILABLE = True
except ImportError:
    TORCHAUDIO_AVAILABLE = False
    import warnings
    warnings.warn("torchaudio not available, using librosa for resampling")
import soundfile as sf
import librosa
import tempfile
import os
import logging

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from transformers import pipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QURAN_STT")

# Get HF token from config or environment
try:
    from config import HF_TOKEN as CONFIG_HF_TOKEN
    HF_TOKEN = CONFIG_HF_TOKEN
except ImportError:
    HF_TOKEN = os.getenv("HF_TOKEN", "your_huggingface_token_here")

# Set environment variables for Hugging Face libraries
os.environ["HF_TOKEN"] = HF_TOKEN
os.environ["HUGGINGFACE_HUB_TOKEN"] = HF_TOKEN

# =========================
# CONFIG
# =========================
BASE_DIR = Path(__file__).parent.parent
LOCAL_MODEL_PATH = BASE_DIR / "whisper-base-ar-quran"

# Check if local model exists (not Git LFS pointer)
if LOCAL_MODEL_PATH.exists():
    model_bin = LOCAL_MODEL_PATH / "pytorch_model.bin"
    if model_bin.exists() and model_bin.stat().st_size > 1000:
        ASR_MODEL_PATH = str(LOCAL_MODEL_PATH)
    else:
        ASR_MODEL_PATH = "tarteel-ai/whisper-base-ar-quran"
else:
    ASR_MODEL_PATH = "tarteel-ai/whisper-base-ar-quran"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
SAMPLE_RATE = 16000

logger.info(f"Using device: {DEVICE}")
logger.info(f"ASR Model Path: {ASR_MODEL_PATH}")

# =========================
# LOAD ASR MODEL
# =========================
asr_pipeline = None

try:
    logger.info("Loading Whisper Quran ASR model...")
    logger.info(f"Using HF Token: {HF_TOKEN[:10]}...")
    
    device_id = 0 if DEVICE == "cuda" else "cpu"
    asr_pipeline = pipeline(
        task="automatic-speech-recognition",
        model=ASR_MODEL_PATH,
        chunk_length_s=30,
        device=device_id,
        token=HF_TOKEN if ASR_MODEL_PATH.startswith("tarteel-ai/") else None
    )
    
    # Set forced decoder ids for Arabic
    asr_pipeline.model.config.forced_decoder_ids = asr_pipeline.tokenizer.get_decoder_prompt_ids(
        language="ar", 
        task="transcribe"
    )
    
    logger.info("ASR model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load ASR model: {e}", exc_info=True)
    asr_pipeline = None

# =========================
# AUDIO UTILS
# =========================
def load_audio(path):
    """Load and resample audio to SAMPLE_RATE"""
    audio, sr = sf.read(path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    audio = audio.astype("float32")
    if sr != SAMPLE_RATE:
        if TORCHAUDIO_AVAILABLE:
            audio = torchaudio.functional.resample(
                torch.from_numpy(audio),
                sr,
                SAMPLE_RATE
            ).numpy()
        else:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=SAMPLE_RATE)
    return audio

# =========================
# FASTAPI APP
# =========================
app = FastAPI(
    title="Quran STT Service",
    description="Specialized Speech-to-Text service for Quranic Arabic recitation",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# HEALTH
# =========================
@app.get("/health")
async def health():
    return {
        "status": "healthy" if asr_pipeline is not None else "model_unavailable",
        "device": DEVICE,
        "asr_loaded": asr_pipeline is not None,
        "model": ASR_MODEL_PATH
    }

# =========================
# TRANSCRIBE ENDPOINT
# =========================
@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Transcribe Arabic Quranic audio to text
    """
    if asr_pipeline is None:
        return JSONResponse({"error": "ASR model not loaded"}, status_code=503)

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # Transcribe using pipeline
        result = asr_pipeline(tmp_path)
        transcription = result["text"]
        
        return {
            "status": "success",
            "transcript": transcription,
            "language": "ar"
        }

    except Exception as e:
        logger.error(e, exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

    finally:
        os.remove(tmp_path)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    import uvicorn
    # Use port 8006 to avoid conflict with existing STT service on 8001
    uvicorn.run(app, host="0.0.0.0", port=8006, log_level="info")
