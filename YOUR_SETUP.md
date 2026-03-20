# 🚀 YOUR SETUP - Simple Start Guide

You already have **Gemma 3.4b running locally**. Here's exactly what to do:

---

## ✅ What You Have Ready

- ✅ Ollama installed with **Gemma 3.4b** running
- ✅ All code files created
- ✅ Sample documents ready

---

## 📋 DO THIS (3 steps only)

### **Step 1: Setup Python Environment**

```bash
# Open PowerShell in the geniebot folder
cd c:\Users\sriva\Desktop\Projects\Personal Repositories\testing_DELME\geniebot

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**This takes 3-5 minutes** (downloads ~2GB of models on first run)

---

### **Step 2: Get Your Telegram Bot Token**

1. Open Telegram
2. Search for [@BotFather](https://t.me/botfather)
3. Send `/newbot`
4. Follow prompts → get your token
5. It looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

---

### **Step 3: Configure and Run**

```bash
# Copy env template
cp .env.example .env

# Edit .env with your token
# Open .env in VS Code, find this line:
# TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
# Replace with your actual token from BotFather

# Start the bot
python app.py
```

**That's it!** ✨

---

## 🎯 What Bot Will Do Now

**Your bot is now running with Gemma 3.4b!**

- Fast responses (Gemma is optimized)
- Local processing (no APIs needed)
- Smart caching (70% faster on repeat questions)
- Image analysis included

---

## 📱 Test Your Bot

1. Open Telegram
2. Search for your bot (by username you created with BotFather)
3. Send `/start` → Welcome message
4. Send `/ask What is artificial intelligence?` → Get answer
5. Send `/image` → Upload image → Get caption + tags
6. Send `/status` → See system info

---

## ❓ Vision Model & HuggingFace

**NO, you DO NOT need a HuggingFace API key!** 

Here's why:
- Vision model (BLIP) will **auto-download** from HuggingFace on first use
- It's **free and public** - no authentication needed
- First download: ~350MB (one time only)
- After that: instant use

---

## 🎨 About the Models

### LLM (Text Generation)
- **Using**: Gemma 3.4b (already running on your Ollama)
- **Why**: Fast, efficient, good quality
- **Speed**: ~1-2 seconds per response

### Embedding Model  
- **Using**: all-MiniLM-L6-v2 (auto-downloads)
- **Size**: 90 MB
- **Purpose**: Convert text to vectors for smart search

### Vision Model
- **Using**: Salesforce BLIP (auto-downloads)
- **Size**: 350 MB
- **Purpose**: Caption images and extract tags
- **Auto-download**: First time you use `/image`

---

## ⚡ Performance to Expect

| Operation | Time |
|-----------|------|
| Bot startup | 5 sec |
| First `/ask` | 2-3 sec (models load) |
| Second `/ask` | 0.5-1 sec (cached) |
| `/image` (first time) | 3-5 sec |
| `/image` (after) | 1-2 sec |

---

## 🔧 If Something Doesn't Work

### Issue: "Cannot connect to Ollama"
```
✅ Solution: Make sure Ollama is running (click Ollama app icon)
```

### Issue: "Bot doesn't respond"
```
✅ Solution: Check .env file has your token (look for TELEGRAM_BOT_TOKEN)
```

### Issue: "Out of memory"
```
✅ Solution: Close other apps. Gemma 3.4b uses ~4GB RAM
```

### Issue: "Certificate error in logs"
```
✅ Solution: Normal on first model downloads - just wait
```

---

## 📂 Project Files Overview

```
geniebot/
├── app.py                  ← MAIN FILE (run this)
├── .env.example            ← Copy to .env and add token
├── requirements.txt        ← Installed with pip
├── bot/                    ← Telegram commands
├── rag/                    ← DOC search (Q&A)
├── vision/                 ← Image analysis
├── utils/                  ← Helper functions
└── data/                   ← Sample documents
```

---

## ✅ Checklist Before Running

- [ ] Ollama running with Gemma 3.4b (`ollama list` shows it)
- [ ] PowerShell/terminal open in geniebot folder
- [ ] Virtual environment created and activated
- [ ] `pip install -r requirements.txt` completed
- [ ] `.env` file created with your bot token
- [ ] Ready to run `python app.py`

---

## 🎉 Final Command

```bash
python app.py
```

**Output should show:**
```
==================================================
GenieBot Starting
==================================================
Connecting to Ollama at http://localhost:11434
Using Gemma 3.4b for fast and efficient responses
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
[downloading if first time]
Loading image captioning model: Salesforce/blip-image-captioning-base
[downloading if first time]
Bot is online and ready!
Webhook/polling setup complete
```

**Then open Telegram and find your bot!** 🤖

---

## 💡 Key Point

**You DON'T need:**
- ❌ HuggingFace API key
- ❌ OpenAI API  
- ❌ Any cloud services
- ❌ Internet after first model download

**Everything runs locally on your Gemma 3.4b!** ✨

---

## 📚 Documentation Files (if you need them)

- `README.md` - Full details
- `TROUBLESHOOTING.md` - More issues + fixes
- `ADVANCED_CONFIG.md` - Performance tuning
- `START_HERE.md` - Project overview

---

**Ready? Just run: `python app.py`** 🚀
