# Multi-Agent Voice Quran Assistant

A comprehensive multi-agent voice-enabled system for interactive Quranic learning, implementing the architecture described in the research paper.

## Features

- **Speech-to-Text**: Arabic speech recognition with diacritics using NVIDIA FastConformer
- **Text-to-Speech**: Arabic TTS synthesis (placeholder - API integration pending)
- **Quran Validation**: Fuzzy matching and verse validation
- **Tafsir RAG**: Retrieval-Augmented Generation for verse interpretation
- **LLM Router**: Intelligent intent classification and routing
- **API Gateway**: Unified entry point for all services

## System Requirements

- **CPU**: Intel i7 or equivalent (8+ cores recommended)
- **RAM**: 32GB (minimum 16GB)
- **GPU**: NVIDIA RTX with 4GB+ VRAM (optimized for 4GB)
- **Storage**: 10GB+ free space
- **OS**: Windows 10/11, Linux, or macOS

## Installation

### 1. Clone and Setup

```bash
# Navigate to project directory
cd Qurani

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Set your Hugging Face token:

```bash
# Windows PowerShell
$env:HF_TOKEN="your_huggingface_token_here"

# Windows CMD
set HF_TOKEN=your_huggingface_token_here

# Linux/Mac
export HF_TOKEN="your_huggingface_token_here"
```

Or create a `.env` file:
```
HF_TOKEN=your_huggingface_token_here
```

### 3. Verify Data Structure

Ensure your `Quran_Data` folder structure matches:
```
Quran_Data/
├── data/
│   ├── surah.json
│   ├── juz.json
│   ├── surah/
│   ├── audio/
│   ├── tajweed/
│   └── translation/
```

## Running the System

### Option 1: Run All Services Individually

Open multiple terminals and run each service:

**Terminal 1 - STT Service:**
```bash
python services/stt_service.py
```

**Terminal 2 - LLM Router:**
```bash
python services/llm_router.py
```

**Terminal 3 - Quran Validator:**
```bash
python services/quran_validator.py
```

**Terminal 4 - Tafsir RAG:**
```bash
python services/tafsir_rag.py
```

**Terminal 5 - TTS Service:**
```bash
python services/tts_service.py
```

**Terminal 6 - API Gateway:**
```bash
python api_gateway.py
```

### Option 2: Use the Startup Script

```bash
python start_services.py
```

## API Endpoints

### API Gateway (Port 8000)

- `GET /` - API information
- `GET /health` - Health check for all services
- `POST /voice_query` - Complete voice query pipeline
- `POST /text_query` - Text-based query
- `POST /transcribe` - Direct STT transcription
- `POST /validate` - Direct verse validation
- `POST /tafsir` - Direct tafsir query

### Individual Services

- **STT Service** (8001): `/transcribe`, `/health`
- **LLM Router** (8002): `/classify_intent`, `/route`, `/chat`, `/health`
- **Quran Validator** (8003): `/validate`, `/verse/{surah}/{verse}`, `/health`
- **Tafsir RAG** (8004): `/tafsir`, `/add_passages`, `/health`
- **TTS Service** (8005): `/synthesize`, `/health`

## Usage Examples

### Python Client

```python
import httpx
import json

# Voice query
with open("recitation.wav", "rb") as f:
    response = httpx.post(
        "http://localhost:8000/voice_query",
        files={"file": ("recitation.wav", f, "audio/wav")}
    )
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Text query
response = httpx.post(
    "http://localhost:8000/text_query",
    json={"text": "ما معنى الآية الأولى من سورة الفاتحة؟"}
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Voice query
curl -X POST http://localhost:8000/voice_query \
  -F "file=@recitation.wav"

# Text query
curl -X POST http://localhost:8000/text_query \
  -H "Content-Type: application/json" \
  -d '{"text": "ما معنى الآية الأولى من سورة الفاتحة؟"}'
```

## Configuration

Edit `config.py` to customize:
- Service ports
- Model paths
- GPU/CPU settings
- Vector database settings
- Thresholds and parameters

## GPU Optimization

The system is optimized for 4GB GPU:
- Quantization enabled by default
- Batch size limited to 1
- CPU fallback available

To disable quantization or adjust settings, edit `config.py`.

## Building Tafsir Knowledge Base

The Tafsir RAG service requires a knowledge base. To build it:

```python
import httpx

passages = [
    {
        "text": "تفسير الآية...",
        "source": "تفسير الطبري",
        "surah_index": "001",
        "verse_key": "verse_1"
    }
]

response = httpx.post(
    "http://localhost:8004/add_passages",
    json=passages
)
```

## Troubleshooting

### CUDA Out of Memory
- Reduce batch size in `config.py`
- Enable quantization
- Use CPU mode

### Service Connection Errors
- Check all services are running
- Verify ports are not in use
- Check firewall settings

### Model Loading Issues
- Verify Hugging Face token is set
- Check internet connection for model download
- Ensure sufficient disk space

## Architecture

The system follows a microservices architecture:

```
User → API Gateway → [STT → LLM Router → Services] → TTS → User
```

Services:
- **STT Service**: Speech-to-text conversion
- **LLM Router**: Intent classification and routing
- **Quran Validator**: Verse matching and validation
- **Tafsir RAG**: Interpretation generation
- **TTS Service**: Text-to-speech synthesis

## Development

### Project Structure
```
Qurani/
├── config.py              # Configuration
├── api_gateway.py         # Main API gateway
├── services/              # Microservices
│   ├── stt_service.py
│   ├── llm_router.py
│   ├── quran_validator.py
│   ├── tafsir_rag.py
│   └── tts_service.py
├── Quran_Data/            # Quran dataset
├── requirements.txt
└── README.md
```

## License

This project implements the system described in the research paper "Multi-Agent Voice Quran Assistant: A Comprehensive System for Interactive Quranic Learning".

## Support

For issues or questions, please refer to the paper documentation or create an issue in the repository.

