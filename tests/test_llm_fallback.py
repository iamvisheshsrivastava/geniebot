"""Tests for rag.llm model fallback chains (issue #3).

Everything here is mocked - no live Ollama server or OpenRouter API call
is made. Covers OllamaLLM's retry-on-error heuristic
(_should_try_fallback) and the fallback-chain walking in both
OllamaLLM.generate and OpenRouterLLM.generate.
"""

import requests

from rag.llm import OllamaLLM, OpenRouterLLM


class _FakeResponse:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self):
        return self._json_data


# ---------------------------------------------------------------------------
# OllamaLLM._should_try_fallback - pure heuristic, no network involved.
# ---------------------------------------------------------------------------


def test_should_try_fallback_on_404():
    assert OllamaLLM._should_try_fallback(404, "") is True


def test_should_try_fallback_on_model_not_found_text():
    assert OllamaLLM._should_try_fallback(500, "Error: model 'foo' not found") is True


def test_should_try_fallback_on_out_of_memory():
    assert OllamaLLM._should_try_fallback(500, "requires more system memory than available") is True


def test_should_not_try_fallback_on_unrelated_error():
    assert OllamaLLM._should_try_fallback(400, "invalid request format") is False


# ---------------------------------------------------------------------------
# OllamaLLM.generate - fallback chain walking.
# ---------------------------------------------------------------------------


def _make_ollama(monkeypatch, model="primary", fallback_models=None):
    # Avoid a real network call from _verify_connection during __init__.
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(status_code=200))
    return OllamaLLM(model=model, fallback_models=fallback_models or ["backup"])


def test_ollama_generate_falls_back_on_404(monkeypatch):
    llm = _make_ollama(monkeypatch)

    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append(json["model"])
        if json["model"] == "primary":
            return _FakeResponse(status_code=404, text="model not found")
        return _FakeResponse(status_code=200, json_data={"response": "hi from backup"})

    monkeypatch.setattr(requests, "post", fake_post)

    result = llm.generate("hello")

    assert result == "hi from backup"
    assert calls == ["primary", "backup"]
    assert llm.model == "backup"  # active model switches to the working fallback


def test_ollama_generate_does_not_fall_back_on_non_triggering_error(monkeypatch):
    llm = _make_ollama(monkeypatch)

    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append(json["model"])
        return _FakeResponse(status_code=400, text="bad request")

    monkeypatch.setattr(requests, "post", fake_post)

    result = llm.generate("hello")

    assert calls == ["primary"]  # never tried the fallback model
    assert "400" in result


def test_ollama_generate_returns_last_error_when_all_models_fail(monkeypatch):
    llm = _make_ollama(monkeypatch)

    monkeypatch.setattr(
        requests, "post", lambda *a, **k: _FakeResponse(status_code=404, text="not found")
    )

    result = llm.generate("hello")
    assert result.startswith("Error:")


def test_ollama_generate_succeeds_on_first_model_without_fallback(monkeypatch):
    llm = _make_ollama(monkeypatch)

    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append(json["model"])
        return _FakeResponse(status_code=200, json_data={"response": "hi"})

    monkeypatch.setattr(requests, "post", fake_post)

    result = llm.generate("hello")
    assert result == "hi"
    assert calls == ["primary"]


# ---------------------------------------------------------------------------
# OpenRouterLLM.generate - fallback chain + null/empty-content guard.
# ---------------------------------------------------------------------------


def _or_response(content):
    return _FakeResponse(
        status_code=200,
        json_data={"choices": [{"message": {"content": content}}]},
    )


def test_openrouter_generate_falls_back_on_null_content(monkeypatch):
    llm = OpenRouterLLM(api_key="key", model="primary", fallback_models=["backup"])

    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append(json["model"])
        if json["model"] == "primary":
            return _or_response(None)  # reasoning model burned its budget
        return _or_response("real answer")

    monkeypatch.setattr(requests, "post", fake_post)

    result = llm.generate("hello")

    assert result == "real answer"
    assert calls == ["primary", "backup"]
    assert llm.model == "backup"


def test_openrouter_generate_falls_back_on_error_status(monkeypatch):
    llm = OpenRouterLLM(api_key="key", model="primary", fallback_models=["backup"])

    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append(json["model"])
        if json["model"] == "primary":
            return _FakeResponse(status_code=503, text="service unavailable")
        return _or_response("real answer")

    monkeypatch.setattr(requests, "post", fake_post)

    result = llm.generate("hello")
    assert result == "real answer"
    assert calls == ["primary", "backup"]


def test_openrouter_generate_returns_helpful_message_when_all_empty(monkeypatch):
    llm = OpenRouterLLM(api_key="key", model="primary", fallback_models=["backup"])

    monkeypatch.setattr(requests, "post", lambda *a, **k: _or_response(None))

    result = llm.generate("hello")
    assert "didn't return a response" in result


def test_openrouter_generate_no_fallback_configured_returns_last_error(monkeypatch):
    llm = OpenRouterLLM(api_key="key", model="only-model")

    monkeypatch.setattr(
        requests, "post", lambda *a, **k: _FakeResponse(status_code=500, text="boom")
    )

    result = llm.generate("hello")
    assert "500" in result
