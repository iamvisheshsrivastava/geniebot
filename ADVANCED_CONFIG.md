"""
Advanced Configuration Guide for GenieBot

This file documents all configurable parameters and how to customize them.
"""

# =============================================================================
# RAG SYSTEM CUSTOMIZATION
# =============================================================================

"""
Embedding Models (Sentence Transformers)
- Desktop/Laptop options:
    - "sentence-transformers/all-MiniLM-L6-v2" [RECOMMENDED]
      Size: 90 MB
      Dims: 384
      Speed: Fast
      Quality: Good
    
    - "sentence-transformers/all-mpnet-base-v2"
      Size: 430 MB
      Dims: 768
      Speed: Medium
      Quality: Excellent
    
    - "sentence-transformers/paraphrase-MiniLM-L6-v2"
      Size: 90 MB
      Dims: 384
      Speed: Fast
      Quality: Good for paraphrases

Change in config.py:
    RAG_CONFIG["embedding_model"] = "sentence-transformers/all-mpnet-base-v2"

Or directly in app.py:
    rag_system = RAGSystem(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
"""

# Chunk Size Configuration
"""
chunk_size: 300 (default)
- Smaller (200): Less context, faster processing, more chunks
- Optimal (300-400): Balanced for most use cases
- Larger (500+): More context, slower, fewer chunks

Example:
    rag_system = RAGSystem(
        chunk_size=400  # Increase for longer documents
    )
"""

# =============================================================================
# LLM MODEL SELECTION (Ollama)
# =============================================================================

"""
Available Models (ordered by speed):

FASTEST (< 1 sec response):
- neural-chat
- tinyllama
- orca-mini

FAST (1-3 sec):
- mistral [RECOMMENDED for balance]
- dolphin-mixtral
- neural-chat-7b

BALANCED (2-5 sec):
- llama2 [RECOMMENDED for quality]
- openchat
- yi

HIGH QUALITY (5-15 sec):
- llama2-uncensored
- dolphin-2.2-mistral-7b
- hermes

ENTERPRISE (15+ sec):
- mixtral
- llama2-13b
- yi-34b

Setup:
    # List available
    ollama list
    
    # Download new model
    ollama pull mistral
    
    # Edit .env or config.py
    OLLAMA_MODEL=mistral
"""

# =============================================================================
# VISION MODEL CONFIGURATION
# =============================================================================

"""
Image Captioning Models (Hugging Face):

CURRENT (Default):
- "Salesforce/blip-image-captioning-base"
  Size: ~350 MB
  Speed: 1-3 seconds
  Quality: Good

ALTERNATIVES:
- "Salesforce/blip-image-captioning-large"
  Size: 900 MB
  Speed: 2-5 seconds
  Quality: Better

- "microsoft/git-base"
  Size: 400 MB
  Speed: 1-2 seconds
  Quality: Good

Change in config.py or app.py:
    vision_processor = ImageProcessor(
        model_name="Salesforce/blip-image-captioning-large"
    )
"""

# =============================================================================
# MEMORY & CACHING TUNING
# =============================================================================

"""
User Memory: Stores last N interactions per user

Current: 3 interactions max
Options:
    - 1: Minimal memory, less context
    - 3: Good balance [RECOMMENDED]
    - 5: More context, uses more memory
    - 10: Full conversation history

Change:
    user_memory = UserMemory(max_history=5)

Caching Strategy:

1. Embedding Cache: Reuse embeddings for same text
   max_size: 1000 (default)
   - Larger: More cache hits, uses more RAM
   - Smaller: Faster, less memory

2. Query Cache: Cache full responses
   max_size: 500 (default)
   - Useful for repeated questions
   - Clears on /clear_cache command

Enable/Disable:
    qa_system = RAGQA(rag_system, llm, use_cache=True)
"""

# =============================================================================
# PERFORMANCE OPTIMIZATION PROFILES
# =============================================================================

