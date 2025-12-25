"""
Speech-to-Text Microservice
Based on working stt.py code
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))

import nemo.collections.asr as nemo_asr
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import logging

# Try to import from config, use defaults if not available
try:
    from config import STT_MODEL, DEVICE
    MODEL_NAME = STT_MODEL
    USE_DEVICE = DEVICE
except ImportError:
    MODEL_NAME = "nvidia/stt_ar_fastconformer_hybrid_large_pcd_v1.0"
    USE_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize device (same as working stt.py)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE}")

# Load model once at startup (same as working stt.py)
logger.info(f"Loading Arabic NeMo model: {MODEL_NAME}")
try:
    model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel.from_pretrained(
        model_name=MODEL_NAME,
        map_location=DEVICE
    )
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load STT model: {e}", exc_info=True)
    # Don't raise - let the service start but mark as unavailable
    model = None
    logger.warning("STT service will start but model is not available")

app = FastAPI(
    title="Arabic STT Service",
    description="Speech-to-Text service for Arabic Quranic recitation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if model is not None else "model_unavailable",
        "model": MODEL_NAME,
        "device": DEVICE,
        "model_loaded": model is not None
    }

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Transcribe Arabic audio to text with diacritics
    Same implementation as working stt.py
    """
    if model is None:
        return JSONResponse(
            {"error": "STT model not loaded. Please check service logs."},
            status_code=503
        )
    
    try:
        # Save uploaded file temporarily (same as working stt.py)
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        try:
            # Run transcription (same as working stt.py)
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

    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )

@app.post("/transcribe_batch")
async def transcribe_batch(files: list[UploadFile] = File(...)):
    """
    Transcribe multiple audio files in batch
    """
    if model is None:
        return JSONResponse(
            {"error": "STT model not loaded"},
            status_code=503
        )
    
    results = []
    temp_files = []
    
    try:
        # Save all files temporarily
        for file in files:
            suffix = os.path.splitext(file.filename)[1]
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(await file.read())
            temp_files.append(tmp.name)
        
        # Batch transcription
        transcripts = model.transcribe(temp_files)
        
        # Format results
        for i, (file, transcript) in enumerate(zip(files, transcripts)):
            results.append({
                "filename": file.filename,
                "transcript": transcript.text if hasattr(transcript, 'text') else str(transcript),
                "status": "success"
            })
        
        return JSONResponse({
            "results": results,
            "count": len(results),
            "status": "success"
        })
    
    except Exception as e:
        logger.error(f"Batch transcription error: {e}", exc_info=True)
        return JSONResponse(
            {"error": str(e), "status": "error"},
            status_code=500
        )
    finally:
        # Cleanup
        for tmp_path in temp_files:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == "__main__":
    import uvicorn
    
    # Get port from config or use default
    try:
        from config import STT_SERVICE_PORT
        port = STT_SERVICE_PORT
    except ImportError:
        port = 8001
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

