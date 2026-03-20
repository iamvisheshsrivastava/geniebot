# GenieBot - Complete File Reference

## Project Structure & File Description

```
geniebot/
├── 📄 ROOT LEVEL FILES
│   ├── app.py                  ✅ MAIN - Bot entry point, system initialization
│   ├── config.py               ✅ Configuration and settings management
│   ├── requirements.txt         ✅ Python dependencies
│   ├── requirements_dev.txt     📚 Dev dependencies (testing, linting, docs)
│   ├── .env.example             🔐 Environment variables template
│   ├── .gitignore              🔒 Git ignore patterns
│   │
│   ├── 📖 DOCUMENTATION
│   ├── README.md                ⭐ Complete documentation & setup guide
│   ├── QUICKSTART.md            🚀 Fast 5-minute setup
│   ├── ADVANCED_CONFIG.md       🔧 Advanced configuration options
│   ├── DEVELOPMENT.md           👨‍💻 Development & contribution guide
│   ├── PROJECT_INFO.md          📋 Project overview
│   │
│   ├── 🤖 BOT MODULE
│   └── bot/
│       ├── __init__.py          - Module initialization
│       └── handlers.py          ⭐ Telegram command handlers
│           ├── start()          - /start command
│           ├── help_command()   - /help command
│           ├── ask_command()    - /ask command (RAG)
│           ├── image_command()  - /image command setup
│           ├── handle_image()   - Image upload handler
│           ├── history_command()- /history command
│           ├── status_command() - /status command
│           ├── clear_cache_command() - /clear_cache
│           └── error_handler()  - Error handling
│
│   ├── 🧠 RAG MODULE (Retrieval Augmented Generation)
│   └── rag/
│       ├── __init__.py          - Module initialization
│       ├── system.py            ⭐ RAG retrieval system
│       │   ├── load_documents()     - Load .txt/.md files
│       │   ├── _chunk_documents()   - Split into chunks
│       │   ├── _generate_embeddings()- Create embeddings
│       │   ├── retrieve_chunks()    - Find relevant chunks
│       │   ├── get_rag_context()    - Build context for LLM
│       │   ├── get_source_chunks()  - Get source attribution
│       │   └── get_stats()          - System statistics
│       │
│       ├── llm.py               ⭐ Ollama LLM interface
│       │   ├── generate()       - Generate text
│       │   ├── chat()          - Chat-style generation
│       │   ├── is_available()  - Check Ollama status
│       │   └── get_available_models() - List models
│       │
│       └── qa.py                ⭐ QA pipeline
│           ├── answer_question()    - Generate answer with sources
│           ├── get_answer_with_sources() - Formatted output
│           └── get_system_info()    - System information
│
│   ├── 👁️ VISION MODULE (Image Analysis)
│   └── vision/
│       ├── __init__.py          - Module initialization
│       └── processor.py         ⭐ Image processing
│           ├── generate_caption()   - Caption generation
│           ├── extract_tags()      - Tag extraction
│           ├── process_image()     - Complete pipeline
│           └── is_available()      - Check model status
│
│   ├── 🛠️ UTILS MODULE (Utilities)
│   └── utils/
│       ├── __init__.py          - Module initialization
│       ├── logger.py            ⭐ Structured logging
│       │   └── setup_logger()   - Configure logger
│       │
│       ├── memory.py            ⭐ User memory management
│       │   ├── add_interaction()    - Store interaction
│       │   ├── get_history()        - Retrieve history
│       │   ├── get_context()        - Get LLM context
│       │   └── clear_history()      - Clear history
│       │
│       └── cache.py             ⭐ Caching systems
│           ├── EmbeddingCache   - Cache embeddings
│           │   ├── get()        - Retrieve from cache
│           │   ├── put()        - Store in cache
│           │   ├── stats()      - Cache statistics
│           │   └── clear()      - Clear cache
│           │
│           └── QueryCache       - Cache responses
│               ├── get()        - Retrieve response
│               ├── put()        - Store response
│               ├── size()       - Cache size
│               └── clear()      - Clear cache
│
│   ├── 📚 DATA MODULE (Documents)
│   └── data/
│       ├── faq.md                - FAQ document
│       ├── faq.txt               - FAQ (text version)
│       ├── company_policies.md   - Company policies
│       ├── policies.txt          - Policies (text version)
│       ├── technical_docs.md     - Technical documentation
│       ├── documentation.txt     - Documentation (text)
│       ├── product_guide.md      - Product guide
│       ├── knowledge.txt         - Knowledge base
│       └── pricing.md            - Pricing information
│
│   └── 📋 LOGS (Auto-created)
│       └── logs/
│           └── geniebot_YYYYMMDD.log  - Daily log files
```

---

## File Categories

### 🚀 START HERE
- `QUICKSTART.md` - 5-minute setup
- `README.md` - Full documentation
- `app.py` - Main entry point

### 🤖 BOT LOGIC
- `bot/handlers.py` - All commands
- `app.py` - Bot initialization

### 🧠 RAG SYSTEM
- `rag/system.py` - Document retrieval
- `rag/llm.py` - LLM communication
- `rag/qa.py` - QA pipeline

### 👁️ VISION AI
- `vision/processor.py` - Image analysis

### 🛠️ UTILITIES
- `utils/logger.py` - Logging
- `utils/memory.py` - Conversation history
- `utils/cache.py` - Performance caching

### ⚙️ CONFIGURATION
- `config.py` - Centralized settings
- `.env.example` - Environment template
- `ADVANCED_CONFIG.md` - Tuning options

