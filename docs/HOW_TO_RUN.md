# How to Run and Stop the System

## Quick Start

### Method 1: Using Bash Script (Recommended for WSL/Linux)

#### Start the System:
```bash
cd /mnt/d/Qurani
./scripts/start_system.sh
```

#### Stop the System:
```bash
cd /mnt/d/Qurani
./scripts/stop_all.sh
```

---

### Method 2: Using Python Script (Cross-platform)

#### Start the System:
```bash
cd /mnt/d/Qurani
source venv/bin/activate  # Activate virtual environment
python start_services.py
```

**Note:** Press `Ctrl+C` to stop all services when using this method.

#### Stop the System:
Press `Ctrl+C` in the terminal where `start_services.py` is running.

---

## Detailed Instructions

### Prerequisites

1. **Virtual Environment**: Make sure you have activated the virtual environment
   ```bash
   source venv/bin/activate  # Linux/WSL
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Hugging Face Token**: Set your HF_TOKEN (optional, uses default from config if not set)
   ```bash
   export HF_TOKEN="your_token_here"
   ```

### Starting the System

#### Step 1: Navigate to Project Directory
```bash
cd /mnt/d/Qurani  # WSL path
# or
cd D:\Qurani      # Windows path
```

#### Step 2: Activate Virtual Environment
```bash
source venv/bin/activate  # Linux/WSL
```

#### Step 3: Start Services

**Option A: Using Bash Script (Recommended)**
```bash
chmod +x scripts/start_system.sh  # Make executable (first time only)
./scripts/start_system.sh
```

**Option B: Using Python Script**
```bash
python start_services.py
```

#### Step 4: Start Web Interface (if not started automatically)

The `start_system.sh` script automatically starts the web interface. If you're using `start_services.py`, you need to start it separately:

```bash
python web_server.py
```

### What Gets Started

The system starts the following services:

1. **STT Service** - Port 8001
   - Speech-to-Text conversion
   - URL: http://localhost:8001

2. **LLM Router** - Port 8002
   - Intent classification and routing
   - URL: http://localhost:8002

3. **Quran Validator** - Port 8003
   - Recitation validation
   - URL: http://localhost:8003

4. **Tafsir RAG** - Port 8004
   - Verse interpretation
   - URL: http://localhost:8004

5. **TTS Service** - Port 8005
   - Text-to-Speech (placeholder)
   - URL: http://localhost:8005

6. **API Gateway** - Port 8000
   - Main entry point
   - URL: http://localhost:8000
   - API Docs: http://localhost:8000/docs

7. **Web Interface** - Port 8080
   - User interface
   - URL: http://localhost:8080

### Accessing the System

Once all services are started:

1. **Open your web browser**
2. **Navigate to**: http://localhost:8080
3. **You should see**: The voice assistant interface with the animated visualizer

### Stopping the System

#### Method 1: Using Stop Script (Recommended)
```bash
cd /mnt/d/Qurani
./scripts/stop_all.sh
```

#### Method 2: Manual Stop (if script doesn't work)
```bash
# Kill all Python processes running the services
pkill -f "stt_service.py"
pkill -f "llm_router.py"
pkill -f "quran_validator.py"
pkill -f "tafsir_rag.py"
pkill -f "tts_service.py"
pkill -f "api_gateway.py"
pkill -f "web_server.py"
```

#### Method 3: Kill by Port
```bash
# Kill processes on specific ports
for port in 8000 8001 8002 8003 8004 8005 8080; do
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
done
```

### Checking Service Status

#### Check if Services are Running:
```bash
# Check all ports
netstat -tuln | grep -E ':(8000|8001|8002|8003|8004|8005|8080)'

# Or use the check script
./scripts/check_services.sh
```

#### Check Service Health:
```bash
# Check API Gateway health
curl http://localhost:8000/health

# Or open in browser
# http://localhost:8000/health
```

### Viewing Logs

All service logs are saved in the `logs/` directory:

```bash
# View all logs
ls -lh logs/

# View specific service log
tail -f logs/STT.log
tail -f logs/LLM_Router.log
tail -f logs/API_Gateway.log
tail -f logs/Web_Server.log

# View all logs in real-time
tail -f logs/*.log
```

### Troubleshooting

#### Port Already in Use
If you get "port already in use" errors:

```bash
# Kill processes on those ports
./scripts/stop_all.sh

# Or manually
for port in 8000 8001 8002 8003 8004 8005 8080; do
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
done
```

#### Service Not Starting
1. Check the logs: `tail -f logs/[Service_Name].log`
2. Verify virtual environment is activated: `which python`
3. Check if dependencies are installed: `pip list | grep fastapi`
4. Verify HF_TOKEN is set: `echo $HF_TOKEN`

#### Web Interface Not Loading
1. Check if web server is running: `curl http://localhost:8080/health`
2. Check web server logs: `tail -f logs/Web_Server.log`
3. Verify port 8080 is not blocked by firewall

#### Services Keep Crashing
1. Check system resources: `free -h` and `nvidia-smi` (for GPU)
2. Verify all dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (should be 3.8+)

### Quick Reference

| Action | Command |
|--------|---------|
| **Start System** | `./scripts/start_system.sh` |
| **Stop System** | `./scripts/stop_all.sh` |
| **Check Status** | `./scripts/check_services.sh` |
| **View Logs** | `tail -f logs/*.log` |
| **Web Interface** | http://localhost:8080 |
| **API Docs** | http://localhost:8000/docs |

### Running in Background

If you want to run the system in the background and detach from terminal:

```bash
# Start in background
nohup ./scripts/start_system.sh > startup.log 2>&1 &

# Check if running
ps aux | grep python

# Stop later
./scripts/stop_all.sh
```

---

## Example Workflow

### Complete Start-to-Stop Example:

```bash
# 1. Navigate to project
cd /mnt/d/Qurani

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start all services
./scripts/start_system.sh

# 4. Wait for "System startup complete!" message

# 5. Open browser to http://localhost:8080

# 6. Use the system...

# 7. When done, stop all services
./scripts/stop_all.sh
```

---

**Note:** Make sure you're in the WSL environment (if using Windows) and have activated the virtual environment before starting services.

