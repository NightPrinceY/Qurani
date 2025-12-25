#!/bin/bash

# Quick service status checker

echo "🔍 Checking service status..."
echo ""

services=(
    "STT:8001:/health"
    "LLM Router:8002:/health"
    "Quran Validator:8003:/health"
    "Tafsir RAG:8004:/health"
    "TTS:8005:/health"
    "API Gateway:8000:/health"
    "Web Interface:8080:/"
)

for service_info in "${services[@]}"; do
    IFS=':' read -r name port endpoint <<< "$service_info"
    
    if curl -s http://localhost:$port$endpoint > /dev/null 2>&1; then
        echo "✅ $name (port $port) - Running"
    else
        echo "❌ $name (port $port) - Not responding"
    fi
done

echo ""
echo "📋 Process check:"
ps aux | grep -E "(stt_service|llm_router|quran_validator|tafsir_rag|tts_service|api_gateway|web_server)" | grep -v grep | head -10

