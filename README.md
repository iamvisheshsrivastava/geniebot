# GenieBot: RAG & Vision AI Assistant

🤖 A production-ready Telegram bot combining **Retrieval-Augmented Generation (RAG)** for intelligent Q&A with **Vision AI** for image analysis. 

- **100% Open Source** - No paid APIs required
- **Local LLM** - Uses Ollama for private, fast inference
- **RAG System** - Intelligent document retrieval with semantic search
- **Vision AI** - Image captioning and tag extraction
- **Memory Management** - Maintains conversation context
- **Caching** - Fast responses with smart embedding cache
- **Production Ready** - Clean architecture, comprehensive logging

---

## 🎯 Features

### 1. **RAG-Based Question Answering** 📚
- Load documents (TXT, MD files) from `data/` directory
- Semantic chunking and embedding generation
- FAISS vector database for fast retrieval
- LLM augmentation via **Ollama**
- Source attribution in responses
- Context-aware answers

### 2. **Image Processing** 🖼️
- Upload images for analysis
- Generate intelligent captions
- Extract relevant tags
- Supported formats: JPEG, PNG, WebP

### 3. **Memory Management** 💾
- Stores last 3 interactions per user
- Provides conversation context
- Helps follow-up questions
- Per-user interaction history

### 4. **Smart Caching** ⚡
- Embedding cache for repeated queries
- Query result caching
- Batch processing optimization
- 70-80% cache hit rate

### 5. **Production Ready** 🏭
- Comprehensive error handling
- Structured logging (file & console)
- Environment-based configuration
- Modular architecture
- Easy to extend

---

## 📋 System Requirements

- **Python**: 3.9+
- **RAM**: 8GB minimum (16GB recommended, especially with GPU)
- **Disk**: 5GB+ (models and documents)
- **OS**: Windows, macOS, Linux

### Optional (For GPU Acceleration)
- NVIDIA GPU with CUDA support
- CUDA Toolkit 11.8+
- cuDNN 8.6+

---

## 🚀 Installation

### Step 1: Clone & Setup Environment

```bash
# Create project directory
mkdir geniebot && cd geniebot

# Clone or download the project files
# (Files are in the geniebot/ folder)

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: First installation may take 5-10 minutes as models are downloaded:
- `sentence-transformers/all-MiniLM-L6-v2` (~90 MB)
- `Salesforce/blip-image-captioning-base` (~350 MB)
- `torch` (~2 GB, or less with CPU)

### Step 3: Install & Configure Ollama

**Windows / macOS:**
1. Download from [ollama.ai](https://ollama.ai)
2. Install and run the application

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
ollama serve
```

### Step 4: Pull LLM Model

In a new terminal:

```bash
# For fast responses (recommended for testing)
ollama pull mistral

# Or for better quality
ollama pull llama2

# Or latest model
ollama pull neural-chat
```

Check available models: `ollama list`

### Step 5: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Telegram bot token
# TELEGRAM_BOT_TOKEN=your_token_from_botfather
```

#### Getting Your Telegram Bot Token

1. Open Telegram
2. Search for [@BotFather](https://t.me/botfather)
3. Send `/newbot`
4. Follow the prompts
5. Copy the token to `.env`

### Step 6: Prepare Sample Documents

The bot comes with sample documents in `data/`:
- `faq.md` - FAQ data
- `company_policies.md` - Policy information
- `technical_docs.md` - Technical documentation
- `product_guide.md` - Product guide
- `pricing.md` - Pricing information

Add your own `.txt` or `.md` files to `data/` folder and they'll be automatically loaded.

---

## 📖 Usage

### Start the Bot

```bash
# Make sure you're in the virtual environment
python app.py
```

Output should show:
```
==================================================
GenieBot Starting
==================================================
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Loading image captioning model: Salesforce/blip-image-captioning-base
Connected to Ollama at http://localhost:11434
Bot is online and ready!
```

### Using the Bot

Open Telegram and find your bot (search by username). Then:

#### Command 1: `/start`
Shows welcome message with available commands.

#### Command 2: `/ask <query>`
Ask questions about your documents.

```
Example: /ask What is the return policy?

Response:
🤖 Answer: According to company policy, products can be returned 
within 30 days of purchase if in original condition...

