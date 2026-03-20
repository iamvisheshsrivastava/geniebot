# GenieBot - Troubleshooting Guide

## Common Issues & Solutions

---

## 🔴 CRITICAL ISSUES

### Issue 1: "TELEGRAM_BOT_TOKEN not set"

**Error Message**:
```
ERROR: TELEGRAM_BOT_TOKEN not set in environment variables
ValueError: Please set TELEGRAM_BOT_TOKEN in .env file
```

**Cause**: Missing or invalid Telegram bot token

**Solutions**:
1. Check if `.env` file exists
   ```bash
   ls -la .env  # Linux/Mac
   dir .env    # Windows
   ```

2. Get your token:
   - Open Telegram
   - Search for [@BotFather](https://t.me/botfather)
   - Send `/newbot`
   - Follow prompts
   - Copy the token

3. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   ```

4. Restart bot
   ```bash
   python app.py
   ```

---

### Issue 2: "Cannot connect to Ollama"

**Error Message**:
```
ERROR: Cannot connect to Ollama at http://localhost:11434
ERROR: Make sure Ollama is running: ollama serve
```

**Cause**: Ollama server not running

**Solutions**:

**On Windows/macOS**:
1. Open Ollama application
2. It should show "Ollama is running" at the top
3. If not installed, download from [ollama.ai](https://ollama.ai)

**On Linux**:
```bash
# Start Ollama server
ollama serve

# In another terminal, verify it's running
curl http://localhost:11434/api/tags
```

**Check Ollama status**:
```bash
# Should return a list of models
ollama list

# If command not found, Ollama not installed
# Download from https://ollama.ai
```

**Alternative Port**:
If port 11434 is busy:
```bash
# Edit .env
OLLAMA_BASE_URL=http://localhost:11435

# Edit ollama configuration (if running custom)
OLLAMA_HOST=localhost:11435 ollama serve
```

---

### Issue 3: "Model not found"

**Error Message**:
```
ERROR: Ollama error: 404
Response: 'model llama2 not found'
```

**Cause**: Ollama model not downloaded

**Solutions**:
```bash
# List installed models
ollama list

# Download model (takes 5-20 minutes, 3-7GB)
ollama pull mistral  # Recommended - fast

# Or other models
ollama pull llama2
ollama pull neural-chat
ollama pull orca-mini  # Smallest, fastest

# Verify download
ollama list

# Should show your downloaded model
```

**For Slow Internet**:
- Use smaller model: `orca-mini` (1.3GB)
- Use faster model: `neural-chat` (4.1GB)

---

## 🟠 COMMON RUNTIME ISSUES

### Issue 4: "Out of Memory" (RAM)

**Error Message**:
```
MemoryError: Unable to allocate X GiB for an array
CUDA out of memory
```

**Cause**: Bot using too much RAM

**Solutions**:

**Quick Fix - Reduce Cache Sizes**:
```python
# In app.py, line ~90:
CACHE_CONFIG["embedding_cache_size"] = 200  # Was 1000
CACHE_CONFIG["query_cache_size"] = 100      # Was 500
```

**Medium Fix - Reduce Context**:
```python
# In app.py, line ~107:
user_memory = UserMemory(max_history=1)  # Was 3
```

**Aggressive Fix**:
```python
# In app.py, lines ~72-73:
rag_system = RAGSystem(
    model_name="sentence-transformers/all-MiniLM-L6-v2",  # Keep this
    chunk_size=150,      # Reduce from 300
    chunk_overlap=25     # Reduce from 50
)
```

**Check Memory Usage**:
```bash
# Windows
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory

# Linux/Mac
free -h
```

---

### Issue 5: "Slow Responses"

**Symptom**: Taking 10+ seconds per query

**Causes & Solutions**:

| Cause | Solution |
|-------|----------|
| Large model running on CPU | Use smaller model: `neural-chat` |
| Documents not indexed | Restart bot to rebuild index |
| First query ever | Normal - models load on first use |
| No cache hits | Same query twice should be faster |
| GPU not detected | Check CUDA installation |
| Many users simultaneously | Need scaling solution |

**Performance Tuning**:
```bash
# Use faster LLM
ollama pull neural-chat  # Fastest: 1-2 sec

# Or enable GPU (if NVIDIA card)
export OLLAMA_NUM_GPU=1
ollama serve
```

---

### Issue 6: "Image Processing Failed"

**Error Message**:
```
ERROR: Image processing failed
Error: Could not process image
```

**Cause**: Vision model issues or image format

**Solutions**:

**Check Image Format**:
- Supported: JPEG, PNG, WebP, BMP, GIF
- Max size: ~10MB (resizes internally)
- Min size: 50x50 pixels

**Try Uploading Different Image**:
- Different format (PNG instead of JPEG)
- Different size (preferably 100x100 to 1024x1024)
- Different source (take a fresh photo)

**Check Model Status**:
```python
# In app.py or in bot, check:
if not vision_processor.is_available():
    print("Vision model not available")
```

**Force Reinitialize**:
```bash
# Delete model cache (if it exists)
rm -rf ~/.cache/huggingface/  # Linux/Mac

# Restart bot (will redownload model)
python app.py
```

---

### Issue 7: "No Documents Loaded"

**Error Message**:
```
WARNING: No documents loaded. RAG system will be limited.
```

**Cause**: No documents in `data/` directory

**Solutions**:

**Check Data Directory**:
```bash
ls -la data/  # Should show .md or .txt files
```

**Add Sample Documents**:
- Project comes with `data/faq.md` etc.
- Add more files to `data/` folder

**Create Sample Document**:
```bash
# Create data/sample.md
echo "# Test Document

## Section 1
This is test content about AI

## Section 2  
More information here" > data/sample.md

# Restart bot - documents auto-reload
python app.py
```

**Verify Documents Loaded**:
```python
# In bot, check status:
qa_system.get_system_info()
# Should show total_chunks > 0
```

---

## 🟡 CONFIGURATION ISSUES

### Issue 8: "Wrong Model Responses"

**Symptom**: Answers are inaccurate or too short

**Solutions**:

**Use Better LLM**:
```bash
# Switch from mistral to llama2 (better quality)
ollama pull llama2

# Edit .env
OLLAMA_MODEL=llama2

# Restart bot
```

**Increase Context**:
```python
# In app.py, line ~65:
top_k_retrieval=5  # Increase from 3 for more context
```

**Use Better Embeddings**:
```python
# In app.py, line ~72:
model_name="sentence-transformers/all-mpnet-base-v2"
# (Larger but better)
```

---

### Issue 9: "Cache Not Working"

**Symptom**: Sending same query twice still takes time

**Cause**: Cache disabled or size too small

**Solutions**:

**Verify Cache Enabled**:
```python
# In app.py, line ~110:
qa_system = RAGQA(rag_system, llm, use_cache=True)  # Must be True
```

**Check Cache Stats**:
```python
# In status command output:
logger.info(qa_system.query_cache.size())
# Should increase after queries
```

**Clear Cache if Full**:
```python
# User can send /clear_cache command
# Or in code:
qa_system.query_cache.clear()
```

---

### Issue 10: "Documents Not Being Retrieved"

**Symptom**: Answers say "No relevant documents" even if they exist

**Solutions**:

**Verify Documents**:
```bash
python app.py
# Check logs for "Created X chunks from documents"
# If X=0, documents didn't load
```

**Check Document Format**:
- Must be `.txt` or `.md` files
- Not `.doc`, `.docx`, `.pdf`
- Must be in `data/` directory

**Try /status Command**:
```
/status
Should show:
  Chunks: > 0
```

**Debug Retrieval**:
```python
# Add debug logging to see what's retrieved:
chunks = rag_system.retrieve_chunks("your query", top_k=5)
for chunk, source in chunks:
    print(f"Found: {source} - {chunk[:100]}")
```

---

## 🟢 ADVANCED TROUBLESHOOTING

### Using Logs

**View Logs**:
```bash
# Latest log file
tail -f logs/geniebot_*.log

# Windows PowerShell
Get-Content logs/geniebot_*.log -Tail 20 -Wait
```

**Enable Debug Logging**:
```python
# In .env
LOG_LEVEL=DEBUG

# Restart bot - will log more details
```

**Analyze Common Errors**:
```bash
# Find all errors
grep "ERROR" logs/geniebot_*.log

# Find specific module errors
grep "RAG\|Vision\|Handler" logs/geniebot_*.log
```

---

### Performance Profiling

**Check Memory Usage**:
```python
import psutil

proc = psutil.Process()
mem = proc.memory_info().rss / 1024 / 1024
print(f"Memory usage: {mem:.2f} MB")
```

**Time Queries**:
```python
import time

start = time.time()
result = qa_system.answer_question("test")
elapsed = time.time() - start
print(f"Query took {elapsed:.2f} seconds")
```

**Profile Code**:
```bash
python -m cProfile -s cumtime app.py
```

---

### Network Issues

**Check Internet Connection**:
```bash
# Telegram API
curl -I https://api.telegram.org

# Model downloads
curl -I https://huggingface.co

# Ollama (if using remote)
curl -I http://ollama-server:11434
```

**Firewall**:
```bash
# Windows Firewall may block Ollama
# Add exception for localhost:11434
# Or use `netsh` to check
netsh advfirewall show allprofiles
```

---

## 🔧 SYSTEM HEALTH CHECK

Run this script to verify everything:

```python
#!/usr/bin/env python3

import sys
import importlib

def check_module(name):
    try:
        importlib.import_module(name)
        print(f"✅ {name}")
        return True
    except ImportError:
        print(f"❌ {name}")
        return False

print("Checking GenieBot dependencies...")
modules = [
    'telegram',
    'sentence_transformers',
    'faiss',
    'transformers',
    'PIL',
    'torch',
    'requests',
    'dotenv'
]

all_ok = all(check_module(m) for m in modules)

if all_ok:
    print("\n✅ All dependencies installed!")
else:
    print("\n❌ Missing dependencies. Run: pip install -r requirements.txt")

print("\n" + "="*50)

# Check files
from pathlib import Path

required_files = [
    'app.py',
    'bot/handlers.py',
    'rag/system.py',
    'utils/logger.py',
    'data/faq.md'
]

print("Checking project structure...")
all_exist = True
for f in required_files:
    exists = Path(f).exists()
    print(f"{'✅' if exists else '❌'} {f}")
    all_exist = all_exist and exists

print("\n" + "="*50)

if all_ok and all_exist:
    print("✅ GenieBot is ready to run!")
    print("   Next: Configure .env and run 'python app.py'")
else:
    print("❌ Issues found. See above.")
    sys.exit(1)
```

---

## 📞 Getting Help

**Before asking for help, check**:
1. ✅ Did you run `pip install -r requirements.txt`?
2. ✅ Is Ollama installed and running?
3. ✅ Did you set `TELEGRAM_BOT_TOKEN` in `.env`?
4. ✅ Did you check the logs for errors?
5. ✅ Did you try the specific fix above?

**Still stuck?**
1. Share error message
2. Share last 20 lines of log file
3. Share your system specs (RAM, OS, Python version)
4. State what you were trying to do

---

## Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Token error | Check `.env` file |
| Ollama not connected | Run `ollama serve` |
| Model not found | Run `ollama pull mistral` |
| Out of memory | Reduce `embedding_cache_size` |
| Slow responses | Use smaller model `neural-chat` |
| No documents | Add files to `data/` folder |
| Image fail | Try different image format |
| Cache not working | Verify `use_cache=True` |

---

**Most issues are configuration-related. Check `.env` and file structure first!** 🔧
