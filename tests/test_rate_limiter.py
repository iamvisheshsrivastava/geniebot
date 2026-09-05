"""Tests for utils.cache.RateLimiter.

RateLimiter is what stands between the shared OpenRouter key and one user
burning through the whole free-tier quota, so the fixed-window accounting
and the eviction cap both need to actually hold up.
"""

import time

from utils.cache import RateLimiter


def test_allows_requests_under_the_limit():
    limiter = RateLimiter(limit=3, window_seconds=60)
    assert limiter.allow(user_id=1)
    assert limiter.allow(user_id=1)
    assert limiter.allow(user_id=1)


def test_blocks_requests_over_the_limit():
    limiter = RateLimiter(limit=2, window_seconds=60)
    assert limiter.allow(user_id=1)
    assert limiter.allow(user_id=1)
    assert not limiter.allow(user_id=1)


def test_users_are_tracked_independently():
    limiter = RateLimiter(limit=1, window_seconds=60)
    assert limiter.allow(user_id=1)
    assert not limiter.allow(user_id=1)
    # A different user has their own counter, unaffected by user 1's usage.
    assert limiter.allow(user_id=2)


def test_window_resets_after_expiry():
    limiter = RateLimiter(limit=1, window_seconds=60)
    assert limiter.allow(user_id=1)
    assert not limiter.allow(user_id=1)

    # Manually expire the window instead of sleeping 60s in a test.
    expires_at, count = limiter._counters[1]
    limiter._counters[1] = (time.time() - 1, count)

    assert limiter.allow(user_id=1)


def test_seconds_until_reset_is_never_negative():
    limiter = RateLimiter(limit=1, window_seconds=30)
    assert limiter.seconds_until_reset(user_id=1) == 0  # unseen user
    limiter.allow(user_id=1)
    remaining = limiter.seconds_until_reset(user_id=1)
    assert 0 <= remaining <= 30


def test_evicts_least_recently_active_user_at_capacity():
    limiter = RateLimiter(limit=10, window_seconds=60, max_users=2)
    limiter.allow(user_id=1)
    limiter.allow(user_id=2)
    limiter.allow(user_id=3)  # pushes the dict over max_users=2

    assert len(limiter._counters) == 2
    # user 1 was least-recently touched and should have been evicted first.
    assert 1 not in limiter._counters
    assert 2 in limiter._counters
    assert 3 in limiter._counters


def test_touching_a_user_protects_them_from_eviction():
    limiter = RateLimiter(limit=10, window_seconds=60, max_users=2)
    limiter.allow(user_id=1)
    limiter.allow(user_id=2)
    limiter.allow(user_id=1)  # re-touch user 1, so user 2 is now the oldest
    limiter.allow(user_id=3)  # should evict user 2, not user 1

    assert 1 in limiter._counters
    assert 2 not in limiter._counters
    assert 3 in limiter._counters