"""
PROFILE 1: Maximum Speed (Limited Hardware)
========================================
RAM: 4GB
Use case: Fast responses, less accuracy

app.py settings:
    # RAG
    rag_system = RAGSystem(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        chunk_size=200,
        chunk_overlap=30
    )
    
    # Memory
    user_memory = UserMemory(max_history=1)
    
    # Cache
    CACHE_CONFIG["embedding_cache_size"] = 500
    CACHE_CONFIG["query_cache_size"] = 300
    
    # LLM
    ollama pull neural-chat
    OLLAMA_MODEL = "neural-chat"


PROFILE 2: Balanced (Standard Hardware)
========================================
RAM: 8GB
Use case: Good balance of speed and quality [RECOMMENDED]

app.py settings:
    # RAG
    rag_system = RAGSystem(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        chunk_size=300,
        chunk_overlap=50
    )
    
    # Memory
    user_memory = UserMemory(max_history=3)
    
    # LLM
    ollama pull mistral
    OLLAMA_MODEL = "mistral"


PROFILE 3: Maximum Quality (High-end Hardware)
================================================
RAM: 16GB+, GPU available
Use case: Best quality responses

app.py settings:
    # RAG
    rag_system = RAGSystem(
        model_name="sentence-transformers/all-mpnet-base-v2",
        chunk_size=400,
        chunk_overlap=75
    )
    
    # Memory
    user_memory = UserMemory(max_history=5)
    
    # Cache
    CACHE_CONFIG["embedding_cache_size"] = 2000
    CACHE_CONFIG["query_cache_size"] = 1000
    
    # LLM
    ollama pull llama2
    OLLAMA_MODEL = "llama2"
    
    # GPU
    export OLLAMA_NUM_GPU=1  # Use GPU
"""

# =============================================================================
# ADVANCED CONFIGURATIONS
# =============================================================================

"""
Increase RAG Quality:
    # More chunks for better context
    top_k_retrieval=5  # Instead of 3
    
    # Larger chunks with more overlap
    chunk_size=500
    chunk_overlap=100
    
    # Better embedding model
    embedding_model="sentence-transformers/all-mpnet-base-v2"

Enable GPU Acceleration:
    # PyTorch
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    
    # Ollama
    export OLLAMA_NUM_GPU=1
    
    # Test
    ollama run mistral "What is AI?"

Add Document Source Filtering:
    # In bot/handlers.py, modify ask_command to limit sources:
    result = qa_system.answer_question(question)
    sources = result.get("sources", {})
    
    # Filter only specific sources
    filtered_sources = {k: v for k, v in sources.items() 
                       if k in ["faq.md", "policies.md"]}

Custom Prompt Engineering:
    # In rag/qa.py, modify system_prompt:
    system_prompt = (
        "You are a helpful customer service agent. "
        "Provide concise answers. "
        "Always cite sources. "
        "Ask clarifying questions if needed."
    )

Monitor Resource Usage:
    # Add in app.py after initialization:
    import psutil
    proc = psutil.Process()
    print(f"Memory: {proc.memory_info().rss / 1024 / 1024:.2f} MB")
"""

# =============================================================================
# DEPLOYMENT CONFIGURATIONS
# =============================================================================

"""
Production Settings:
    LOG_LEVEL = "INFO"  # Not DEBUG
    CACHE_CONFIG["enable_caching"] = True
    
    # Increase timeouts for slower servers
    LLM_CONFIG["timeout"] = 180
    
    # Monitor errors
    error_handler: Send to logging service

Scaling for Multiple Users:
    # Increase cache
    CACHE_CONFIG["embedding_cache_size"] = 5000
    CACHE_CONFIG["query_cache_size"] = 2000
    
    # Database backend (future)
    # user_memory = DatabaseMemory()
    
    # Async processing (future)
    # await qa_system.answer_question_async(question)
"""

# =============================================================================
# TROUBLESHOOTING CONFIGURATIONS
# =============================================================================

"""
Issue: Out of memory
    Solution:
        chunk_size=200
        embedding_cache_size=500
        query_cache_size=200
        max_history_per_user=1

Issue: Slow responses
    Solution:
        Use smaller embedding model
        Use faster LLM (neural-chat)
        Reduce chunk_size
        Enable GPU

Issue: Inaccurate answers
    Solution:
        Increase chunk_size=500
        Use better embedding model
        Use better LLM (llama2)
        Increase top_k_retrieval=5

Issue: High latency on first query
    Solution:
        Normal - models load on first use
        Can pre-load models with:
            rag_system = RAGSystem()
            vision_processor = ImageProcessor()
            # Models are now ready
"""
