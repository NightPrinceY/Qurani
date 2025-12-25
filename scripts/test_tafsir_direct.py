#!/usr/bin/env python3
"""
Direct test of Tafsir service
"""
import requests
import json

TAFSIR_URL = "http://localhost:8004"

print("=" * 60)
print("Testing Tafsir Service Directly")
print("=" * 60)

# Test 1: Health Check
print("\n1. Health Check:")
print("-" * 60)
try:
    response = requests.get(f"{TAFSIR_URL}/health", timeout=5)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("✅ Health check passed")
    else:
        print(f"❌ Health check failed: {response.text}")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to Tafsir service. Is it running on port 8004?")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Tafsir Query
print("\n2. Tafsir Query (Arabic):")
print("-" * 60)
try:
    payload = {
        "query": "ما معنى بسم الله الرحمن الرحيم؟",
        "surah_index": "001",
        "verse_key": "verse_1"
    }
    response = requests.post(
        f"{TAFSIR_URL}/tafsir",
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("\nResponse:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("\n✅ Tafsir query successful")
        if data.get("tafsir"):
            print(f"✅ Tafsir text length: {len(data['tafsir'])} chars")
        if data.get("response_voice_optimized"):
            print("✅ Response is voice-optimized")
    else:
        print(f"❌ Tafsir query failed: {response.text}")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to Tafsir service. Is it running on port 8004?")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Simple Query
print("\n3. Simple Tafsir Query:")
print("-" * 60)
try:
    payload = {
        "query": "اشرح لي سورة الفاتحة"
    }
    response = requests.post(
        f"{TAFSIR_URL}/tafsir",
        json=payload,
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        tafsir = data.get("tafsir", "")
        print(f"Tafsir Response: {tafsir[:200]}..." if len(tafsir) > 200 else f"Tafsir Response: {tafsir}")
        print(f"✅ Response length: {len(tafsir)} chars")
        print(f"✅ Mode: {data.get('mode', 'unknown')}")
    else:
        print(f"❌ Query failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

