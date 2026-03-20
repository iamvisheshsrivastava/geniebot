# Contributing & Development Guide

## Getting Started with Development

### Setup Development Environment

```bash
# Clone repository
git clone <repo-url>
cd geniebot

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dev dependencies
pip install -r requirements_dev.txt
```

### Code Style

We use **Black** for formatting and **Flake8** for linting.

```bash
# Format code
black *.py bot/ rag/ vision/ utils/

# Lint code
flake8 *.py bot/ rag/ vision/ utils/

# Sort imports
isort *.py bot/ rag/ vision/ utils/

# Type check
mypy app.py
```

### Pre-commit Hook

```bash
# Create .git/hooks/pre-commit
#!/bin/bash
black --check .
flake8 .
isort --check-only .
```

---

## Adding New Features

### 1. Add a New Command

**File**: `bot/handlers.py`

```python
async def my_new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    My new command description
    """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} used /my_new_command")
    
    await update.message.reply_text("Response message")
```

**Register in**: `app.py`

```python
application.add_handler(CommandHandler("my_new_command", my_new_command))
```

### 2. Extend RAG System

**File**: `rag/system.py`

```python
def new_retrieval_method(self, query: str):
    """Add new retrieval strategy"""
    # Your implementation
    pass
```

### 3. Add Vision Model

**File**: `vision/processor.py`

```python
def object_detection(self, image_input):
    """Detect objects in image"""
    # Your implementation
    pass
```

### 4. Create New Util

**File**: `utils/my_util.py`

```python
"""My utility module"""

from .logger import setup_logger

logger = setup_logger(__name__)

class MyUtil:
    pass
```

**Register in**: `utils/__init__.py`

```python
from .my_util import MyUtil

__all__ = [..., 'MyUtil']
```

---

## Testing

### Run Tests

```bash
pytest
pytest -v  # verbose
pytest --cov  # with coverage
```

### Write Tests

**File**: `tests/test_rag.py`

```python
import pytest
from rag import RAGSystem

def test_rag_initialization():
    rag = RAGSystem()
    assert rag.embedding_model is not None

@pytest.mark.asyncio
async def test_async_handler():
    # Test async function
    pass
```

---

## Architecture Deep Dive

### Module Interactions

```
app.py (Entry point)
  ├── RAGSystem + OllamaLLM → RAGQA
  ├── ImageProcessor
  ├── UserMemory
  └── Telegram handlers

bot/handlers.py
  ├── Uses qa_system from context
  ├── Uses vision_processor
  └── Stores in user_memory

rag/system.py
  ├── Loads documents
  ├── Creates embeddings
  └── Builds FAISS index

rag/llm.py
  └── Communicates with Ollama

vision/processor.py
  └── BLIP model inference

utils/
  ├── logger.py - Structured logging
  ├── memory.py - Conversation history
  └── cache.py - Embedding/Query caching
```

### Data Flow

```
User Message (Telegram)
    ↓
handlers.py (Parse command)
    ↓
RAG/Vision System (Process)
    ↓
Cache Layer (Check/Store)
    ↓
LLM/Model (Generate)
    ↓
Memory Layer (Store interaction)
    ↓
Response (Back to user)
```

---

## Performance Profiling

```python
# Profile RAG query
import time

start = time.time()
result = qa_system.answer_question("query")
elapsed = time.time() - start
print(f"Query took {elapsed:.2f}s")

# Profile memory usage
import psutil
proc = psutil.Process()
print(f"Memory: {proc.memory_info().rss / 1024 / 1024:.2f} MB")

# Profile model loading
import cProfile
cProfile.run('rag_system.load_documents("data")')
```

---

## Database Integration (Future)

```python
# Instead of in-memory memory
from storage import DatabaseMemory

user_memory = DatabaseMemory(connection_string="postgresql://...")

# Instead of in-memory cache
from storage import DatabaseCache

cache = DatabaseCache(redis_url="redis://localhost:6379")
```

---

## API Server Integration (Future)

```python
# Add FastAPI
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app_api = FastAPI()

@app_api.post("/ask")
async def ask_api(query: str):
    result = qa_system.answer_question(query)
    return JSONResponse(result)

@app_api.post("/image")
async def image_api(image: UploadFile):
    image_data = await image.read()
    result = vision_processor.process_image(image_data)
    return JSONResponse(result)
```

---

## Common Development Tasks

### Add Logging

```python
from utils.logger import setup_logger

logger = setup_logger(__name__)

logger.info("Information")
logger.debug("Debug details")
logger.error("Error occurred")
```

### Add Caching

```python
from utils.cache import QueryCache

cache = QueryCache()

# Check cache
cached = cache.get(query)

# Store in cache
cache.put(query, response)
```

### Add Error Handling

```python
try:
    result = operation()
except SpecificException as e:
    logger.error(f"Error: {e}")
    return {"error": str(e)}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"error": "Internal error"}
```

---

## Release Checklist

- [ ] Run all tests: `pytest`
- [ ] Check code style: `black`, `flake8`
- [ ] Update version in `README.md`
- [ ] Update `CHANGELOG.md`
- [ ] Update dependencies in `requirements.txt`
- [ ] Test on different Python versions
- [ ] Test with different models
- [ ] Create release branch
- [ ] Tag release: `git tag v1.0.0`

---

## Debugging Tips

### Enable Debug Logging

```python
# In app.py
LOG_LEVEL = "DEBUG"
```

### Use debugger

```python
import pdb

# In code
pdb.set_trace()

# Or with breakpoint() (Python 3.7+)
breakpoint()
```

### Profile Code

```bash
python -m cProfile app.py > profile.txt
```

### Monitor Ollama

```bash
# Check Ollama logs
ollama ps  # Show running models
ollama list  # List available models
```

---

## Continuous Integration (Future)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements_dev.txt
      - name: Run tests
        run: pytest
      - name: Check style
        run: black --check .
```

---

## Helpful Resources

- [python-telegram-bot docs](https://python-telegram-bot.readthedocs.io/)
- [Sentence Transformers](https://www.sbert.net/)
- [FAISS documentation](https://faiss.ai/)
- [Ollama repository](https://github.com/jmorganca/ollama)
- [Hugging Face Hub](https://huggingface.co/)
- [FastAPI docs](https://fastapi.tiangolo.com/)

---

## Questions or Issues?

Create an issue or start a discussion in the repository.
