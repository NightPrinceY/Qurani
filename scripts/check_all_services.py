#!/usr/bin/env python3
"""
Quick health check for all services
"""
import requests
import time

services = {
    "STT Service": "http://localhost:8001/health",
    "LLM Router": "http://localhost:8002/health",
    "Quran Validator": "http://localhost:8003/health",
    "Tafsir RAG": "http://localhost:8004/health",
    "TTS Service": "http://localhost:8005/health",
    "API Gateway": "http://localhost:8000/health",
    "Web Interface": "http://localhost:8080/health",
}

print("=" * 60)
print("🔍 Checking Service Health")
print("=" * 60)
print()

# Wait a moment for services to fully initialize
time.sleep(2)

all_ok = True
for name, url in services.items():
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            status = response.json().get("status", "unknown")
            if status == "ok" or status == "healthy":
                print(f"✅ {name:20s} - Running")
            else:
                print(f"⚠️  {name:20s} - Running (status: {status})")
        else:
            print(f"❌ {name:20s} - Error {response.status_code}")
            all_ok = False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name:20s} - Not responding")
        all_ok = False
    except Exception as e:
        print(f"❌ {name:20s} - Error: {str(e)[:50]}")
        all_ok = False

print()
print("=" * 60)
if all_ok:
    print("✅ All services are running!")
else:
    print("⚠️  Some services may need attention")
print("=" * 60)

