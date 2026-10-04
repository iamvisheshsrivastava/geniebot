"""Tests for RAGQA.answer_question's conversation_context param (issue #12).

UserMemory.get_context() already formats a user's recent interactions into
an LLM-ready string; these tests cover the RAGQA side of wiring it into the
prompt sent to the LLM, separate from retrieved document chunks, and make
sure it doesn't get tangled up with the query cache.
"""

from unittest.mock import MagicMock

from rag.qa import RAGQA


def _make_qa(generate_return="The answer."):
    rag_system = MagicMock()
    rag_system.has_documents.return_value = True
    rag_system.retrieve_chunks.return_value = [("some chunk text", "doc.txt")]

    llm = MagicMock()
    llm.generate.return_value = generate_return

    qa = RAGQA(rag_system, llm, use_cache=True)
    return qa, llm


def test_conversation_context_is_included_in_prompt_sent_to_llm():
    qa, llm = _make_qa()

    qa.answer_question(
        "What about the enterprise plan?",
        conversation_context="Previous interactions:\n- Q: pricing?\n  A: Starts at $10...\n",
    )

    prompt_sent = llm.generate.call_args[0][0]
    assert "Previous interactions:" in prompt_sent
    assert "pricing?" in prompt_sent


def test_no_conversation_context_omits_the_section():
    qa, llm = _make_qa()

    qa.answer_question("What is the return policy?")

    prompt_sent = llm.generate.call_args[0][0]
    assert "Previous interactions:" not in prompt_sent


def test_cache_is_skipped_when_conversation_context_present():
    qa, llm = _make_qa()

    qa.answer_question("same question", conversation_context="some prior context")
    # A second call with the same question but no context should NOT hit a
    # cache entry written by the context-bearing call above.
    llm.generate.return_value = "a different answer without context"
    result = qa.answer_question("same question")

    assert result["answer"] == "a different answer without context"
    assert llm.generate.call_count == 2


def test_cache_still_works_without_conversation_context():
    qa, llm = _make_qa()

    qa.answer_question("same question")
    llm.generate.return_value = "should not be used"
    result = qa.answer_question("same question")

    assert result["cached"] is True
    assert llm.generate.call_count == 1
