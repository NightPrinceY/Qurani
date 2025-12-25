# Multi-Agent Voice Quran Assistant

---

## Project Information

### Project Title
**Multi-Agent Voice Quran Assistant**  
**مساعد القرآن الصوتي متعدد الوكلاء**

### Project Summary

The Multi-Agent Voice Quran Assistant is a comprehensive advanced system designed to help users memorize and learn the Holy Quran through voice interaction. The system uses a Microservices Architecture with specialized agents for each task.

#### Key Features:

1. **Speech-to-Text (STT)**
   - Uses NVIDIA FastConformer model specialized for Arabic language
   - Full diacritics (Tashkeel) support
   - Specialized Quran service using Whisper model

2. **Recitation Validation**
   - Validates Quran recitation accuracy using AI
   - Analyzes Tajweed rules
   - Provides detailed teacher-like feedback
   - Intelligent matching with complete Quran database

3. **Tafsir RAG (Retrieval-Augmented Generation)**
   - Retrieval-Augmented Generation system
   - Verse interpretation based on trusted sources
   - Semantic search support in knowledge base

4. **Intelligent Routing (LLM Router)**
   - Automatic user intent classification
   - Routes requests to appropriate services
   - Uses GPT-OSS-20B model as the system's "brain"

5. **Text-to-Speech (TTS)**
   - Converts text responses to speech (under development)

6. **Interactive Web Interface**
   - Simple and user-friendly interface
   - Supports voice and text input
   - Clear and organized results display

#### Technologies Used:

- **Python 3.8+**: Primary programming language
- **FastAPI**: API framework
- **NVIDIA NeMo**: Speech recognition models
- **Hugging Face**: AI models and LLM
- **FAISS**: Vector database for semantic search
- **PyTorch**: Machine learning framework
- **Whisper**: Specialized model for Quran recitation

---

## Team Information

### Academic Supervisor:

**Prof. Dr. Marwa Seddiq**  
**الأستاذة الدكتورة مروة صدّيق**

### Team Member:

**Name:** Yahya Mohamed Elnawasany  
**يحيى محمد النواسني**

**Phone Number:** +201022570742

**National ID:** 30402231500656

**Level:** Level 4

**Expected Graduation Year:** 2026

---

## Hardware and Equipment Requirements

### Minimum Requirements:

#### Processor (CPU):
- **Intel Core i7** or equivalent
- **8+ cores** (recommended)
- Minimum: 4 cores

#### Memory (RAM):
- **64 GB** (recommended)
- Minimum: **32 GB**

#### Graphics Card (GPU):
- **NVIDIA RTX** with **128GB+ VRAM**
- System optimized for **128GB VRAM**
- CUDA support required
- Can work on CPU as alternative (slower)

#### Storage:
- **10GB+** free space
- Additional space for downloading models and data

#### Operating System:
- **Windows 10/11**
- **Linux** (Ubuntu 20.04+ recommended)
- **macOS**
- **WSL2** (Windows Subsystem for Linux) for Windows users

### Required Software:

1. **Python 3.8 or later**
2. **CUDA Toolkit** (for GPU operation)
3. **Git** (for project management)
4. **Modern web browser** (Chrome, Firefox, Edge)

### Internet Connection:

- **Required** for downloading models from Hugging Face
- **Required** for accessing Hugging Face Inference API
- **Required** for initial data download

### Additional Notes:

- System optimized for **128GB GPU** through:
  - Quantization enabled
  - Reduced batch size
  - Memory usage optimization

- **TTS Model Training**: Requires a server with **more than 128 GPU cores** for effective training of the Text-to-Speech model

- System supports **Graceful Degradation** - can operate even if some components fail to load

---

## Project Structure

```
Qurani/
├── api_gateway.py          # Main entry point
├── config.py               # Configuration file
├── start_services.py       # Services startup script
├── web_server.py           # Web server
├── services/               # Specialized services
│   ├── stt_service.py      # Speech-to-text service
│   ├── stt_quran_service.py # Quran-specific STT service
│   ├── llm_router.py       # Intelligent router
│   ├── quran_validator.py  # Recitation validator
│   ├── tafsir_rag.py       # Tafsir service
│   └── tts_service.py      # Text-to-speech service
├── Quran_Data/             # Quran database
│   └── data/
│       ├── surah/          # Surah files
│       ├── tajweed/        # Tajweed rules
│       ├── audio/          # Audio files
│       └── translation/    # Translations
├── web_interface/          # User interface
├── vector_db/              # Vector database
├── logs/                   # Log files
└── docs/                   # Documentation
```

---

## Services and Ports

| Service | Port | Description |
|---------|------|-------------|
| API Gateway | 8000 | Main entry point |
| STT Service | 8001 | Speech-to-text (general) |
| LLM Router | 8002 | Intelligent routing and classification |
| Quran Validator | 8003 | Recitation validation |
| Tafsir RAG | 8004 | Tafsir service |
| TTS Service | 8005 | Text-to-speech |
| Quran STT Service | 8006 | Speech-to-text (Quran-specific) |
| Web Interface | 8080 | User interface |

---

## Main Use Cases

1. **Quran Memorization**
   - Validate recitation accuracy
   - Get detailed feedback
   - Analyze Tajweed rules

2. **Understanding the Quran**
   - Verse interpretation
   - Meaning explanation
   - Answer general questions

3. **Interactive Learning**
   - Natural voice interaction
   - Encouraging and motivating responses
   - Comprehensive learning experience

---

## License

This project implements the system described in the academic research paper:  
**"Multi-Agent Voice Quran Assistant: A Comprehensive System for Interactive Quranic Learning"**

---

**Creation Date:** 2025  
**Version:** 1.0.0  
**Developer:** Yahya Mohamed Elnawasany