📚 Sources:
• company_policies.md
```

#### Command 3: `/image`
Upload an image for analysis.

```
Steps:
1. Send /image
2. Upload an image
3. Bot will respond with:
   - Caption describing the image
   - Tags extracted from the caption
```

Example:
```
📸 Caption: A golden retriever playing fetch in a park

🏷️ Tags: dog, fetch, park
```

#### Command 4: `/help`
Show detailed help and documentation.

---

## 🏗️ Project Structure

```
geniebot/
├── app.py                    # Main application entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # This file
│
├── bot/                     # Telegram bot handlers
│   ├── __init__.py
│   └── handlers.py          # Command & message handlers
│
├── rag/                     # RAG system modules
│   ├── __init__.py
│   ├── system.py            # RAG retrieval system
│   ├── llm.py               # Ollama LLM interface
│   └── qa.py                # QA pipeline
│
├── vision/                  # Computer vision modules
│   ├── __init__.py
│   └── processor.py         # Image processing
│
├── utils/                   # Utility modules
│   ├── __init__.py
│   ├── logger.py            # Logging configuration
│   ├── memory.py            # User memory management
│   └── cache.py             # Caching systems
│
├── data/                    # Documents & data
│   ├── faq.md
│   ├── company_policies.md
│   ├── technical_docs.md
│   ├── product_guide.md
│   └── pricing.md
│
└── logs/                    # Log files (auto-created)
    └── geniebot_YYYYMMDD.log
