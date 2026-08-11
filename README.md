# GenieBot - RAG + Vision Telegram Assistant  

GenieBot is a Telegram assistant that supports:
- document-grounded Q&A with RAG
- image captioning with tags
- quick summary of the latest chat or image interaction

It uses OpenRouter free-tier models for generation and vision, fastembed for embeddings, and SQLite for persistent vector storage. No local model server or GPU required — it runs comfortably on a free-tier host.

## Quick Access

- Telegram bot: [@mygenie_ai_bot](https://t.me/mygenie_ai_bot)
- Service check: `<your-render-url>/health` to confirm whether the bot service is running
- The previous DigitalOcean droplet deployment has been retired; see **Deploy (free tier)** below for the current hosting setup

## Highlights

- RAG retrieval with persistent embeddings in SQLite
- Query and embedding caches in RAM for fast repeated calls
- Vision pipeline for image caption + tags (via a hosted vision model, no local weights)
- User memory that keeps the last 3 interactions per user
- Health/status page at `/` and `/health`

## Tech Stack

- Python 3.10+
- python-telegram-bot
- OpenRouter (hosted LLM + vision, free-tier models) — or Ollama for local dev
- fastembed / sentence-transformers/all-MiniLM-L6-v2 (embeddings, ONNX-based, no torch)
- SQLite (`data/rag_embeddings.db`)

## Current Runtime Settings

- retrieval top_k: 2
- chunk_size: 200
- max_tokens: 250
- user history: last 3 interactions per user

## Project Structure

```text
app.py                    # Bot bootstrap + status server
bot/handlers.py           # Telegram command handlers
rag/system.py             # Chunking, embedding, retrieval, SQLite persistence
rag/qa.py                 # QA orchestration and prompt flow
rag/llm.py                # OpenRouter + Ollama clients with model fallback handling
rag/embeddings.py         # fastembed wrapper (no torch dependency)
vision/processor.py       # Image captioning via a hosted OpenRouter vision model
utils/cache.py            # QueryCache + EmbeddingCache (RAM)
utils/memory.py           # Per-user short history (RAM)
utils/logger.py           # File + console logging
data/                     # Knowledge documents + SQLite DB file
media/                    # Assignment screenshots used below
docs/diagrams/system-design.mmd
```

## Setup and Run (local)

### 1) Create and activate virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment

Create `.env` from `.env.example`. By default `LLM_PROVIDER=openrouter`, which needs no local model server:

```env
TELEGRAM_BOT_TOKEN=your_token_here
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=nvidia/nemotron-nano-9b-v2:free
OPENROUTER_VISION_MODEL=google/gemma-4-31b-it:free
LOG_LEVEL=INFO
PORT=8080
```

To use a local Ollama server instead, set `LLM_PROVIDER=ollama` and configure `OLLAMA_BASE_URL` / `OLLAMA_MODEL` (see `.env.example`); note the vision pipeline always calls OpenRouter regardless of `LLM_PROVIDER`.

### 4) Optional: prebuild the embedding DB

```bash
python scripts/build_vector_db.py --data-dir data --db-path data/rag_embeddings.db --chunk-size 200 --chunk-overlap 50
```

### 5) Run the bot

```bash
python app.py
```

## Deploy (free tier)

This repo includes a `Dockerfile` and `render.yaml` for a one-click Render deployment:

1. On [Render](https://render.com), choose **New > Blueprint** and point it at this repo (`render.yaml` will be picked up automatically).
2. Set the required secrets in the Render dashboard: `TELEGRAM_BOT_TOKEN` and `OPENROUTER_API_KEY`.
3. Deploy. Render auto-redeploys on every push to `main` (`autoDeployTrigger: commit`).
4. Confirm it's running via `<your-render-url>/health`.

The bot itself doesn't need inbound HTTP (it long-polls Telegram), the status server just satisfies Render's free-tier requirement that the service bind to `$PORT`.

## Bot Commands

- `/start` - quick intro and commands
- `/help` - usage guidance
- `/ask <question>` - document-grounded answer
- `/image` - upload image for caption + tags
- `/summarize [chat|image]` - summarize latest interaction

## Demo Screenshots

### Start
![Start](media/start.png)

### Ask
![Ask](media/ask.png)

These are example `/ask` queries that fetch information from your loaded documents and then answer:
- `/ask What is the return policy?`
- `/ask What are the pricing plans and included features?`
- `/ask What are the support hours and escalation process?`
- `/ask How do I reset my account password?`
- `/ask What are the main security/compliance points?`

### Image
![Image](media/image.png)

### Summarize
![Summarize](media/summarize.png)

## Architecture Diagram

Source: `docs/diagrams/system-design.mmd`

```mermaid
flowchart TD
    U[Telegram User] --> TG[Telegram API]
    TG --> APP["app.py - Bot Runtime"]
    WEB[Browser / Render Ping] --> STATUS["Status endpoints: / and /health"]
    STATUS --> APP

    APP --> H["bot/handlers.py - Command Handlers"]
    H --> MEM["utils/memory.py - Last 3 interactions per user"]
    H --> QA["rag/qa.py - RAG QA Orchestrator"]
    H --> VISION["vision/processor.py - Vision Caption + Tags"]

    QA --> RAG["rag/system.py - RAG Retrieval"]
    QA --> LLM["rag/llm.py - OpenRouter/Ollama LLM + Fallback"]
    QA --> QCACHE["utils/cache.py - QueryCache (RAM only)"]

    RAG --> DOCS["Knowledge Documents (md txt files)"]
    RAG --> ECACHE["utils/cache.py - EmbeddingCache (RAM only)"]
    RAG --> ST["rag/embeddings.py - fastembed all-MiniLM-L6-v2"]
    RAG --> SQLITE["SQLite DB - data/rag_embeddings.db"]

    BLD["scripts/build_vector_db.py - One-time or manual DB build"] --> SQLITE
    VISION --> ORV["OpenRouter Vision Model (hosted, free tier)"]
    LLM --> OR["OpenRouter Chat Model (hosted, free tier)"]

    APP --> LOGS["logs/geniebot YYYYMMDD.log"]
    APP --> ENV[".env configuration"]
```

## Storage and Caching

- Persistent: document chunk embeddings in SQLite (`data/rag_embeddings.db`)
- RAM only: QueryCache, EmbeddingCache, user interaction history
- Logs: `logs/geniebot_YYYYMMDD.log` (daily file name, no auto-rotation cleanup)

## Assignment Notes

- RAG is optimized for concise answers with grounded context.
- Repeated same questions are served from in-memory query cache when available.
