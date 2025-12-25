#!/usr/bin/env python3
"""
Comprehensive service status report
"""
import requests
import subprocess
import json
from datetime import datetime

print("=" * 70)
print("📊 MULTI-AGENT VOICE QURAN ASSISTANT - SERVICE STATUS REPORT")
print("=" * 70)
print(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Service definitions
services = {
    "STT Service": {
        "port": 8001,
        "url": "http://localhost:8001/health",
        "description": "Speech-to-Text conversion"
    },
    "LLM Router": {
        "port": 8002,
        "url": "http://localhost:8002/health",
        "description": "Intent classification and routing"
    },
    "Quran Validator": {
        "port": 8003,
        "url": "http://localhost:8003/health",
        "description": "Recitation validation"
    },
    "Tafsir RAG": {
        "port": 8004,
        "url": "http://localhost:8004/health",
        "description": "Verse interpretation (RAG)"
    },
    "TTS Service": {
        "port": 8005,
        "url": "http://localhost:8005/health",
        "description": "Text-to-Speech synthesis"
    },
    "API Gateway": {
        "port": 8000,
        "url": "http://localhost:8000/health",
        "description": "Central API gateway"
    },
    "Web Interface": {
        "port": 8080,
        "url": "http://localhost:8080/health",
        "description": "User web interface"
    }
}

# Check processes
print("🔍 PROCESS STATUS")
print("-" * 70)
try:
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True,
        timeout=5
    )
    for name, info in services.items():
        script_name = name.lower().replace(" ", "_")
        if "stt" in script_name:
            script_name = "stt_service"
        elif "llm" in script_name:
            script_name = "llm_router"
        elif "quran" in script_name:
            script_name = "quran_validator"
        elif "tafsir" in script_name:
            script_name = "tafsir_rag"
        elif "tts" in script_name:
            script_name = "tts_service"
        elif "api" in script_name:
            script_name = "api_gateway"
        elif "web" in script_name:
            script_name = "web_server"
        
        if script_name in result.stdout:
            print(f"✅ {name:20s} - Process running")
        else:
            print(f"❌ {name:20s} - Process not found")
except:
    print("⚠️  Could not check processes")

print()
print("🌐 HEALTH CHECK")
print("-" * 70)

all_healthy = True
for name, info in services.items():
    try:
        response = requests.get(info["url"], timeout=3)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            if status in ["ok", "healthy"]:
                print(f"✅ {name:20s} - Healthy (Port {info['port']})")
            else:
                print(f"⚠️  {name:20s} - Running (Status: {status})")
                if status == "degraded":
                    print(f"    └─ Some dependencies may be unavailable")
        else:
            print(f"❌ {name:20s} - Error {response.status_code}")
            all_healthy = False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name:20s} - Not responding (Port {info['port']})")
        all_healthy = False
    except requests.exceptions.Timeout:
        print(f"⏳ {name:20s} - Timeout (may be loading)")
    except Exception as e:
        print(f"❌ {name:20s} - Error: {str(e)[:40]}")

print()
print("📋 SERVICE DETAILS")
print("-" * 70)
for name, info in services.items():
    print(f"{name}:")
    print(f"  Port: {info['port']}")
    print(f"  Description: {info['description']}")
    print(f"  URL: {info['url']}")
    print()

print("=" * 70)
if all_healthy:
    print("✅ ALL SERVICES OPERATIONAL")
else:
    print("⚠️  SOME SERVICES NEED ATTENTION")
print("=" * 70)
print()
print("🌐 Access Points:")
print("   Web Interface:  http://localhost:8080")
print("   API Gateway:    http://localhost:8000")
print("   API Docs:      http://localhost:8000/docs")
print()