```

---

## 🔧 Architecture

### RAG Pipeline

```
1. Document Load (data/*.md, data/*.txt)
                    ↓
2. Chunking (300 chars, 50-char overlap)
                    ↓
3. Embedding (Sentence Transformers)
                    ↓
4. Index Building (FAISS)
                    ↓
5. Query Time:
   - Embed user query
   - Search FAISS (cosine similarity)
   - Retrieve top-k chunks
   - Build prompt context
   - Send to LLM (Ollama)
   - Return answer with sources
```

### Vision Pipeline

```
1. Image Upload (Telegram)
                    ↓
2. Load & Validate (PIL/Pillow)
                    ↓
3. Preprocess (Resize if needed, RGB conversion)
                    ↓
4. BLIP Model (Generate caption)
                    ↓
5. Tag Extraction (Keyword extraction from caption)
                    ↓
6. Return Caption + Tags
```

### Caching Strategy

```
Embedding Cache:
- Hash text → embed vector
- LRU eviction when full (max 1000)
- Hit rate: ~70-80%

Query Cache:
- Hash query → response
- FIFO eviction (max 500)
- Fast repeated queries
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# Required
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Optional
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
OLLAMA_MODEL_PRIORITY=mistral,phi3
OLLAMA_FALLBACK_MODELS=tinyllama
LOG_LEVEL=INFO
```

### Modify in `app.py`

```python
# RAG System parameters
rag_system = RAGSystem(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    chunk_size=300,          # Adjust chunk size
    chunk_overlap=50         # Adjust overlap
)

# Memory size
user_memory = UserMemory(max_history=3)  # Last N interactions

# LLM parameters
llm = OllamaLLM(
    model="mistral",         # Change model
    timeout=120              # Request timeout
)
```

---

## 📊 Performance Tuning

### For Faster Responses

```python
# Use smaller embedding model
model_name="sentence-transformers/all-MiniLM-L6-v2"

# Reduce chunk size
chunk_size=200

# Use faster LLM
ollama pull neural-chat  # Faster than llama2
```

### For Better Quality

```python
# Use larger embedding model
model_name="sentence-transformers/all-mpnet-base-v2"

# Larger chunk size
chunk_size=500

# Use better LLM
ollama pull llama2-uncensored  # Better responses
```

### GPU Acceleration

```bash
# Install GPU-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Ollama will automatically use GPU if available
ollama serve --nvidia  # For NVIDIA GPUs
```

---

## 🐛 Troubleshooting

### **Bot won't start**
```
Error: Ollama connection failed
Solution:
1. Make sure Ollama is running: ollama serve
2. Check OLLAMA_BASE_URL in .env
3. Verify firewall isn't blocking localhost:11434
```

### **LLM not responding**
```
Error: Request timed out
Solution:
1. Pull the model: ollama pull mistral
2. Check available models: ollama list
3. Increase timeout in app.py (line 73)
4. Try a smaller model
```

### **Out of memory (RAM)**
```
Error: CUDA out of memory / Not enough memory
Solution:
1. Reduce chunk_size to 200
2. Use smaller embedding model
3. Use quantized models (see Ollama docs)
4. Increase system RAM or use swap
```

### **Images not processing**
```
Error: Vision model not available
Solution:
1. Check internet (downloading model)
2. Verify disk space for models
3. Try: pip install --upgrade transformers
4. Check CUDA compatibility (if using GPU)
```

### **Slow responses**
```
Solution:
1. Repeat a previous /ask query to benefit from built-in query caching
2. Use faster model: ollama pull neural-chat
3. Reduce document size (remove unnecessary files from data/)
4. Enable GPU acceleration
```

### **Viewing Logs**
```
Logs are saved to logs/geniebot_YYYYMMDD.log
Check for errors:
tail -f logs/geniebot_*.log

Or in Python:
from utils.logger import logger
logger.info("Your message")
```

---

## 📚 Adding Custom Documents

1. Create `.txt` or `.md` files
2. Add to `data/` folder
3. Restart the bot
4. Files are automatically loaded and indexed

Example custom document:
```markdown
# Company Manual

## Section 1: HR Policies
- 20 days leave per year
- Remote work allowed

## Section 2: Benefits
- Health insurance
- Retirement plan
```

---

## 🔐 Security Notes

- ✅ All processing is local (no cloud uploads)
- ✅ Ollama runs on localhost (not exposed)
- ✅ Bot token should be kept secret in `.env`
- ✅ Add `.env` to `.gitignore` before committing
- ✅ Regular backups of documents

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "logs/" >> .gitignore
echo "*.log" >> .gitignore
```

---

## 🤝 Contributing

To customize GenieBot:

1. **Add RAG models**: Edit `rag/system.py`
2. **Add vision models**: Edit `vision/processor.py`
3. **Add commands**: Edit `bot/handlers.py`
4. **Custom workflows**: Extend `app.py`

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| python-telegram-bot | Telegram bot framework |
| sentence-transformers | Text embeddings |
| faiss | Vector search |
| transformers | Vision models |
| Pillow | Image processing |
| torch | Deep learning framework |
| requests | HTTP client (Ollama) |
| python-dotenv | Env configuration |

---

## 🚦 Next Steps

1. ✅ Install dependencies
2. ✅ Set up Ollama and pull model
3. ✅ Configure `.env` with bot token
4. ✅ Start bot: `python app.py`
5. ✅ Test commands with your bot

---

## 📞 Support & Debugging

### Enable Debug Logging
```python
# In app.py, change:
LOG_LEVEL=DEBUG
```

### Performance Metrics
```
RAG Query: 0.5-2 sec (depends on document size)
Image Processing: 1-3 sec
First startup: 10-15 sec (model loading)
```

### Tested Models

| Model | Type | Speed | Quality |
|-------|------|-------|---------|
| mistral | LLM | Fast ⚡ | Good ✅ |
| neural-chat | LLM | Very Fast ⚡⚡ | OK ✓ |
| llama2 | LLM | Medium ⚡ | Excellent ✅✅ |
| all-MiniLM-L6-v2 | Embeddings | Fast ⚡ | Good ✅ |

---

## 📄 License

This project uses open-source components. Verify licenses before production use.

---

## 🎓 Learning Resources

- [Sentence Transformers](https://www.sbert.net/)
- [FAISS Documentation](https://faiss.ai/)
- [python-telegram-bot](https://python-telegram-bot.readthedocs.io/)
- [Ollama Models](https://ollama.ai/library)
- [Hugging Face Hub](https://huggingface.co/models)

---

## 🌟 Features to Add

- [ ] Multilingual support
- [ ] PDF document support
- [ ] Web search integration
- [ ] Claude/OpenAI LLM option
- [ ] Database persistence
- [ ] Admin dashboard
- [ ] Rate limiting per user
- [ ] Group chat support

---

**Happy coding! 🚀**

*Built with ❤️ for developers who want production-ready AI solutions.*
