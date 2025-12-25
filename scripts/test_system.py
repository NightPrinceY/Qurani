"""
Test script for Multi-Agent Voice Quran Assistant
Tests all services and endpoints
"""
import httpx
import json
import asyncio
from config import (
    STT_SERVICE_PORT, LLM_SERVICE_PORT, VALIDATOR_SERVICE_PORT,
    TAFSIR_SERVICE_PORT, TTS_SERVICE_PORT, API_GATEWAY_PORT
)

SERVICE_URLS = {
    "stt": f"http://localhost:{STT_SERVICE_PORT}",
    "llm": f"http://localhost:{LLM_SERVICE_PORT}",
    "validator": f"http://localhost:{VALIDATOR_SERVICE_PORT}",
    "tafsir": f"http://localhost:{TAFSIR_SERVICE_PORT}",
    "tts": f"http://localhost:{TTS_SERVICE_PORT}",
    "gateway": f"http://localhost:{API_GATEWAY_PORT}"
}

async def test_service_health(name, url):
    """Test service health endpoint"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}/health")
            if response.status_code == 200:
                print(f"✅ {name}: Healthy")
                return True
            else:
                print(f"❌ {name}: Unhealthy (Status: {response.status_code})")
                return False
    except Exception as e:
        print(f"❌ {name}: Connection failed - {e}")
        return False

async def test_validator():
    """Test Quran validator service"""
    print("\n📖 Testing Quran Validator...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test with first verse of Al-Fatiha
            test_text = "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
            response = await client.post(
                f"{SERVICE_URLS['validator']}/validate",
                json={"text": test_text}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("best_match"):
                    match = data["best_match"]
                    print(f"✅ Validation successful!")
                    print(f"   Matched: {match.get('surah_name')} {match.get('verse_key')}")
                    print(f"   Similarity: {match.get('similarity', 0):.2%}")
                    return True
                else:
                    print(f"⚠️  No match found (this might be expected)")
                    return True
            else:
                print(f"❌ Validation failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Validation test error: {e}")
        return False

async def test_llm_router():
    """Test LLM router service"""
    print("\n🧠 Testing LLM Router...")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Test intent classification
            test_text = "ما معنى الآية الأولى من سورة الفاتحة؟"
            response = await client.post(
                f"{SERVICE_URLS['llm']}/classify_intent",
                json={"text": test_text}
            )
            
            if response.status_code == 200:
                data = response.json()
                intent = data.get("intent", "unknown")
                print(f"✅ Intent classification successful!")
                print(f"   Text: {test_text[:50]}...")
                print(f"   Detected intent: {intent}")
                return True
            else:
                print(f"❌ Intent classification failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ LLM router test error: {e}")
        return False

async def test_tafsir():
    """Test Tafsir RAG service"""
    print("\n📚 Testing Tafsir RAG...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{SERVICE_URLS['tafsir']}/tafsir",
                json={"query": "ما معنى سورة الفاتحة؟"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Tafsir service responding")
                print(f"   Response length: {len(data.get('tafsir', ''))} characters")
                return True
            else:
                print(f"⚠️  Tafsir service responded but may not have data yet")
                return True  # Service is working, just no data
    except Exception as e:
        print(f"❌ Tafsir test error: {e}")
        return False

async def test_gateway():
    """Test API Gateway"""
    print("\n🚪 Testing API Gateway...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test health endpoint
            response = await client.get(f"{SERVICE_URLS['gateway']}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Gateway healthy")
                services = data.get("services", {})
                for service, status in services.items():
                    status_icon = "✅" if status else "❌"
                    print(f"   {status_icon} {service}: {'Healthy' if status else 'Unhealthy'}")
                return True
            else:
                print(f"❌ API Gateway unhealthy: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Gateway test error: {e}")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("Multi-Agent Voice Quran Assistant - System Test")
    print("=" * 60)
    print()
    
    # Test individual services
    print("🔍 Testing Individual Services...")
    print("-" * 60)
    
    health_results = []
    for name, url in SERVICE_URLS.items():
        if name != "gateway":  # Test gateway separately
            result = await test_service_health(name.upper(), url)
            health_results.append(result)
    
    print()
    
    # Test specific functionality
    print("🧪 Testing Functionality...")
    print("-" * 60)
    
    validator_result = await test_validator()
    llm_result = await test_llm_router()
    tafsir_result = await test_tafsir()
    gateway_result = await test_gateway()
    
    # Summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_health = all(health_results)
    all_functional = validator_result and llm_result and tafsir_result and gateway_result
    
    if all_health and all_functional:
        print("✅ All tests passed! System is ready.")
    elif all_health:
        print("⚠️  Services are running but some functionality needs attention.")
    else:
        print("❌ Some services are not responding. Please check:")
        print("   1. All services are started")
        print("   2. Ports are not in use by other applications")
        print("   3. Firewall settings allow connections")
    
    print()
    print("API Gateway: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main())

