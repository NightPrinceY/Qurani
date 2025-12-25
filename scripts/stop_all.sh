#!/bin/bash

# Stop script for Linux/WSL environment

echo "============================================================"
echo "🛑 Stopping Multi-Agent Voice Quran Assistant"
echo "============================================================"
echo ""

cd /mnt/d/Qurani 2>/dev/null || cd "$(dirname "$0")/.." 2>/dev/null || pwd

# Kill services by port (most reliable method)
echo "🔍 Finding services on ports..."
for port in 8000 8001 8002 8003 8004 8005 8006 8080; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "   Stopping service on port $port (PID: $pid)..."
        kill -9 $pid 2>/dev/null || true
    fi
done

sleep 1

# Kill services by process name (fallback)
echo ""
echo "🔍 Finding services by process name..."
services=(
    "stt_service.py"
    "stt_quran_service.py"
    "llm_router.py"
    "quran_validator.py"
    "tafsir_rag.py"
    "tts_service.py"
    "api_gateway.py"
    "web_server.py"
)

for service in "${services[@]}"; do
    pids=$(pgrep -f "$service" 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "   Stopping $service (PIDs: $pids)..."
        pkill -9 -f "$service" 2>/dev/null || true
    fi
done

sleep 1

# Kill services by PID files (if they exist)
if [ -d "logs" ]; then
    echo ""
    echo "🔍 Checking PID files..."
    for pidfile in logs/*.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile" 2>/dev/null)
            if [ ! -z "$pid" ] && ps -p $pid > /dev/null 2>&1; then
                echo "   Stopping PID $pid from $pidfile..."
                kill -9 $pid 2>/dev/null || true
            fi
            rm "$pidfile" 2>/dev/null || true
        fi
    done
fi

sleep 1

# Final check
echo ""
echo "🔍 Verifying all services are stopped..."
still_running=false
for port in 8000 8001 8002 8003 8004 8005 8006 8080; do
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "   ⚠️  Port $port is still in use"
        still_running=true
    fi
done

if [ "$still_running" = false ]; then
    echo ""
    echo "============================================================"
    echo "✅ All services stopped successfully!"
    echo "============================================================"
else
    echo ""
    echo "============================================================"
    echo "⚠️  Some services may still be running"
    echo "   Try running this script again or manually kill processes"
    echo "============================================================"
fi
echo ""

