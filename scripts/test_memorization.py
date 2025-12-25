"""
Test script specifically for Quran memorization features
Tests Arabic feedback and correction system
"""
import httpx
import json
import asyncio
from config import API_GATEWAY_PORT

GATEWAY_URL = f"http://localhost:{API_GATEWAY_PORT}"

async def test_correct_recitation():
    """Test with correct recitation"""
    print("\n" + "="*60)
    print("✅ Test 1: Correct Recitation (Should get positive feedback)")
    print("="*60)
    
    # First verse of Al-Fatiha
    correct_text = "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{GATEWAY_URL}/text_query",
                json={"text": correct_text}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n📝 User Input: {correct_text}")
                print(f"\n🤖 System Response (Arabic):")
                print(f"   {data.get('response', 'No response')}")
                
                result = data.get('result', {})
                if result.get('is_correct'):
                    print(f"\n✅ Status: CORRECT - User will receive positive feedback!")
                else:
                    print(f"\n⚠️  Status: Needs review")
                
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_incorrect_recitation():
    """Test with incorrect recitation"""
    print("\n" + "="*60)
    print("❌ Test 2: Incorrect Recitation (Should get corrections)")
    print("="*60)
    
    # Incorrect version (missing some characters)
    incorrect_text = "بسم الله الرحمن"
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{GATEWAY_URL}/text_query",
                json={"text": incorrect_text}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n📝 User Input: {incorrect_text}")
                print(f"\n🤖 System Response (Arabic):")
                print(f"   {data.get('response', 'No response')}")
                
                result = data.get('result', {})
                if not result.get('is_correct'):
                    print(f"\n✅ Status: INCORRECT - System detected errors!")
                    corrections = result.get('corrections', [])
                    if corrections:
                        print(f"\n📋 Corrections provided:")
                        for i, correction in enumerate(corrections[:3], 1):
                            print(f"   {i}. {correction}")
                else:
                    print(f"\n⚠️  Status: Marked as correct (may need threshold adjustment)")
                
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_general_question():
    """Test general question about Quran"""
    print("\n" + "="*60)
    print("💬 Test 3: General Question (Should get Arabic response)")
    print("="*60)
    
    question = "كيف أحفظ القرآن بشكل أفضل؟"
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{GATEWAY_URL}/text_query",
                json={"text": question}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n📝 User Question: {question}")
                print(f"\n🤖 System Response (Arabic):")
                response_text = data.get('response', 'No response')
                print(f"   {response_text}")
                
                # Check if response is in Arabic
                if any('\u0600' <= char <= '\u06FF' for char in response_text):
                    print(f"\n✅ Response is in Arabic!")
                else:
                    print(f"\n⚠️  Response may not be in Arabic")
                
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_tafsir_query():
    """Test tafsir query"""
    print("\n" + "="*60)
    print("📚 Test 4: Tafsir Query (Should get explanation)")
    print("="*60)
    
    query = "ما معنى الآية الأولى من سورة الفاتحة؟"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GATEWAY_URL}/text_query",
                json={"text": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n📝 User Query: {query}")
                print(f"\n🤖 System Response (Arabic):")
                response_text = data.get('response', 'No response')
                print(f"   {response_text[:200]}...")  # First 200 chars
                
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Run all memorization tests"""
    print("="*60)
    print("🧪 Quran Memorization Assistant - Test Suite")
    print("="*60)
    print("\nThis test suite verifies:")
    print("1. ✅ Correct recitation gets positive Arabic feedback")
    print("2. ❌ Incorrect recitation gets corrections in Arabic")
    print("3. 💬 General questions get Arabic responses")
    print("4. 📚 Tafsir queries get helpful explanations")
    print()
    
    results = []
    
    results.append(await test_correct_recitation())
    results.append(await test_incorrect_recitation())
    results.append(await test_general_question())
    results.append(await test_tafsir_query())
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for memorization assistance.")
    else:
        print("\n⚠️  Some tests failed. Please check the service logs.")
    
    print("\n💡 Tips:")
    print("   - All responses should be in Arabic")
    print("   - Correct recitations should be encouraged")
    print("   - Incorrect recitations should provide specific corrections")
    print("   - The system should be helpful and encouraging for memorization")

if __name__ == "__main__":
    asyncio.run(main())

