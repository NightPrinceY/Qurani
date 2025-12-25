# Tajweed Detection Research & Recommendations

## Current Status

The Tajweed CNN models were removed from the service because:
- They required analyzing entire audio clips instead of specific segments
- Character position to audio timestamp mapping was approximate
- Results were not reliable enough for production use

## Research Findings

### Best Approaches for Tajweed Detection

#### 1. **Text-Based Tajweed Detection** (RECOMMENDED - Fastest & Most Accurate)

**Concept:** Use rule-based or ML-based analysis on the transcribed text itself.

**Advantages:**
- ✅ Very fast (text processing is instant)
- ✅ 100% accurate for position-based rules
- ✅ No audio processing needed
- ✅ Works with any transcription
- ✅ Can use existing Tajweed JSON data directly

**Implementation:**
1. Transcribe audio → Get Arabic text with diacritics
2. Load Tajweed rules from JSON (character positions)
3. Analyze transcribed text at those positions
4. Check if correct diacritics/characters match expected rules
5. For duration-based rules (Madd), use audio analysis if needed

**Example Rules:**
- `hamzat_wasl` - Check if hamza al-wasl (ٱ) is present
- `lam_shamsiyyah` - Check if lam is sun letter
- `madd_2` - Check if madd diacritic present (needs audio for duration)
- `idghaam_ghunnah` - Check character combinations
- `qalqalah` - Check for qalqalah letters (ق, ط, ب, ج, د)

#### 2. **Forced Alignment + Audio Analysis** (More Accurate but Slower)

**Concept:** Use forced alignment to precisely map text to audio, then analyze segments.

**Tools:**
- `whisper-timestamped` - Word-level timestamps
- Montreal Forced Aligner (MFA) - Character-level alignment
- Wav2Vec2 Forced Alignment - Very precise

**Workflow:**
1. Transcribe with word timestamps
2. Force-align to get character-level timestamps
3. Extract audio segments for each Tajweed rule position
4. Analyze segments with specialized models (if needed)

**Advantages:**
- ✅ Precise character-to-audio mapping
- ✅ Can analyze audio features for duration-based rules
- ✅ Works with existing Tajweed models (if retrained properly)

**Disadvantages:**
- ⚠️ Slower (forced alignment takes time)
- ⚠️ More complex setup
- ⚠️ Requires additional dependencies

#### 3. **Hybrid Approach** (BEST FOR PRODUCTION)

**Concept:** Combine text-based for most rules + audio for duration-based rules.

**Implementation:**
1. **Text-based rules** (fast, instant):
   - `hamzat_wasl`, `lam_shamsiyyah`, `idghaam`, `iqlab`, `ikhfa`, `qalqalah`
   - Check transcribed text at character positions
   - Compare with expected text from Tajweed JSON

2. **Audio-based rules** (only when needed):
   - `madd_2`, `madd_4`, `madd_6` - Check duration in audio
   - `ghunnah` - Check nasalization duration
   - Use simple audio feature extraction (e.g., duration, pitch, formants)

**Workflow:**
```python
def analyze_tajweed(transcript, expected_text, tajweed_rules, audio_segments):
    results = []
    
    for rule in tajweed_rules:
        if rule["rule"] in TEXT_BASED_RULES:
            # Fast text check
            result = check_text_rule(transcript, expected_text, rule)
        else:
            # Audio analysis only for duration-based rules
            audio_segment = get_audio_segment(rule["start"], rule["end"])
            result = analyze_audio_rule(audio_segment, rule["rule"])
        
        results.append(result)
    
    return results
```

## Recommended Implementation Strategy

### Phase 1: Text-Based Detection (Immediate - Fastest)

**Rules that can be detected from text:**
1. `hamzat_wasl` - Presence of ٱ
2. `lam_shamsiyyah` - Lam + sun letter combination
3. `idghaam_ghunnah` - Character combinations (ن + specific letters)
4. `idghaam_bilaghunnah` - Character combinations
5. `ikhfa` - Character combinations
6. `iqlab` - ب after ن
7. `qalqalah` - Presence of qalqalah letters at specific positions
8. `izhar` - Clear pronunciation markers

