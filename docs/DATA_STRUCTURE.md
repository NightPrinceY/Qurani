# Quran Data Structure

## Overview
The Quran_Data folder contains a complete structured representation of the Quran with verses, tajweed rules, and translations.

## Directory Structure

### 1. `surah/` - Surah Files
Each surah has its own JSON file (e.g., `surah_1.json`):
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
    "juz": [...]
}
```

### 2. `tajweed/` - Tajweed Rules
Each surah has tajweed rules (e.g., `surah_1.json`):
```json
{
    "index": "001",
    "verse": {
        "verse_1": [
            {
                "start": 7,
                "end": 8,
                "rule": "hamzat_wasl"
            },
            {
                "start": 24,
                "end": 25,
                "rule": "madd_2"
            },
            ...
        ]
    }
}
```

**Tajweed Rules:**
- `hamzat_wasl` - همزة الوصل (Hamza of connection)
- `madd_2` - مد طبيعي (Natural prolongation - 2 counts)
- `madd_246` - مد لازم (Required prolongation - 4 or 6 counts)
- `madd_6` - مد لازم (Required prolongation - 6 counts)
- `lam_shamsiyyah` - اللام الشمسية (Solar Lam)
- `ghunnah` - الغنة (Nasal sound)
- `idgham` - الإدغام (Merging)
- `ikhfa` - الإخفاء (Hiding)
- `qalqalah` - القلقلة (Echoing)

### 3. `translation/` - Translations
Three languages:
- `ar/` - Arabic tafsir/explanation
- `en/` - English translation
- `id/` - Indonesian translation

Files named: `ar_translation_1.json`, `en_translation_1.json`, etc.

### 4. `surah.json` - Surah Metadata
Contains metadata for all 114 surahs:
- place (Mecca/Medina)
- type (Makkiyah/Madaniyah)
- count (number of verses)
- title, titleAr (Arabic name)
- index, pages
- juz information

### 5. `juz.json` - Juz Information
Contains information about the 30 juz (parts) of the Quran, including start and end verses for each juz.

## How Validation Uses This Data

1. **Search Database**: System searches all surah files to find best matching verse
2. **Load Tajweed**: If match found, loads tajweed rules for that verse
3. **LLM Validation**: Uses LLM with Quran context and tajweed rules to provide:
   - Accuracy check
   - Detailed corrections
   - Tajweed-specific feedback
   - Encouragement for correct recitation