### 📚 DATA
- `data/*.md` - Sample documents
- `data/*.txt` - Text versions

### 📖 DOCUMENTATION
- `README.md` - Primary guide
- `QUICKSTART.md` - Fast setup
- `ADVANCED_CONFIG.md` - Advanced tuning
- `DEVELOPMENT.md` - Developer guide
- `PROJECT_INFO.md` - Project overview

---

## Key Components Explained

### 1. RAG System (`rag/`)
**Purpose**: Answer questions based on documents

**Flow**:
```
Documents → Chunks → Embeddings → FAISS Index
                          ↓
                    Query Time: Retrieve top-K
                          ↓
                    Build context → Send to LLM
                          ↓
                    Return answer + sources
```

**Files**:
- `system.py` - Document loading and indexing
- `llm.py` - Ollama communication
- `qa.py` - QA pipeline orchestration

### 2. Vision System (`vision/`)
**Purpose**: Caption images and extract tags

**Flow**:
```
Image → Load & Validate → BLIP Model → Caption
                               ↓
                         Tag Extraction
```

**Files**:
- `processor.py` - Image processing pipeline

### 3. Bot Handlers (`bot/`)
**Purpose**: Telegram command processing

**Commands**:
- `/start` → Welcome
- `/ask <q>` → RAG answer
- `/image` → Upload image
- `/history` → Show history
- `/status` → System status
- `/help` → Help text
- `/clear_cache` → Clear cache

**Files**:
- `handlers.py` - All command implementations

### 4. Memory System (`utils/memory.py`)
**Purpose**: Store conversation context

**Features**:
- Last 3 interactions per user
- Provides context for follow-ups
- Easy access to history

### 5. Caching System (`utils/cache.py`)
**Purpose**: Speed up responses

**Types**:
- Embedding cache: Reuse embeddings
- Query cache: Store full responses
- Hit rate: 70-80%

### 6. Logging System (`utils/logger.py`)
**Purpose**: Track operations and debug

**Output**:
- Console: INFO level
- File: DEBUG level (daily logs)

---

## Data Flow Diagram

### Text Query (`/ask`)
```
User Input (/ask "What is AI?")
        ↓
[bot/handlers.py: ask_command()]
        ↓
[rag/qa.py: answer_question()]
        ↓
[rag/system.py: retrieve_chunks()]
        ↓
[FAISS Index: Search]
        ↓
[rag/llm.py: generate()]
        ↓
[Ollama LLM]
        ↓
[utils/memory.py: Store interaction]
        ↓
[utils/cache.py: Cache response]
        ↓
Response with sources → Telegram → User
```

### Image Query (`/image`)
```
Image Upload
        ↓
[bot/handlers.py: handle_image()]
        ↓
[vision/processor.py: process_image()]
        ↓
[BLIP Model: Caption]
        ↓
[Extract tags]
        ↓
[utils/memory.py: Store interaction]
        ↓
Caption + Tags → Telegram → User
```

---

## Critical Files to Understand First

1. **`app.py`** - Understand initialization order
2. **`bot/handlers.py`** - See all commands
3. **`rag/system.py`** - Understand RAG pipeline
4. **`rag/llm.py`** - See LLM communication
5. **`utils/cache.py`** - Performance optimization

---

## Common File Modifications

| Want to... | Edit this file |
|-----------|---------------|
| Add command | `bot/handlers.py` + register in `app.py` |
| Change chunk size | `config.py` or `app.py` line 73 |
| Use different LLM | `.env` OLLAMA_MODEL |
| Use different embedding model | `app.py` line 72 |
| Increase memory size | `app.py` line 107 `max_history=5` |
| Change cache size | `app.py` or `config.py` |
| Add document | Add `.md` or `.txt` to `data/` |
| Change logging level | `.env` LOG_LEVEL |

---

## File Dependencies

```
app.py
├── bot/handlers.py
├── rag/system.py
├── rag/llm.py
├── rag/qa.py (imports system, llm)
├── vision/processor.py
├── utils/logger.py
├── utils/memory.py
├── utils/cache.py
└── config.py

bot/handlers.py
├── rag/qa.py
├── vision/processor.py
├── utils/logger.py
└── utils/memory.py

rag/system.py
├── utils/logger.py
└── utils/cache.py

rag/llm.py
└── utils/logger.py

vision/processor.py
└── utils/logger.py

utils/logger.py (no dependencies)
utils/memory.py (no dependencies)
utils/cache.py (no dependencies)
```

---

## Version Control

**Git ignore** (`.gitignore`):
- `.env` - Keep secrets local
- `logs/` - Keep log files local
- `venv/` - Don't commit virtual env
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python

**Good commits**:
```
✅ "Add support for PDF documents"
✅ "Fix embedding cache hit rate"
✅ "Improve error handling in RAG system"
❌ "Fix stuff"
❌ "Update"
```

---

## Performance & Quality

**Speed optimizations** (`utils/cache.py`, `config.py`):
- Embedding cache
- Query cache
- Smaller chunk size
- Faster LLM

**Quality improvements**:
- Larger chunk size
- Better embedding model
- Better LLM
- Increase top-k retrieval

---

## Testing Strategy

**Unit tests** (`utils/`)
- Logging
- Memory management
- Caching

**Integration tests** (`rag/`, `vision/`)
- RAG pipeline
- Image processing

**End-to-end tests** (`bot/`)
- Command handlers
- Message processing

---

**All files work together to create GenieBot! Start with `README.md` and `QUICKSTART.md`** 🚀
