#!/usr/bin/env python3
"""
Test OSS Model using the exact API format from model card
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from huggingface_hub import InferenceClient

# Get token from config or environment
try:
    from config import HF_TOKEN, LLM_MODEL
except ImportError:
    HF_TOKEN = os.getenv("HF_TOKEN", "")
    LLM_MODEL = "openai/gpt-oss-20b"

if not HF_TOKEN:
    print("❌ ERROR: HF_TOKEN not set!")
    print("Please set it in config.py or as environment variable")
    sys.exit(1)

print("=" * 60)
print("Testing OSS Model - Using Model Card API Format")
print("=" * 60)
print(f"Model: {LLM_MODEL}")
print(f"Token: {HF_TOKEN[:10]}...{HF_TOKEN[-5:]}")
print()

# Initialize client exactly as in model card
client = InferenceClient(api_key=HF_TOKEN)

# Test 1: Simple test (non-streaming) - like model card example
print("Test 1: Simple Question (Non-Streaming)")
print("-" * 60)
try:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ],
    )
    response = completion.choices[0].message.content
    print(f"✅ Response: {response}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 2: Streaming (as in model card example)
print("\nTest 2: Streaming Response")
print("-" * 60)
try:
    stream = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ],
        stream=True,
    )
    print("✅ Streaming response: ", end="")
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()  # New line after streaming
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 3: Arabic greeting (voice assistant style)
print("\nTest 3: Arabic Greeting (Voice Assistant)")
print("-" * 60)
try:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "أنت مساعد صوتي ذكي لمساعدة الناس في حفظ القرآن. أجب دائماً بالعربية بطريقة طبيعية ومناسبة للصوت."
            },
            {
                "role": "user",
                "content": "مرحبا"
            }
        ],
        temperature=0.75,
        max_tokens=50
    )
    response = completion.choices[0].message.content
    print(f"✅ Response: {response}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 4: Quran question (voice-optimized)
print("\nTest 4: Quran Question (Voice-Optimized)")
print("-" * 60)
try:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": """أنت مساعد صوتي متخصص في مساعدة الناس في حفظ القرآن الكريم.
استجاباتك ستُقرأ بصوت عالي، لذا:
- اجعلها طبيعية ومحادثة
- استخدم جمل قصيرة ومناسبة للصوت
- كن مشجعاً ومحترماً
- أجب بالعربية الفصحى الواضحة"""
            },
            {
                "role": "user",
                "content": "ما هي أول آية في القرآن؟"
            }
        ],
        temperature=0.7,
        max_tokens=100
    )
    response = completion.choices[0].message.content
    print(f"✅ Response: {response}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 5: JSON response format (for validation)
print("\nTest 5: JSON Response Format (Validation)")
print("-" * 60)
try:
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "أنت خبير في القرآن. أجب بصيغة JSON فقط."
            },
            {
                "role": "user",
                "content": "تحقق من هذه التلاوة: بسم الله الرحمن الرحيم"
            }
        ],
        temperature=0.1,
        max_tokens=200,
        response_format={"type": "json_object"}
    )
    response = completion.choices[0].message.content
    print(f"✅ JSON Response: {response}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! OSS model is working correctly.")
print("=" * 60)
print("\n📝 Model API Format Verified:")
print("   - Model: 'openai/gpt-oss-20b' (no colon)")
print("   - Client: InferenceClient(api_key=HF_TOKEN)")
print("   - Method: client.chat.completions.create()")
print("   - Streaming: Supported with stream=True")
print("   - JSON format: Supported with response_format")
