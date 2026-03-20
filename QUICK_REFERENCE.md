# 🎯 QUICK REFERENCE - Your Exact Steps

## COPY & PASTE THESE COMMANDS

### Terminal 1: Setup
```bash
cd c:\Users\sriva\Desktop\Projects\Personal Repositories\testing_DELME\geniebot

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```
⏱️ **Wait: 3-5 minutes** for downloads

---

### Configure Bot Token

```bash
# View .env file
notepad .env
```

**Edit this line** in .env:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

Replace with your actual token from @BotFather

---

### Terminal 2: Run Bot
```bash
python app.py
```

🎉 **Bot is now LIVE!**

---

## ❓ Your Questions Answered

### Q1: "Do I need API for HuggingFace vision model?"

**Answer: NO** ❌ No API needed

- Vision model **automatically downloads** on first use
- It's **free and public** from HuggingFace Hub
- For **Salesforce BLIP** (image captioning)
- ~350 MB, downloads once, then cached
- No authentication required - just works!

---

### Q2: "What do I do to start this project?"

**3 simple steps:**

1. **Setup Python**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Get Bot Token** from @BotFather in Telegram
   - Add to `.env` file

3. **Run Bot**
   ```bash
   python app.py
   ```

---

### Q3: "Can I just use Gemma 3.4b?"

**Yes! Already done!** ✅

- Updated code to use **Gemma 3.4b by default**
- Your `.env.example` now shows `OLLAMA_MODEL=gemma3:4b`
- No configuration needed - it's the default!

---

## 📊 What Each Model Does

| Model | Purpose | Size | Auto-Download | API Needed |
|-------|---------|------|----------------|-----------|
| **Gemma 3.4b** | Text responses | Already have | ❌ | ❌ |
| **all-MiniLM-L6-v2** | Search/find info | 90 MB | ✅ Yes | ❌ |
| **BLIP** | Image captions | 350 MB | ✅ Yes | ❌ |

**All downloads are FREE - no API keys needed!**

---

## ✨ Your Bot Commands

**After running `python app.py`:**

1. `/start` → Welcome
2. `/ask What is AI?` → Get answer from documents
3. `/image` → Upload photo → Get caption + tags
4. `/history` → See your chats
5. `/status` → System info
6. `/help` → Help text

---

## 🔄 Model Download Timeline (First Run Only)

```
1. Start bot: python app.py
   ↓
2. Load Gemma 3.4b (already have!)
   ✅ Complete
   ↓
3. Load Sentence Transformers (~90 MB)
   ⏳ 2-3 minutes
   ↓
4. Load BLIP for images (~350 MB)
   ⏳ 2-3 minutes
   ↓
5. Ready to use!
   ✅ All future runs: ~5 seconds startup
```

---

## 🎨 Model Details

### **LLM: Gemma 3.4b** (Your choice - excellent!)
- ✅ Already running on Ollama
- 📊 4 billion parameters
- ⚡ Fast & efficient
- 💾 ~2-3 GB memory
- 🎯 Good for conversational AI

### **Embedding: all-MiniLM-L6-v2** (Auto-downloads)
- 📏 Creates vectors for search
- 🔍 Finds relevant documents
- ⚡ Very fast
- 💾 Small: 90 MB

### **Vision: Salesforce BLIP** (Auto-downloads)
- 📸 Describes images  
- 🏷️ Extracts tags
- 🎨 Good quality captions
- 💾 ~350 MB

---

## ⚠️ Common Mistakes to Avoid

❌ **Don't forget to:**
- Copy `.env.example` to `.env`
- Add actual bot token to `.env`
- Keep Ollama running while bot runs

❌ **Don't try to install:**
- HuggingFace API (not needed)
- OpenAI (not used)
- Other LLM services (Gemma 3.4b is enough)

✅ **Just run:**
```bash
python app.py
```

---

## 📱 Test It

1. Open Telegram
2. Find your bot (search by username)
3. Send: `/start`
4. Send: `/ask What is machine learning?`
5. Send: `/image` then upload any photo

**Done!** You're using GenieBot with Gemma 3.4b! 🎉

---

## 🆘 If Bot Doesn't Start

### Check 1: Is Ollama Running?
```bash
ollama list
```

### Check 2: Is Token Correct?
```bash
notepad .env
# Look for: TELEGRAM_BOT_TOKEN=your_actual_token
```

### Check 3: Check Logs
```
Look in: geniebot/logs/geniebot_*.log
```

---

## 💡 Pro Tips

**Tip 1**: Keep Ollama open in background while bot runs

**Tip 2**: Virtual environment activates fresh each terminal:
```bash
venv\Scripts\activate
```

**Tip 3**: Check bot is running:
```
Bot logs should show: "Bot is online and ready!"
```

**Tip 4**: Share documents in `data/` folder to add more knowledge

---

## 🎓 Next Level

**After bot is working:**
- Add more `.md` files to `data/` folder
- Change embedding model in `config.py`
- Try different Ollama models
- Read `ADVANCED_CONFIG.md` for tuning

---

## ✅ YES or NO Answers

| Question | Answer |
|----------|--------|
| Need HF API for vision? | **NO** |
| Need OpenAI API? | **NO** |
| Need internet after setup? | **NO** |
| Can I use Gemma 3.4b only? | **YES** ✅ |
| Is setup hard? | **NO** - 3 steps |
| Will it work on my computer? | **YES** ✅ |

---

**Your bot is ready! 🚀 Just run: `python app.py`**

*Questions? Check `YOUR_SETUP.md` in geniebot folder*
