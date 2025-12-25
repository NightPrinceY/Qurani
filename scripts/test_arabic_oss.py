#!/usr/bin/env python3
"""
Test OSS Model with Arabic - Verify all services work
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from huggingface_hub import InferenceClient

try:
    from config import HF_TOKEN
except ImportError:
    HF_TOKEN = os.getenv("HF_TOKEN", "")

if not HF_TOKEN:
    print("❌ ERROR: HF_TOKEN not set!")
    sys.exit(1)

print("=" * 60)
print("Testing OSS Model - Arabic Support")
print("=" * 60)

client = InferenceClient(api_key=HF_TOKEN)
model_name = "openai/gpt-oss-20b"

# Test 1: Simple Arabic
print("\n1. Simple Arabic Greeting:")
print("-" * 60)
try:
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": "مرحبا"}
        ],
        max_tokens=30
    )
    response = completion.choices[0].message.content
    print(f"Response: {response}")
    print(f"✅ Length: {len(response) if response else 0} chars")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Arabic with System Prompt
print("\n2. Arabic with System Prompt (Voice Assistant):")
print("-" * 60)
try:
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "أنت مساعد صوتي. أجب بالعربية دائماً بطريقة طبيعية."
            },
            {"role": "user", "content": "مرحبا، كيف حالك؟"}
        ],
        max_tokens=50,
        temperature=0.7
    )
    response = completion.choices[0].message.content
    print(f"Response: {response}")
    print(f"✅ Length: {len(response) if response else 0} chars")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Quran Question
print("\n3. Quran Question (Arabic):")
print("-" * 60)
try:
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "أنت مساعد صوتي لمساعدة الناس في حفظ القرآن. أجب بالعربية."
            },
            {"role": "user", "content": "ما هي أول آية في القرآن؟"}
        ],
        max_tokens=100,
        temperature=0.5
    )
    response = completion.choices[0].message.content
    print(f"Response: {response}")
    print(f"✅ Length: {len(response) if response else 0} chars")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Voice-Optimized Response
print("\n4. Voice-Optimized Response (Full Prompt):")
print("-" * 60)
try:
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": """أنت مساعد صوتي ذكي متخصص في مساعدة الناس في حفظ القرآن الكريم.
استجاباتك ستُقرأ بصوت عالي، لذا:
- اجعلها طبيعية ومحادثة
- استخدم جمل قصيرة
- أجب بالعربية الفصحى الواضحة
- كن مشجعاً ومحترماً"""
            },
            {"role": "user", "content": "كيف أحفظ القرآن؟"}
        ],
        max_tokens=150,
        temperature=0.75
    )
    response = completion.choices[0].message.content
    print(f"Response: {response}")
    print(f"✅ Length: {len(response) if response else 0} chars")
    if response and len(response) > 0:
        print("✅ Arabic response working!")
    else:
        print("⚠️  Empty response - model may have limitations with Arabic")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

