#!/bin/bash

# Start Multi-Agent Voice Quran Assistant System
# Uses existing venv without installing new libraries

echo "============================================================"
echo "🚀 Starting Multi-Agent Voice Quran Assistant"
echo "============================================================"
echo ""

cd /mnt/d/Qurani

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    exit 1
fi

source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Set HF_TOKEN if not already set
if [ -z "$HF_TOKEN" ]; then
    export HF_TOKEN="your_huggingface_token_here"
    echo "⚠️  Using default HF_TOKEN from config"
fi

# Create logs directory
mkdir -p logs

# Kill any existing services on these ports
echo "🧹 Cleaning up any existing services..."
for port in 8000 8001 8002 8003 8004 8005 8006 8080; do
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
done
sleep 2
echo ""

# Start services in background
echo "🔧 Starting services..."
echo ""

# STT Service (port 8001)
echo "   Starting STT Service on port 8001..."
nohup python services/stt_service.py > logs/STT.log 2>&1 &
STT_PID=$!
sleep 5
if ps -p $STT_PID > /dev/null; then
    echo "   ✅ STT Service started (PID: $STT_PID)"
else
    echo "   ❌ STT Service failed to start. Check logs/STT.log"
fi

# Quran STT Service (port 8006)
echo "   Starting Quran STT Service on port 8006..."
nohup python services/stt_quran_service.py > logs/Quran_STT.log 2>&1 &
QURAN_STT_PID=$!
sleep 5
if ps -p $QURAN_STT_PID > /dev/null; then
    echo "   ✅ Quran STT Service started (PID: $QURAN_STT_PID)"
else
    echo "   ❌ Quran STT Service failed to start. Check logs/Quran_STT.log"
fi

# LLM Router (port 8002)
echo "   Starting LLM Router on port 8002..."
nohup python services/llm_router.py > logs/LLM_Router.log 2>&1 &
LLM_PID=$!
sleep 3
if ps -p $LLM_PID > /dev/null; then
    echo "   ✅ LLM Router started (PID: $LLM_PID)"
else
    echo "   ❌ LLM Router failed to start. Check logs/LLM_Router.log"
fi

# Quran Validator (port 8003)
echo "   Starting Quran Validator on port 8003..."
nohup python services/quran_validator.py > logs/Quran_Validator.log 2>&1 &
VALIDATOR_PID=$!
sleep 3
if ps -p $VALIDATOR_PID > /dev/null; then
    echo "   ✅ Quran Validator started (PID: $VALIDATOR_PID)"
else
    echo "   ❌ Quran Validator failed to start. Check logs/Quran_Validator.log"
fi

# Tafsir RAG (port 8004)
echo "   Starting Tafsir RAG on port 8004..."
nohup python services/tafsir_rag.py > logs/Tafsir_RAG.log 2>&1 &
TAFSIR_PID=$!
sleep 3
if ps -p $TAFSIR_PID > /dev/null; then
    echo "   ✅ Tafsir RAG started (PID: $TAFSIR_PID)"
else
    echo "   ❌ Tafsir RAG failed to start. Check logs/Tafsir_RAG.log"
fi

# TTS Service (port 8005)
echo "   Starting TTS Service on port 8005..."
nohup python services/tts_service.py > logs/TTS.log 2>&1 &
TTS_PID=$!
sleep 3
if ps -p $TTS_PID > /dev/null; then
    echo "   ✅ TTS Service started (PID: $TTS_PID)"
else
    echo "   ❌ TTS Service failed to start. Check logs/TTS.log"
fi

# API Gateway (port 8000)
echo "   Starting API Gateway on port 8000..."
nohup python api_gateway.py > logs/API_Gateway.log 2>&1 &
GATEWAY_PID=$!
sleep 3
if ps -p $GATEWAY_PID > /dev/null; then
    echo "   ✅ API Gateway started (PID: $GATEWAY_PID)"
else
    echo "   ❌ API Gateway failed to start. Check logs/API_Gateway.log"
fi

# Web Server (port 8080)
echo "   Starting Web Interface on port 8080..."
nohup python web_server.py > logs/Web_Server.log 2>&1 &
WEB_PID=$!
sleep 3
if ps -p $WEB_PID > /dev/null; then
    echo "   ✅ Web Interface started (PID: $WEB_PID)"
else
    echo "   ❌ Web Interface failed to start. Check logs/Web_Server.log"
fi

echo ""
echo "============================================================"
echo "✅ System startup complete!"
echo "============================================================"
echo ""
echo "📊 Service Status:"
echo "   - STT Service:        http://localhost:8001"
echo "   - Quran STT Service:  http://localhost:8006"
echo "   - LLM Router:         http://localhost:8002"
echo "   - Quran Validator:    http://localhost:8003"
echo "   - Tafsir RAG:         http://localhost:8004"
echo "   - TTS Service:        http://localhost:8005"
echo "   - API Gateway:        http://localhost:8000"
echo "   - Web Interface:      http://localhost:8080"
echo ""
echo "📝 API Documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "📋 Process IDs (save these to stop services):"
echo "   STT: $STT_PID"
echo "   Quran STT: $QURAN_STT_PID"
echo "   LLM: $LLM_PID"
echo "   Validator: $VALIDATOR_PID"
echo "   Tafsir: $TAFSIR_PID"
echo "   TTS: $TTS_PID"
echo "   Gateway: $GATEWAY_PID"
echo "   Web: $WEB_PID"
echo ""
echo "🛑 To stop all services, run:"
echo "   ./stop_all.sh"
echo ""
echo "📋 To check logs:"
echo "   tail -f logs/*.log"
echo ""

