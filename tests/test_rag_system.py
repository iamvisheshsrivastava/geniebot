"""Tests for rag.system.RAGSystem: chunking, index signatures, and
cosine-similarity retrieval (issue #3).

These construct a real RAGSystem against a temp SQLite path, but never
trigger the actual fastembed model download - FastEmbedModel only loads
its ONNX model lazily on the first .encode() call, and the retrieval
tests avoid that by pre-seeding the embedding cache instead of calling
the real embedding model.
"""

import numpy as np
import pytest

from rag.system import RAGSystem


@pytest.fixture
def rag(tmp_path):
    return RAGSystem(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        chunk_size=30,
        chunk_overlap=10,
        db_path=str(tmp_path / "rag_test.db"),
    )


def test_chunk_documents_splits_with_overlap(rag):
    documents = [("doc.txt", "a" * 50)]
    chunks, sources = rag._chunk_documents(documents)

    step = rag.chunk_size - rag.chunk_overlap
    assert step == 20
    # First few chunks should be exactly chunk_size long and start `step`
    # characters apart (the overlap region repeats between consecutive
    # chunks).
    assert chunks[0] == "a" * 30
    assert chunks[1] == "a" * 30
    assert sources == ["doc.txt"] * len(chunks)


def test_chunk_documents_skips_short_trailing_chunks(rag):
    # A doc just barely longer than one chunk leaves a short tail chunk
    # that should be dropped (len(chunk.strip()) > 20 filter).
    documents = [("doc.txt", "a" * 32)]
    chunks, _ = rag._chunk_documents(documents)

    assert all(len(c.strip()) > 20 for c in chunks)


def test_chunk_documents_multiple_sources_tracked_independently(rag):
    documents = [("a.txt", "x" * 40), ("b.txt", "y" * 40)]
    chunks, sources = rag._chunk_documents(documents)

    assert set(sources) == {"a.txt", "b.txt"}
    assert len(chunks) == len(sources)


def test_hash_documents_is_order_independent(rag):
    docs_a = [("a.txt", "hello"), ("b.txt", "world")]
    docs_b = [("b.txt", "world"), ("a.txt", "hello")]

    assert rag._hash_documents(docs_a) == rag._hash_documents(docs_b)


def test_hash_documents_changes_with_content(rag):
    docs_a = [("a.txt", "hello")]
    docs_b = [("a.txt", "hello!")]

    assert rag._hash_documents(docs_a) != rag._hash_documents(docs_b)


def test_index_signature_changes_with_chunk_config(rag):
    doc_hash = rag._hash_documents([("a.txt", "hello")])
    sig_before = rag._index_signature(doc_hash)

    rag.chunk_size = rag.chunk_size + 1
    sig_after = rag._index_signature(doc_hash)

    assert sig_before != sig_after


def test_load_documents_missing_dir_leaves_no_documents(rag, tmp_path):
    rag.load_documents(str(tmp_path / "does-not-exist"))

    assert rag.has_documents() is False
    assert rag.get_stats()["total_chunks"] == 0


def test_retrieve_chunks_with_no_documents_returns_empty(rag):
    assert rag.retrieve_chunks("anything") == []


def test_retrieve_chunks_ranks_by_cosine_similarity(rag):
    # Three orthogonal-ish chunk embeddings; the query vector points
    # squarely at the second one, so it should be ranked first.
    chunks = ["about cats", "about dogs", "about birds"]
    sources = ["cats.txt", "dogs.txt", "birds.txt"]
    embeddings = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype="float32",
    )
    rag._set_in_memory_index(chunks, sources, embeddings)

    # Pre-seed the embedding cache for the query so retrieve_chunks takes
    # the cache-hit branch and never calls the real (unmocked) model.
    query = "tell me about dogs"
    rag.embedding_cache.put(query, np.array([0.0, 5.0, 0.0], dtype="float32"))

    results = rag.retrieve_chunks(query, top_k=2)

    assert len(results) == 2
    assert results[0] == ("about dogs", "dogs.txt")


def test_retrieve_chunks_respects_top_k(rag):
    chunks = ["one", "two", "three"]
    sources = ["a", "b", "c"]
    embeddings = np.eye(3, dtype="float32")
    rag._set_in_memory_index(chunks, sources, embeddings)

    query = "q"
    rag.embedding_cache.put(query, np.array([1.0, 0.0, 0.0], dtype="float32"))

    results = rag.retrieve_chunks(query, top_k=1)
    assert len(results) == 1


def test_load_documents_persists_and_reloads_from_sqlite(rag, tmp_path):
    doc_dir = tmp_path / "docs"
    doc_dir.mkdir()
    (doc_dir / "notes.txt").write_text("hello world " * 10, encoding="utf-8")

    def fake_encode(text, convert_to_numpy=True, **kwargs):
        # Deterministic stand-in embedding so we don't need the real model.
        if isinstance(text, str):
            return np.array([float(len(text)), 1.0, 0.0], dtype="float32")
        return np.array([[float(len(t)), 1.0, 0.0] for t in text], dtype="float32")

    rag.embedding_model.encode = fake_encode

    rag.load_documents(str(doc_dir))
    assert rag.has_documents() is True
    first_chunk_count = rag.get_stats()["total_chunks"]

    # Reloading unchanged documents should hit the persisted-signature path
    # (load from SQLite) rather than re-chunking/re-embedding.
    rag2 = RAGSystem(
        model_name=rag.model_name,
        chunk_size=rag.chunk_size,
        chunk_overlap=rag.chunk_overlap,
        db_path=str(rag.db_path),
    )
    rag2.load_documents(str(doc_dir))
    assert rag2.get_stats()["total_chunks"] == first_chunk_count
