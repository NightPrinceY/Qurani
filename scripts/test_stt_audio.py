#!/usr/bin/env python3
"""
Test STT service with an audio file
"""
import requests
import sys
from pathlib import Path

# Audio file path
audio_file = Path("Quran_Data/data/audio/001/007.mp3")

if not audio_file.exists():
    print(f"❌ Audio file not found: {audio_file}")
    sys.exit(1)

print(f"🎵 Testing STT service with: {audio_file}")
print(f"📁 File size: {audio_file.stat().st_size / 1024:.2f} KB")
print()

# STT service URL
stt_url = "http://localhost:8001/transcribe"

try:
    print("📤 Sending audio to STT service...")
    with open(audio_file, "rb") as f:
        files = {"file": (audio_file.name, f, "audio/mpeg")}
        response = requests.post(stt_url, files=files, timeout=60)
    
    print(f"📥 Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        transcript = result.get("transcript", "")
        print()
        print("✅ Transcription successful!")
        print("=" * 60)
        print(f"📝 Transcript: {transcript}")
        print("=" * 60)
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to STT service at http://localhost:8001")
    print("   Make sure the STT service is running!")
except requests.exceptions.Timeout:
    print("❌ Request timed out. The audio file might be too long.")
except Exception as e:
    print(f"❌ Error: {e}")

