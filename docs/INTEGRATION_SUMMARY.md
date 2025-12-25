# Quran STT Service Integration Summary

## Overview

The Quran STT service has been successfully integrated into the system with intelligent routing and enhanced teacher-like validation using Tajweed rules.

## Key Features

### 1. Intelligent STT Routing

The system now intelligently routes audio input:

- **Quran STT First**: Uses `stt_quran_service.py` (Whisper Quran model) for Quran recitation
- **Regular STT Fallback**: Falls back to `stt_service.py` (NeMo FastConformer) for normal speech
- **Automatic Detection**: Detects if transcript matches Quran verses to determine intent

**Flow:**
```
Audio Input
    ↓
Try Quran STT (port 8006)
    ↓
If fails/empty → Use Regular STT (port 8001)
    ↓
Check if transcript matches Quran database
    ↓
Route to appropriate service
```

### 2. Enhanced Validation with Teacher Mode

The `quran_validator.py` service now provides **muallim (معلم)**-like feedback:

- **Quran_Data Integration**: Uses structured Quran data (surah files + tajweed rules)
- **Tajweed-Aware**: Loads and analyzes Tajweed rules for each verse
- **LLM-Powered Feedback**: Uses LLM to generate detailed, encouraging, teacher-like feedback
- **Detailed Corrections**: Provides specific corrections with position information

**Feedback includes:**
- Encouragement for correct recitation
- Specific corrections for errors
- Tajweed rule explanations when relevant
- Verse identification (surah and verse number)

### 3. Service Architecture

```
┌─────────────┐
│ API Gateway │ (Port 8000)
│             │
│ Smart Router│
└──────┬──────┘
       │
       ├──→ Quran STT Service (Port 8006) ← Specialized for Quran
       │        └─→ Whisper Quran Model
       │
       ├──→ Regular STT Service (Port 8001) ← For normal speech
       │        └─→ NeMo FastConformer
       │
       ├──→ Quran Validator (Port 8003) ← Enhanced with Tajweed
       │        ├─→ Quran_Data (surah + tajweed JSON)
       │        └─→ LLM Teacher Feedback
       │
       ├──→ LLM Router (Port 8002)
       ├──→ Tafsir RAG (Port 8004)
       └──→ TTS Service (Port 8005)
```

## Configuration Changes

### `config.py`
```python
QURAN_STT_SERVICE_PORT = 8006  # Added
```

### `api_gateway.py`
- Added `quran_stt` to `SERVICE_URLS`
- Implemented `detect_if_quran_recitation()` function
- Updated `voice_query()` endpoint with smart routing
- Enhanced `process_intent()` to use enhanced validator

### `services/quran_validator.py`
- Complete rewrite with Tajweed integration
- Added `load_tajweed_rules()` function
- Added `get_teacher_feedback()` function using LLM
- Enhanced validation response with Tajweed rules

### `start_services.py`
- Added Quran STT service to startup list

## API Changes

### `/voice_query` Endpoint

**New Response Fields:**
- `stt_service_used`: Indicates which STT service was used (`"quran_stt"` or `"stt"`)

**Example Response:**
```json
{
  "transcript": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
  "intent": "recitation_validation",
  "stt_service_used": "quran_stt",
  "response": "ممتاز! قراءتك صحيحة تماماً...",
  "result": {
    "is_correct": true,
    "tajweed_rules": [...],
    "matched_verse": "001:verse_0"
  }
}
```

### `/validate` Endpoint (Enhanced)

**New Request Parameters:**
- `use_teacher_mode`: Enable detailed LLM-powered teacher feedback (default: `true`)

**Enhanced Response:**
```json
{
  "is_correct": true,
  "feedback_arabic": "ممتاز! قراءتك صحيحة تماماً...",
  "tajweed_rules": [
    {
      "rule": "hamzat_wasl",
      "start": 7,
      "end": 8
    }
  ],
  "corrections": [],
  "best_match": {
    "surah_index": "001",
    "surah_name": "al-Fatihah",
    "verse_key": "verse_0"
  }
}
```

## Data Flow for Quran Recitation

1. **User records audio** → API Gateway
2. **API Gateway** → Tries Quran STT first
3. **Quran STT** → Transcribes with specialized model
4. **API Gateway** → Checks if transcript matches Quran database
5. **If match** → Routes to enhanced validator
6. **Validator** → 
   - Finds matching verse from Quran_Data
   - Loads Tajweed rules for that verse
   - Generates teacher feedback using LLM with Tajweed context
7. **Response** → Returns detailed feedback to user

## Tajweed Rule Detection

The validator now uses Tajweed rules from `Quran_Data/data/tajweed/`:

- `hamzat_wasl` - همزة الوصل
- `madd_2`, `madd_246`, `madd_6` - أنواع المد
- `lam_shamsiyyah` - اللام الشمسية
- `ghunnah` - الغنة
- `idgham`, `idghaam_ghunnah` - الإدغام
- `ikhfa` - الإخفاء
- `iqlab` - الإقلاب
- `qalqalah` - القلقلة

The LLM teacher feedback includes these rules in context when providing corrections.

## Starting All Services

Use the updated startup script:

```bash
python start_services.py
```

This will start:
1. STT Service (8001)
2. **Quran STT Service (8006)** ← New
3. LLM Router (8002)
4. Quran Validator (8003)
5. Tafsir RAG (8004)
6. TTS Service (8005)
7. API Gateway (8000)

## Testing

### Test Quran Recitation:
```bash
# Send audio to API Gateway
curl -X POST "http://localhost:8000/voice_query" \
  -F "file=@quran_recitation.mp3"

# Response will show:
# - stt_service_used: "quran_stt"
# - intent: "recitation_validation"
# - Detailed teacher feedback with Tajweed info
```

### Test Normal Speech:
```bash
# Send normal speech audio
curl -X POST "http://localhost:8000/voice_query" \
  -F "file=@normal_speech.mp3"

# Response will show:
# - stt_service_used: "stt" (or "quran_stt" if it worked)
# - intent: Based on LLM classification
```

## Benefits

1. **Better Accuracy**: Specialized Quran model for Quranic Arabic
2. **Smart Routing**: Automatically uses the right STT service
3. **Teacher-Like Feedback**: Detailed, encouraging feedback like a real teacher
4. **Tajweed Awareness**: Validation includes Tajweed rule checking
5. **Fallback Safety**: If Quran STT fails, falls back to regular STT

## Future Enhancements

- [ ] Real-time audio streaming support
- [ ] Tajweed audio analysis (duration-based rules like Madd)
- [ ] Pronunciation scoring per character
- [ ] Progress tracking for memorization
- [ ] Comparison with multiple reciters

