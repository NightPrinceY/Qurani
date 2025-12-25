"""
Test script for Quran STT Service
Tests transcription accuracy
"""
import requests
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
AUDIO_FILE = BASE_DIR / "Quran_Data" / "data" / "audio" / "002" / "007.mp3"
EXPECTED_VERSE = "خَتَمَ ٱللَّهُ عَلَىٰ قُلُوبِهِمْ وَعَلَىٰ سَمْعِهِمْ ۖ وَعَلَىٰٓ أَبْصَٰرِهِمْ غِشَٰوَةٌۭ ۖ وَلَهُمْ عَذَابٌ عَظِيمٌۭ"

SERVICE_URL = "http://localhost:8006"

def calculate_similarity(str1, str2):
    """Simple character-level similarity"""
    if not str1 or not str2:
        return 0.0
    
    # Remove diacritics for comparison (optional)
    from unicodedata import normalize
    str1_clean = normalize('NFKD', str1).encode('ascii', 'ignore').decode()
    str2_clean = normalize('NFKD', str2).encode('ascii', 'ignore').decode()
    
    # Calculate Jaccard similarity
    set1 = set(str1_clean)
    set2 = set(str2_clean)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    if union == 0:
        return 0.0
    
    return intersection / union

def test_service():
    print("=" * 60)
    print("Testing Quran STT Service")
    print("=" * 60)
    
    # Check health
    print("\n1. Checking service health...")
    try:
        response = requests.get(f"{SERVICE_URL}/health", timeout=5)
        health = response.json()
        print(f"   Status: {health.get('status')}")
        print(f"   Device: {health.get('device')}")
        print(f"   ASR Loaded: {health.get('asr_loaded')}")
        print(f"   Model: {health.get('model', 'N/A')}")
        
        if health.get('status') != 'healthy':
            print("   ❌ Service is not healthy!")
            return
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to service. Is it running?")
        return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test with audio file
    print("\n2. Testing transcription...")
    if not AUDIO_FILE.exists():
        print(f"   ❌ Audio file not found: {AUDIO_FILE}")
        return
    
    print(f"   Audio file: {AUDIO_FILE}")
    print(f"   Expected verse: {EXPECTED_VERSE}")
    
    try:
        with open(AUDIO_FILE, 'rb') as f:
            files = {'file': ('007.mp3', f, 'audio/mpeg')}
            response = requests.post(
                f"{SERVICE_URL}/transcribe",
                files=files,
                timeout=60
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n   ✅ Transcription successful!")
            print(f"\n   Transcript:")
            print(f"   {result.get('transcript', 'N/A')}")
            print(f"\n   Expected:")
            print(f"   {EXPECTED_VERSE}")
            
            # Compare transcript with expected
            transcript = result.get('transcript', '').strip()
            expected_clean = EXPECTED_VERSE.strip()
            
            if transcript:
                similarity = calculate_similarity(transcript, expected_clean)
                print(f"\n   Similarity: {similarity:.2%}")
                if similarity > 0.95:
                    print("   ✅ Excellent transcription accuracy!")
                elif similarity > 0.85:
                    print("   ✅ Good transcription accuracy")
                else:
                    print("   ⚠️  Transcription may need improvement")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_service()
