# Quran STT + Tajweed Service

## Overview

This is a specialized Speech-to-Text (STT) service designed specifically for Quranic recitation. It combines:

1. **Whisper-based Arabic Quran ASR**: Fine-tuned Whisper model (`whisper-base-ar-quran`) optimized for Quranic Arabic
2. **Tajweed Rule Detection**: CNN-based models to detect specific Tajweed rules in audio

## Service Details

- **Port**: 8006 (to avoid conflict with regular STT service on 8001)
- **Endpoint**: `/analyze`
- **Health Check**: `/health`

## Models Used

### ASR Model
- **Path**: `whisper-base-ar-quran/`
- **Type**: Whisper Base fine-tuned on Arabic Quran
- **Format**: Hugging Face transformers format

### Tajweed Models
Located in `tajweed_models/`:
- `model_ghunnah.pth` - Detects Ghunnah (nasalization)
- `model_idghaam_ghunnah.pth` - Detects Idghaam with Ghunnah
- `model_ikhfa.pth` - Detects Ikhfa (concealment)
- `model_iqlab.pth` - Detects Iqlab (conversion)
- `model_madd_2.pth` - Detects Madd (prolongation)
- `model_qalqalah.pth` - Detects Qalqalah (echo)

Each Tajweed model uses:
- **Architecture**: CNN with 3 convolutional layers + fully connected layers
- **Features**: MFCC (40 coefficients)
- **Input**: Audio segments up to 5 seconds
- **Output**: Binary classification (rule present/absent) with confidence

## API Usage

### Health Check
```bash
curl http://localhost:8006/health
```

Response:
```json
{
  "status": "healthy",
  "device": "cuda",
  "asr_loaded": true,
  "tajweed_models": ["ghunnah", "idghaam_ghunnah", "ikhfa", "iqlab", "madd_2", "qalqalah"]
}
```

### Analyze Audio
```bash
curl -X POST http://localhost:8006/analyze \
  -F "file=@Quran_Data/data/audio/002/007.mp3"
```

Response:
```json
{
  "status": "success",
  "transcript": "خَتَمَ ٱللَّهُ عَلَىٰ قُلُوبِهِمْ...",
  "tajweed": {
    "ghunnah": {
      "detected": true,
      "confidence": 85.5
    },
    "madd_2": {
      "detected": true,
      "confidence": 92.3
    },
    ...
  }
}
```

## Running the Service

### In WSL (College environment)
```bash
cd /mnt/d/Qurani
source venv/bin/activate  # if venv exists
python services/stt_quran_service.py
```

Or use the script:
```bash
bash scripts/start_quran_stt_service.sh
```

## Testing

Test script available:
```bash
python scripts/test_quran_stt.py
```

This will:
1. Check service health
2. Test with `Quran_Data/data/audio/002/007.mp3`
3. Compare transcript with expected verse 7 from surah 2
4. Display Tajweed analysis results

## Expected Results

For verse 7 of surah 2:
- **Expected text**: "خَتَمَ ٱللَّهُ عَلَىٰ قُلُوبِهِمْ وَعَلَىٰ سَمْعِهِمْ ۖ وَعَلَىٰٓ أَبْصَٰرِهِمْ غِشَٰوَةٌۭ ۖ وَلَهُمْ عَذَابٌ عَظِيمٌۭ"

According to tajweed data, this verse should have:
- `hamzat_wasl` (positions 7-8)
- `madd_munfasil` (positions 60-63)
- `qalqalah` (positions 66-68)
- `madd_2` (positions 70-71, 82-83)
- `idghaam_ghunnah` (positions 86-90)
- `madd_246` (positions 109-110)

## Advantages of This Service

1. **Specialized for Quran**: Fine-tuned on Quranic Arabic, better accuracy for diacritics
2. **Tajweed Detection**: Can identify specific Tajweed rules automatically
3. **Validation Ready**: Can help validate recitation correctness
4. **Comprehensive**: Single service for both transcription and Tajweed analysis

## Limitations

1. **Tajweed models**: Only detect presence/absence, not exact positions
2. **Audio duration**: Tajweed analysis limited to 5 seconds per segment
3. **Model loading**: All models loaded at startup (memory intensive)

## Integration with Main System

To integrate this service:
1. Update `api_gateway.py` to use this service for Quran validation
2. Modify validation logic to use both transcript and Tajweed results
3. Consider using this instead of generic STT for Quran-specific queries

