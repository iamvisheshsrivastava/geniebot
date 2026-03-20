"""RAG system backed by persistent SQLite embeddings."""

import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

from utils.cache import EmbeddingCache
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RAGSystem:
    """Retrieval Augmented Generation system with SQLite persistence."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 300,
        chunk_overlap: int = 50,
        db_path: str = "data/rag_embeddings.db",
    ):
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.db_path = Path(db_path)

        logger.info(f"Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        self.embedding_cache = EmbeddingCache()

        self.chunks: List[str] = []
        self.chunk_sources: List[str] = []
        self.embeddings: np.ndarray = np.array([], dtype="float32")
        self.normalized_embeddings: np.ndarray = np.array([], dtype="float32")

        self._init_db()
        logger.info("RAG system initialized (SQLite persistent store)")

    def _init_db(self) -> None:
        """Create SQLite schema if it does not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    chunk_text TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    embedding_dim INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def _hash_documents(documents: List[Tuple[str, str]]) -> str:
        """Create a deterministic hash for document contents."""
        digest = hashlib.sha256()
        for name, text in sorted(documents, key=lambda x: x[0].lower()):
            digest.update(name.encode("utf-8"))
            digest.update(b"\n")
            digest.update(text.encode("utf-8"))
            digest.update(b"\n\n")
        return digest.hexdigest()

    def _index_signature(self, doc_hash: str) -> str:
        """Build signature that invalidates index on config/model changes."""
        raw = f"{doc_hash}|{self.model_name}|{self.chunk_size}|{self.chunk_overlap}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _load_raw_documents(self, doc_dir: str) -> List[Tuple[str, str]]:
        """Load .txt and .md documents from the provided directory."""
        logger.info(f"Loading documents from: {doc_dir}")
        doc_path = Path(doc_dir)
        if not doc_path.exists():
            logger.warning(f"Document directory not found: {doc_dir}")
            return []

        documents: List[Tuple[str, str]] = []
        for file_path in sorted(doc_path.glob("*")):
            if file_path.suffix.lower() not in {".txt", ".md"}:
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
                documents.append((file_path.name, content))
                logger.debug(f"Loaded: {file_path.name}")
            except Exception as exc:
                logger.error(f"Error loading {file_path.name}: {exc}")

        logger.info(f"Loaded {len(documents)} documents")
        return documents

    def _chunk_documents(self, documents: List[Tuple[str, str]]) -> Tuple[List[str], List[str]]:
        """Split documents into overlapping chunks."""
        logger.info("Chunking documents...")
        chunks: List[str] = []
        sources: List[str] = []

        step = max(1, self.chunk_size - self.chunk_overlap)
        for filename, content in documents:
            for i in range(0, len(content), step):
                chunk = content[i : i + self.chunk_size]
                if len(chunk.strip()) > 20:
                    chunks.append(chunk)
                    sources.append(filename)

        logger.info(f"Created {len(chunks)} chunks from documents")
        return chunks, sources

    def _generate_embeddings(self, chunks: List[str]) -> np.ndarray:
        """Generate embeddings for chunk texts with in-process cache."""
        logger.info("Generating embeddings...")
        vectors: List[np.ndarray] = []
        for i, chunk in enumerate(chunks):
            cached = self.embedding_cache.get(chunk)
            if cached is not None:
                vectors.append(cached)
            else:
                emb = self.embedding_model.encode(chunk, convert_to_numpy=True).astype("float32")
                vectors.append(emb)
                self.embedding_cache.put(chunk, emb)

            if (i + 1) % 10 == 0:
                logger.debug(f"Generated embeddings for {i + 1}/{len(chunks)} chunks")

        return np.array(vectors, dtype="float32") if vectors else np.array([], dtype="float32")

    def _set_in_memory_index(self, chunks: List[str], sources: List[str], embeddings: np.ndarray) -> None:
        """Load chunk/embedding data into process memory for retrieval."""
        self.chunks = chunks
        self.chunk_sources = sources
        self.embeddings = embeddings.astype("float32") if embeddings.size else np.array([], dtype="float32")

        if self.embeddings.size:
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
            norms = np.clip(norms, 1e-12, None)
            self.normalized_embeddings = self.embeddings / norms
        else:
            self.normalized_embeddings = np.array([], dtype="float32")

    def _persist_index(self, chunks: List[str], sources: List[str], embeddings: np.ndarray, signature: str) -> None:
        """Persist index rows and metadata in SQLite."""
        logger.info(f"Persisting {len(chunks)} chunks to SQLite: {self.db_path}")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM chunks")
            rows = []
            for chunk, source, emb in zip(chunks, sources, embeddings):
                rows.append((source, chunk, emb.astype("float32").tobytes(), int(emb.shape[0])))

            conn.executemany(
                "INSERT INTO chunks (source, chunk_text, embedding, embedding_dim) VALUES (?, ?, ?, ?)",
                rows,
            )
            conn.execute(
                "INSERT INTO metadata (key, value) VALUES ('index_signature', ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (signature,),
            )
            conn.commit()

    def _load_from_db(self) -> int:
        """Load chunks and embeddings from SQLite into memory."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT source, chunk_text, embedding, embedding_dim FROM chunks ORDER BY id"
            ).fetchall()

        chunks: List[str] = []
        sources: List[str] = []
        vectors: List[np.ndarray] = []

        for source, chunk_text, emb_blob, emb_dim in rows:
            chunks.append(chunk_text)
            sources.append(source)
            vec = np.frombuffer(emb_blob, dtype="float32", count=int(emb_dim)).copy()
            vectors.append(vec)

        embeddings = np.array(vectors, dtype="float32") if vectors else np.array([], dtype="float32")
        self._set_in_memory_index(chunks, sources, embeddings)
        return len(chunks)

    def load_documents(self, doc_dir: str) -> None:
        """Load documents, rebuild SQLite index when needed, and warm in-memory data."""
        documents = self._load_raw_documents(doc_dir)
        if not documents:
            self._set_in_memory_index([], [], np.array([], dtype="float32"))
            return

        doc_hash = self._hash_documents(documents)
        signature = self._index_signature(doc_hash)

        with sqlite3.connect(self.db_path) as conn:
            current_sig_row = conn.execute(
                "SELECT value FROM metadata WHERE key='index_signature'"
            ).fetchone()
            current_signature = current_sig_row[0] if current_sig_row else ""

        if current_signature == signature:
            loaded = self._load_from_db()
            logger.info(f"Loaded {loaded} chunks from persistent SQLite index")
            return

        chunks, sources = self._chunk_documents(documents)
        embeddings = self._generate_embeddings(chunks)
        self._persist_index(chunks, sources, embeddings, signature)
        self._set_in_memory_index(chunks, sources, embeddings)
        logger.info("SQLite index rebuilt and loaded into memory")

    def retrieve_chunks(self, query: str, top_k: int = 3) -> List[Tuple[str, str]]:
        """Retrieve top-k chunks using cosine similarity over persisted embeddings."""
        if len(self.chunks) == 0 or self.normalized_embeddings.size == 0:
            logger.warning("No documents loaded. Cannot retrieve chunks.")
            return []

        logger.debug(f"Retrieving chunks for query: {query[:50]}...")
        query_vec = self.embedding_model.encode(query, convert_to_numpy=True).astype("float32")
        query_norm = max(float(np.linalg.norm(query_vec)), 1e-12)
        query_vec = query_vec / query_norm

        scores = self.normalized_embeddings @ query_vec
        k = min(top_k, len(self.chunks))
        top_indices = np.argsort(scores)[-k:][::-1]

        results: List[Tuple[str, str]] = []
        for idx in top_indices:
            results.append((self.chunks[int(idx)], self.chunk_sources[int(idx)]))

        logger.debug(f"Retrieved {len(results)} chunks")
        return results

    def get_rag_context(self, query: str, top_k: int = 3) -> str:
        """Build context string from retrieved chunks for LLM prompting."""
        chunks = self.retrieve_chunks(query, top_k)
        if not chunks:
            logger.warning("No relevant chunks found")
            return "No relevant documents found in the knowledge base."

        context = "Relevant context from documents:\n\n"
        for i, (chunk, source) in enumerate(chunks, 1):
            context += f"[Source {i}: {source}]\n{chunk}\n\n"
        return context

    def get_source_chunks(self, query: str, top_k: int = 3) -> Dict[str, List[str]]:
        """Return source mapping for the retrieved chunks."""
        chunks = self.retrieve_chunks(query, top_k)
        sources: Dict[str, List[str]] = {}
        for chunk, source in chunks:
            sources.setdefault(source, []).append(chunk[:100] + "...")
        return sources

    def has_documents(self) -> bool:
        """Check if chunks are loaded in memory."""
        return len(self.chunks) > 0

    def get_stats(self) -> Dict:
        """Get RAG system statistics."""
        return {
            "total_chunks": len(self.chunks),
            "embedding_model": self.model_name,
            "chunk_size": self.chunk_size,
            "vector_store": "sqlite",
            "vector_store_rows": len(self.chunks),
            "db_path": str(self.db_path),
            "cache_stats": self.embedding_cache.stats(),
        }
