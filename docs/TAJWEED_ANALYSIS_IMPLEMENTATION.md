# Tajweed Analysis Implementation - Complete Solution

## Overview

I've completely redesigned the Tajweed detection system to properly analyze specific audio segments corresponding to character positions in the Quranic text, rather than analyzing the entire audio clip.

## What Was Fixed

### Previous Approach (WRONG)
- Analyzed entire audio clip with all Tajweed models
- No connection between text positions and audio segments
- Couldn't verify if rules were applied at correct locations

### New Approach (CORRECT)
1. **Get word timestamps** from Whisper ASR
2. **Match transcript to verse** using similarity matching
3. **Load expected Tajweed rules** from JSON data files
4. **Map character positions to audio timestamps** (alignment)
5. **Extract audio segments** for each rule position
6. **Run specific Tajweed model** on the correct segment
7. **Compare detected vs expected** rules

## Architecture

### New Components

#### 1. `TajweedAnalyzer` Class (`services/tajweed_analyzer.py`)

**Key Methods:**
- `load_tajweed_data(surah_index)` - Loads Tajweed rules JSON
- `load_surah_data(surah_index)` - Loads verse text
- `find_matching_verse(transcript, surah_index)` - Matches transcript to verse
- `map_text_positions_to_audio()` - Maps character positions to timestamps
- `get_tajweed_rules_for_verse()` - Gets expected rules for a verse
- `extract_audio_segment()` - Extracts audio for specific character range

#### 2. Updated Service (`services/stt_quran_service.py`)

**Key Changes:**
- Gets word-level timestamps from Whisper pipeline
- Uses `TajweedAnalyzer` to identify verse and get rules
- Extracts audio segments for each rule position
- Runs Tajweed models on specific segments
- Returns detailed analysis with position information

## Data Flow

```
Audio File
    ↓
[Whisper ASR with timestamps]
    ↓
Transcript + Word Timestamps
    ↓
[Match to Verse (surah/verse)]
    ↓
Expected Text + Tajweed Rules
    ↓
[Map Character Positions → Audio Timestamps]
    ↓
[Extract Audio Segments per Rule]
    ↓
[Run Tajweed Models on Segments]
    ↓
[Compare Detected vs Expected]
    ↓
Detailed Results
```

## Tajweed Data Structure

Each surah has a JSON file (`tajweed/surah_X.json`):

```json
{
    "index": "002",
    "verse": {
        "verse_7": [
            {
                "start": 70,
                "end": 71,
                "rule": "madd_2"
            },
            {
                "start": 86,
                "end": 90,
                "rule": "idghaam_ghunnah"
            }
        ]
    }
}
```

- `start`/`end`: Character positions in the Arabic text (0-indexed)
- `rule`: Name of the Tajweed rule (must match model name)

## Example Response

```json
{
    "status": "success",
    "transcript": "خَتَمَ اللَّهُ عَلَى قُلُوبِهِمْ...",
    "tajweed": {
        "madd_2": {
            "detected": true,
            "confidence": 95.3,
            "instances": 2
        },
        "idghaam_ghunnah": {
            "detected": true,
            "confidence": 87.2,
            "instances": 1
        }
    },
    "tajweed_analysis": {
        "matched_verse": "2:verse_7",
        "expected_rules_count": 7,
        "rules_analyzed": [
            {
                "rule": "madd_2",
                "expected": true,
                "detected": true,
                "confidence": 95.3,
                "position": {"start": 70, "end": 71},
                "correct": true
            },
            ...
        ],
        "summary": {
            "madd_2": {
                "total": 2,
                "detected": 2,
                "missed": 0
            }
        }
    }
}
```

## How It Works

### Step 1: Verse Identification
- Tries to extract surah/verse from filename pattern (`002/007.mp3`)
- Falls back to text similarity matching against known verses
- Loads expected text and Tajweed rules

### Step 2: Audio-Text Alignment
- Maps word timestamps from Whisper to character positions
- Creates position map: `{char_position: (start_time, end_time)}`
- Handles word alignment between transcript and expected text

### Step 3: Segment Extraction
- For each expected Tajweed rule:
  - Gets character position range (start, end)
  - Converts to audio timestamps using position map
  - Extracts audio segment with padding (100ms)
  - Ensures minimum segment length (100ms)

### Step 4: Tajweed Detection
- Extracts MFCC features from segment
- Runs the specific Tajweed model for that rule
- Gets binary classification (present/absent) with confidence
- Compares with expected presence

### Step 5: Reporting
- Detailed analysis per rule with positions
- Summary statistics per rule type
- Backward-compatible format for existing code

## Supported Tajweed Models

- `ghunnah` - Nasalization
- `idghaam_ghunnah` - Assimilation with nasalization
- `ikhfa` - Concealment
- `iqlab` - Conversion
- `madd_2` - Prolongation (2 counts)
- `qalqalah` - Echo/bounce

## Limitations & Future Improvements

### Current Limitations
1. Word alignment may not be perfect (text similarity-based)
2. Character-to-time mapping is approximate (linear interpolation)
3. Requires filename pattern or text matching to identify verse
4. Segment extraction uses padding which might include adjacent sounds

### Potential Improvements
1. **Force-alignment**: Use forced alignment tools (e.g., Montreal Forced Aligner) for precise character-to-time mapping
2. **Better verse matching**: Use semantic similarity or verse embedding models
3. **Context windows**: Extract larger segments with context before/after
4. **Rule-specific segments**: Different segment sizes for different rules
5. **Confidence thresholds**: Adjustable thresholds per rule type

## Testing

Test with:
```bash
python scripts/test_quran_stt.py
```

Expected improvements:
- ✅ Rules detected at correct positions
- ✅ Higher accuracy (comparing segments, not full audio)
- ✅ Detailed position information
- ✅ Ability to identify missing or incorrect rules

## Integration Notes

The service maintains backward compatibility:
- `tajweed` field still exists with simple detected/confidence
- New `tajweed_analysis` field provides detailed information
- Falls back to old method if verse cannot be identified

