"""Lightweight embedding backend (ONNX-based, no PyTorch dependency).

Drop-in replacement for sentence_transformers.SentenceTransformer that only
implements the .encode() call GenieBot actually uses. Uses fastembed, which
produces the same 384-dim all-MiniLM-L6-v2 vectors as sentence-transformers
so any previously stored embeddings remain compatible.
"""

import os

import numpy as np


class FastEmbedModel:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._model = None

    def _load(self):
        if self._model is None:
            from fastembed import TextEmbedding  # ~100 MB vs 1GB+ for torch

            # Pin thread count - onnxruntime otherwise sizes itself off the
            # host's full core count rather than the tiny CPU share a
            # free-tier instance actually gets, causing severe contention.
            threads = int(os.getenv("EMBEDDING_THREADS", "2"))
            self._model = TextEmbedding(model_name=self._model_name, threads=threads)
        return self._model

    def encode(self, text, convert_to_numpy: bool = True, **kwargs) -> np.ndarray:
        model = self._load()
        if isinstance(text, str):
            return np.array(list(model.embed([text]))[0], dtype="float32")
        return np.array(list(model.embed(list(text))), dtype="float32")
