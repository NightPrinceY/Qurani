"""
Startup script to launch all services
"""
import subprocess
import sys
import time
import os
from pathlib import Path

# Service scripts
SERVICES = [
    ("STT Service", "services/stt_service.py", 8001),
    ("LLM Router", "services/llm_router.py", 8002),
    ("Quran Validator", "services/quran_validator.py", 8003),
    ("Tafsir RAG", "services/tafsir_rag.py", 8004),
    ("TTS Service", "services/tts_service.py", 8005),
    ("API Gateway", "api_gateway.py", 8000),
]

def check_port(port):
    """Check if port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def start_service(name, script, port):
    """Start a service in a new process"""
    if not check_port(port):
        print(f"⚠️  Port {port} is already in use. Skipping {name}.")
        return None
    
    print(f"🚀 Starting {name} on port {port}...")
    try:
        process = subprocess.Popen(
            [sys.executable, script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(2)  # Give service time to start
        if process.poll() is None:
            print(f"✅ {name} started successfully (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ {name} failed to start:")
            print(stderr)
            return None
    except Exception as e:
        print(f"❌ Error starting {name}: {e}")
        return None

def main():
    """Main function to start all services"""
    print("=" * 60)
    print("Multi-Agent Voice Quran Assistant - Service Launcher")
    print("=" * 60)
    print()
    
    # Check HF token
    if not os.getenv("HF_TOKEN"):
        print("⚠️  Warning: HF_TOKEN environment variable not set!")
        print("   Set it with: export HF_TOKEN='your_token'")
        print()
    
    processes = []
    
    # Start all services
    for name, script, port in SERVICES:
        if not Path(script).exists():
            print(f"⚠️  Script not found: {script}")
            continue
        
        process = start_service(name, script, port)
        if process:
            processes.append((name, process))
        time.sleep(1)
    
    print()
    print("=" * 60)
    print(f"✅ Started {len(processes)} services")
    print("=" * 60)
    print()
    print("Services are running. Press Ctrl+C to stop all services.")
    print()
    print("API Gateway: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print()
    
    try:
        # Wait for user interrupt
        while True:
            time.sleep(1)
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} has stopped unexpectedly")
    except KeyboardInterrupt:
        print()
        print("🛑 Stopping all services...")
        for name, process in processes:
            print(f"   Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("✅ All services stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()

