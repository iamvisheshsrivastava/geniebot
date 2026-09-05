"""Tests for utils.cache.EmbeddingCache and QueryCache."""

import numpy as np

from utils.cache import EmbeddingCache, QueryCache


def test_embedding_cache_miss_then_hit():
    cache = EmbeddingCache(max_size=10)
    assert cache.get("hello") is None

    vec = np.array([0.1, 0.2, 0.3], dtype="float32")
    cache.put("hello", vec)

    cached = cache.get("hello")
    assert cached is not None
    assert np.array_equal(cached, vec)


def test_embedding_cache_is_case_insensitive():
    cache = EmbeddingCache()
    vec = np.array([1.0], dtype="float32")
    cache.put("Hello World", vec)

    assert cache.get("hello world") is not None
    assert np.array_equal(cache.get("HELLO WORLD"), vec)


def test_embedding_cache_evicts_least_accessed_when_full():
    cache = EmbeddingCache(max_size=2)
    cache.put("a", np.array([1.0], dtype="float32"))
    cache.put("b", np.array([2.0], dtype="float32"))

    # Access "a" so it's no longer the least-accessed entry.
    cache.get("a")

    cache.put("c", np.array([3.0], dtype="float32"))

    assert cache.get("a") is not None
    assert cache.get("c") is not None
    # "b" was never accessed, so it should have been the one evicted.
    assert len(cache.cache) == 2


def test_embedding_cache_clear():
    cache = EmbeddingCache()
    cache.put("a", np.array([1.0], dtype="float32"))
    cache.clear()

    assert cache.get("a") is None
    assert cache.stats()["total_cached"] == 0


def test_query_cache_miss_then_hit():
    cache = QueryCache()
    assert cache.get("what is x") is None

    cache.put("what is x", "x is y")
    assert cache.get("what is x") == "x is y"


def test_query_cache_is_case_insensitive():
    cache = QueryCache()
    cache.put("What Is X?", "x is y")
    assert cache.get("what is x?") == "x is y"


def test_query_cache_evicts_fifo_when_full():
    cache = QueryCache(max_size=2)
    cache.put("q1", "a1")
    cache.put("q2", "a2")
    cache.put("q3", "a3")  # should evict q1 (oldest), not q2

    assert cache.get("q1") is None
    assert cache.get("q2") == "a2"
    assert cache.get("q3") == "a3"
    assert cache.size() == 2


def test_query_cache_clear():
    cache = QueryCache()
    cache.put("q", "a")
    cache.clear()

    assert cache.get("q") is None
    assert cache.size() == 0