**Implementation:**
```python
def check_text_based_tajweed(transcript, expected_text, tajweed_rules):
    """Fast text-based Tajweed checking"""
    results = []
    
    for rule in tajweed_rules:
        rule_type = rule["rule"]
        start = rule["start"]
        end = rule["end"]
        
        transcript_segment = transcript[start:end+1]
        expected_segment = expected_text[start:end+1]
        
        if rule_type == "hamzat_wasl":
            detected = "ٱ" in expected_segment and check_presence(transcript_segment, expected_segment)
        elif rule_type == "qalqalah":
            detected = check_qalqalah_letter(expected_segment)
        elif rule_type == "idghaam_ghunnah":
            detected = check_idghaam_combination(transcript_segment, expected_segment)
        # ... etc
        
        results.append({
            "rule": rule_type,
            "expected": True,
            "detected": detected,
            "position": {"start": start, "end": end}
        })
    
    return results
```

### Phase 2: Audio Duration Analysis (For Madd Rules)

**Rules that need audio:**
- `madd_2`, `madd_4`, `madd_6` - Prolongation duration
- `ghunnah` - Nasalization duration

**Simple approach:**
1. Use approximate character-to-time mapping (or forced alignment if available)
2. Extract audio segment
3. Measure duration and compare to expected duration
4. For Madd: Duration should be 2/4/6 beats (approximately)

### Phase 3: Advanced Audio Features (Future Enhancement)

If more accuracy needed:
- Use formant analysis for nasalization
- Use pitch/prosody analysis for Madd
- Train lightweight models specifically for these duration-based rules

## Performance Comparison

| Method | Speed | Accuracy | Complexity |
|--------|-------|----------|------------|
| Text-based | ⚡⚡⚡ Very Fast | ✅✅✅ High (for text rules) | 🟢 Simple |
| Forced Alignment + Audio | ⚡ Slow | ✅✅✅ Very High | 🔴 Complex |
| Hybrid (Text + Simple Audio) | ⚡⚡ Fast | ✅✅✅ High | 🟡 Moderate |
| Full Audio CNN Models | ⚡ Very Slow | ✅✅ Moderate | 🔴 Very Complex |

## Recommendation

**Start with Text-Based Detection:**
1. Implement text-based rules first (80% of rules can be detected this way)
2. This gives immediate, fast, accurate feedback
3. Use simple duration checks for Madd rules
4. Add forced alignment later if more precision needed

**Benefits:**
- ⚡ Instant results (no audio processing)
- ✅ High accuracy for position-based rules
- 🟢 Simple to implement and maintain
- 💪 Scales well (works with any transcription)

## Code Structure Suggestion

```python
# services/tajweed_validator.py
class TajweedValidator:
    def __init__(self):
        self.text_rules = TextBasedTajweedRules()
        self.audio_rules = AudioBasedTajweedRules()
    
    def validate(self, transcript, expected_text, tajweed_rules, audio_path=None):
        """Main validation method"""
        results = []
        
        for rule in tajweed_rules:
            if rule["rule"] in self.text_rules.supported_rules():
                # Fast text check
                result = self.text_rules.check(transcript, expected_text, rule)
            else:
                # Audio check (if audio provided)
                if audio_path:
                    result = self.audio_rules.check(audio_path, rule)
                else:
                    result = {"error": "Audio required for this rule"}
            
            results.append(result)
        
        return results
```

## Conclusion

For a fast, production-ready Tajweed detection system:
1. **Use text-based detection** for 80% of rules
2. **Simple audio duration checks** for Madd rules
3. **Add forced alignment** only if character-level precision is critical
4. **Avoid heavy CNN models** unless absolutely necessary

This approach will be:
- ⚡ 10-100x faster than audio-based models
- ✅ More accurate for text-based rules
- 🟢 Easier to maintain and debug
- 💰 Lower resource requirements

