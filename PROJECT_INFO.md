# GenieBot

## Description
A production-ready Telegram bot combining Retrieval-Augmented Generation (RAG) with Vision AI capabilities.

## Features
- **RAG System**: Document Q&A with semantic search using FAISS and Sentence Transformers
- **Vision AI**: Image captioning with tag extraction using Salesforce BLIP
- **Memory**: Maintains last 3 conversations per user
- **Caching**: Smart embedding and query caching for fast responses
- **Local LLM**: Uses Ollama for private, fast inference
- **Production Ready**: Comprehensive logging, error handling, and modular architecture

## Quick Start

### Requirements
- Python 3.9+
- 8GB RAM (16GB+ recommended)
- Ollama installed locally

### Installation

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Pull Ollama model (in another terminal)
ollama pull mistral

# 4. Configure
cp .env.example .env
# Edit .env and add TELEGRAM_BOT_TOKEN

# 5. Run
python app.py
```

## Usage

- `/start` - Welcome message
- `/ask <query>` - Ask questions about documents
- `/image` - Upload image for captioning
- `/history` - View last 3 interactions
- `/status` - Check system status
- `/help` - Detailed help

## Documentation

See [README.md](README.md) for complete documentation.

## Architecture

```
Documents → Chunking → Embeddings → FAISS Index
                                        ↓
                                    Query Search
                                        ↓
                                    Context Building
                                        ↓
                                    LLM (Ollama)
                                        ↓
                                    Answer + Sources
```

## Technologies

- **Bot Framework**: python-telegram-bot
- **Embeddings**: Sentence Transformers
- **Vector DB**: FAISS
- **Vision**: Hugging Face BLIP
- **LLM**: Ollama (local)
- **ML Framework**: PyTorch

## Directory Structure

```
geniebot/
├── app.py              # Main entry point
├── requirements.txt
├── README.md
├── .env.example
├── bot/                # Telegram handlers
├── rag/                # RAG system
├── vision/             # Image processing
├── utils/              # Caching, memory, logging
├── data/               # Sample documents
└── logs/               # Log files
```

## License

Open source. See individual component licenses.

## Support

Check README.md for troubleshooting guide.
