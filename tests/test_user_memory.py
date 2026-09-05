"""Tests for utils.memory.UserMemory.

Covers the two things that matter for a long-running process: per-user
history stays capped at max_history, and the whole dict stays capped at
max_users via LRU eviction (this is the fix for the memory-leak issue
tracked as #6 - the OrderedDict eviction path is the part worth pinning
down with tests).
"""

from utils.memory import UserMemory


def test_add_and_get_interaction():
    memory = UserMemory(max_history=3)
    memory.add_interaction(user_id=1, query="hi", response="hello", interaction_type="text")

    history = memory.get_history(1)
    assert len(history) == 1
    assert history[0]["query"] == "hi"
    assert history[0]["response"] == "hello"
    assert history[0]["type"] == "text"


def test_history_capped_at_max_history_per_user():
    memory = UserMemory(max_history=3)
    for i in range(5):
        memory.add_interaction(user_id=1, query=f"q{i}", response=f"a{i}")

    history = memory.get_history(1)
    assert len(history) == 3
    # Oldest interactions are dropped, newest ones survive.
    assert [item["query"] for item in history] == ["q2", "q3", "q4"]


def test_get_history_for_unknown_user_is_empty_list():
    memory = UserMemory()
    assert memory.get_history(999) == []


def test_clear_history_removes_the_user_entirely():
    memory = UserMemory()
    memory.add_interaction(user_id=1, query="q", response="a")
    memory.clear_history(1)

    assert memory.get_history(1) == []
    assert 1 not in memory.history


def test_clear_history_on_unknown_user_does_not_raise():
    memory = UserMemory()
    memory.clear_history(42)  # should be a no-op, not an exception


def test_get_context_formats_previous_interactions():
    memory = UserMemory()
    memory.add_interaction(user_id=1, query="What is X?", response="X is Y" * 50)

    context = memory.get_context(1)
    assert "Previous interactions:" in context
    assert "Q: What is X?" in context


def test_get_context_for_user_with_no_history_is_empty_string():
    memory = UserMemory()
    assert memory.get_context(1) == ""


def test_evicts_least_recently_active_user_at_capacity():
    memory = UserMemory(max_history=3, max_users=2)
    memory.add_interaction(user_id=1, query="q", response="a")
    memory.add_interaction(user_id=2, query="q", response="a")
    memory.add_interaction(user_id=3, query="q", response="a")  # over max_users=2

    assert len(memory.history) == 2
    assert 1 not in memory.history
    assert 2 in memory.history
    assert 3 in memory.history


def test_touching_a_user_protects_them_from_eviction():
    memory = UserMemory(max_history=3, max_users=2)
    memory.add_interaction(user_id=1, query="q", response="a")
    memory.add_interaction(user_id=2, query="q", response="a")
    memory.add_interaction(user_id=1, query="q2", response="a2")  # re-touch user 1
    memory.add_interaction(user_id=3, query="q", response="a")  # should evict user 2

    assert 1 in memory.history
    assert 2 not in memory.history
    assert 3 in memory.history
