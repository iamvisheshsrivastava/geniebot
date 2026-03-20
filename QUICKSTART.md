# Quick Start Guide for GenieBot

## 5-Minute Setup

### Prerequisites Check
```bash
python --version  # Must be 3.9+
```

### Step 1: Clone & Setup (2 min)
```bash
cd geniebot
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 2: Install & Download (3 min)
```bash
pip install -r requirements.txt
```

### Step 3: Setup Ollama (1 min)

**Option A: GUI (Recommended for first-time)**
- Download from https://ollama.ai
- Install and open the app
- It will start automatically

**Option B: Command Line**
```bash
# Start Ollama server
ollama serve

# In another terminal, pull a model:
ollama pull mistral
```

### Step 4: Get Bot Token (1 min)
1. Open Telegram
2. Chat with [@BotFather](https://t.me/botfather)
3. Send `/newbot`
4. Follow prompts to create bot
5. Copy the token

### Step 5: Configure & Run (1 min)
```bash
# Copy env template
cp .env.example .env

# Edit .env and paste token:
# TELEGRAM_BOT_TOKEN=your_token_here

# Run bot
python app.py
```

### Step 6: Test Bot
1. Find your bot in Telegram (search by username)
2. Send `/start`
3. Try `/ask What is machine learning?`
4. Try `/image` and upload a photo

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| "ConnectionError to Ollama" | Run `ollama serve` in another terminal |
| "Model not found" | Run `ollama pull mistral` |
| "It's not responding" | Check bot token in .env |
| "Permission denied" | Run from project root directory |
| "Out of memory" | Close other apps or use smaller model |
| "No documents loaded" | Add `.txt` or `.md` files to `data/` folder |

---

## Next Steps
- Read full [README.md](README.md) for detailed documentation
- Add custom documents to `data/` folder
- Explore different Ollama models with `ollama list`
- Configure caching and memory settings in `app.py`

---

**That's it! You're ready to go!** 🚀

For full documentation, see [README.md](README.md)
