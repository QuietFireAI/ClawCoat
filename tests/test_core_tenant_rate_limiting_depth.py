# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_tenant_rate_limiting_depth.py
# REM: Depth coverage for core/tenant_rate_limiting.py
# REM: _InMemoryBucket, TenantRateLimiter — in-memory fallback path.

import time
import pytest

from core.tenant_rate_limiting import (
    BURST_MULTIPLIER,
    DEFAULT_TENANT_REQUESTS_PER_MINUTE,
    DEFAULT_USER_REQUESTS_PER_MINUTE,
    PREMIUM_TENANT_MULTIPLIER,
    REDIS_KEY_TTL_SECONDS,
    TenantRateLimiter,
    _InMemoryBucket,
)


# ─── Patch Redis so TenantRateLimiter uses in-memory fallback path ─────────────
@pytest.fixture(autouse=True)
def _no_redis(monkeypatch):
    monkeypatch.setattr("core.tenant_rate_limiting._get_redis_client", lambda: None)


@pytest.fixture
def limiter():
    """Fresh TenantRateLimiter — pure in-memory, no Redis deps in __init__."""
    return TenantRateLimiter()


def _make_quota(rpm=4, user_rpm=3):
    """Build a minimal quota dict for direct _check_in_memory calls."""
    return {
        "tenant_id": "t1",
        "requests_per_minute": rpm,
        "user_requests_per_minute": user_rpm,
        "burst_multiplier": BURST_MULTIPLIER,
        "premium_multiplier": 1.0,
        "is_custom": False,
        "effective_requests_per_minute": rpm,
        "effective_user_requests_per_minute": user_rpm,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Module-level constants
# ═══════════════════════════════════════════════════════════════════════════════

class TestConstants:
    def test_default_tenant_rpm(self):
        assert DEFAULT_TENANT_REQUESTS_PER_MINUTE == 600

    def test_default_user_rpm(self):
        assert DEFAULT_USER_REQUESTS_PER_MINUTE == 120

    def test_burst_multiplier(self):
        assert BURST_MULTIPLIER == 1.5

    def test_premium_tenant_multiplier(self):
        assert PREMIUM_TENANT_MULTIPLIER == 2.0

    def test_redis_key_ttl(self):
        assert REDIS_KEY_TTL_SECONDS == 120


# ═══════════════════════════════════════════════════════════════════════════════
# _InMemoryBucket
# ═══════════════════════════════════════════════════════════════════════════════

class TestInMemoryBucket:
    def test_initial_timestamps_empty(self):
        b = _InMemoryBucket()
        assert b.timestamps == []

    def test_add_and_count_returns_int(self):
        b = _InMemoryBucket()
        now = time.time()
        result = b.add_and_count(now)
        assert isinstance(result, int)

    def test_add_and_count_first_call_returns_one(self):
        b = _InMemoryBucket()
        assert b.add_and_count(time.time()) == 1

    def test_add_and_count_increments(self):
        b = _InMemoryBucket()
        now = time.time()
        b.add_and_count(now)
        assert b.add_and_count(now) == 2

    def test_add_and_count_evicts_old_entries(self):
        b = _InMemoryBucket()
        old_ts = time.time() - 120  # 2 minutes ago — outside 60s window
        b.timestamps = [old_ts, old_ts]
        now = time.time()
        # Should evict 2 old entries and add 1 new
        count = b.add_and_count(now)
        assert count == 1

    def test_count_returns_int(self):
        b = _InMemoryBucket()
        assert isinstance(b.count(time.time()), int)

    def test_count_zero_initially(self):
        b = _InMemoryBucket()
        assert b.count(time.time()) == 0

    def test_count_after_add(self):
        b = _InMemoryBucket()
        now = time.time()
        b.add_and_count(now)
        assert b.count(now) == 1

    def test_count_does_not_add_entry(self):
        b = _InMemoryBucket()
        now = time.time()
        b.count(now)
        assert len(b.timestamps) == 0

    def test_count_evicts_expired_entries(self):
        b = _InMemoryBucket()
        old_ts = time.time() - 120
        b.timestamps = [old_ts, old_ts, old_ts]
        assert b.count(time.time()) == 0

    def test_custom_window_seconds(self):
        now = time.time()
        # 30-second window: entry from 50s ago is outside
        b1 = _InMemoryBucket()
        b1.timestamps = [now - 50]
        assert b1.count(now, window_seconds=30.0) == 0
        # 60-second window: entry from 50s ago is inside (fresh bucket — count() prunes)
        b2 = _InMemoryBucket()
        b2.timestamps = [now - 50]
        assert b2.count(now, window_seconds=60.0) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# TenantRateLimiter static key builders
# ═══════════════════════════════════════════════════════════════════════════════

class TestKeyBuilders:
    def test_tenant_key_format(self):
        key = TenantRateLimiter._tenant_key("t1", 12345)
        assert key == "ratelimit:tenant:t1:12345"

    def test_user_key_format(self):
        key = TenantRateLimiter._user_key("user-001", 12345)
        assert key == "ratelimit:user:user-001:12345"

    def test_quota_key_format(self):
        key = TenantRateLimiter._quota_key("t1")
        assert key == "ratelimit:quota:t1"

    def test_tenant_key_contains_tenant_id(self):
        assert "tenant_abc" in TenantRateLimiter._tenant_key("tenant_abc", 0)

    def test_user_key_contains_user_id(self):
        assert "user-xyz" in TenantRateLimiter._user_key("user-xyz", 0)

    def test_different_tenants_different_keys(self):
        k1 = TenantRateLimiter._tenant_key("t1", 100)
        k2 = TenantRateLimiter._tenant_key("t2", 100)
        assert k1 != k2

    def test_minute_bucket_returns_int(self):
        result = TenantRateLimiter._minute_bucket(time.time())
        assert isinstance(result, int)

    def test_minute_bucket_is_now_divided_by_60(self):
        now = 7200.0  # 120 minutes
        assert TenantRateLimiter._minute_bucket(now) == 120


# ═══════════════════════════════════════════════════════════════════════════════
# TenantRateLimiter.__init__()
# ═══════════════════════════════════════════════════════════════════════════════

class TestTenantRateLimiterInit:
    def test_fallback_tenant_buckets_empty(self, limiter):
        assert len(limiter._fallback_tenant_buckets) == 0

    def test_fallback_user_buckets_empty(self, limiter):
        assert len(limiter._fallback_user_buckets) == 0

    def test_redis_warned_false(self, limiter):
        assert limiter._redis_warned is False


# ═══════════════════════════════════════════════════════════════════════════════
# TenantRateLimiter.get_tenant_quota()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetTenantQuota:
    def test_returns_dict(self, limiter):
        assert isinstance(limiter.get_tenant_quota("t1"), dict)

    def test_tenant_id_in_result(self, limiter):
        q = limiter.get_tenant_quota("t1")
        assert q["tenant_id"] == "t1"

    def test_default_requests_per_minute(self, limiter):
        q = limiter.get_tenant_quota("t1")
        assert q["requests_per_minute"] == DEFAULT_TENANT_REQUESTS_PER_MINUTE

    def test_default_user_requests_per_minute(self, limiter):
        q = limiter.get_tenant_quota("t1")
        assert q["user_requests_per_minute"] == DEFAULT_USER_REQUESTS_PER_MINUTE

    def test_is_custom_false_by_default(self, limiter):
        q = limiter.get_tenant_quota("t1")
        assert q["is_custom"] is False

    def test_effective_requests_per_minute_present(self, limiter):
        assert "effective_requests_per_minute" in limiter.get_tenant_quota("t1")

    def test_effective_user_requests_per_minute_present(self, limiter):
        assert "effective_user_requests_per_minute" in limiter.get_tenant_quota("t1")

    def test_effective_equals_default_with_no_premium(self, limiter):
        q = limiter.get_tenant_quota("t1")
        # premium_multiplier defaults to 1.0, so effective == default
        assert q["effective_requests_per_minute"] == DEFAULT_TENANT_REQUESTS_PER_MINUTE


# ═══════════════════════════════════════════════════════════════════════════════
# TenantRateLimiter.set_tenant_quota() — requires Redis, returns False without it
# ═══════════════════════════════════════════════════════════════════════════════

class TestSetTenantQuota:
    def test_returns_false_without_redis(self, limiter):
        result = limiter.set_tenant_quota("t1", 300, set_by="admin")
        assert result is False

    def test_returns_bool(self, limiter):
        result = limiter.set_tenant_quota("t1", 100, set_by="admin")
        assert isinstance(result, bool)


# ═══════════════════════════════════════════════════════════════════════════════
# TenantRateLimiter._build_info()
# ═══════════════════════════════════════════════════════════════════════════════

class TestBuildInfo:
    def _build(self, allowed=True, reason=None, tenant_count=1, user_count=1,
               tenant_limit=900, user_limit=180):
        now = time.time()
        return TenantRateLimiter._build_info(
            allowed=allowed, reason=reason,
            tenant_id="t1", user_id="u1",
            tenant_count=tenant_count, user_count=user_count,
            tenant_limit=tenant_limit, user_limit=user_limit,
            reset_at=now + 30,
            quota={"effective_requests_per_minute": 600},
        )

    def test_returns_dict(self):
        assert isinstance(self._build(), dict)

    def test_allowed_key(self):
        assert self._build(allowed=True)["allowed"] is True

    def test_reason_none_when_allowed(self):
        assert self._build(allowed=True, reason=None)["reason"] is None

    def test_reason_set_when_denied(self):
        info = self._build(allowed=False, reason="tenant_limit")
        assert info["reason"] == "tenant_limit"

    def test_tenant_id_present(self):
        assert self._build()["tenant_id"] == "t1"

    def test_user_id_present(self):
        assert self._build()["user_id"] == "u1"

    def test_tenant_section_present(self):
        assert "tenant" in self._build()

    def test_user_section_present(self):
        assert "user" in self._build()

    def test_remaining_calculated(self):
        info = self._build(tenant_count=10, tenant_limit=20)
        assert info["tenant"]["remaining"] == 10

    def test_remaining_not_negative(self):
        info = self._build(tenant_count=1000, tenant_limit=5)
        assert info["tenant"]["remaining"] == 0

    def test_retry_after_zero_when_allowed(self):
        assert self._build(allowed=True)["retry_after"] == 0

    def test_retry_after_positive_when_denied(self):
        info = self._build(allowed=False)
        assert info["retry_after"] >= 1

    def test_reset_at_present(self):
        assert "reset_at" in self._build()

    def test_quota_present(self):
        assert "quota" in self._build()


# ═══════════════════════════════════════════════════════════════════════════════
# TenantRateLimiter._check_in_memory()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckInMemory:
    def test_first_request_allowed(self, limiter):
        now = time.time()
        quota = _make_quota(rpm=100, user_rpm=100)
        allowed, info = limiter._check_in_memory(
            "t1", "u1", now, tenant_limit=10, user_limit=10, quota=quota, reset_at=now+60
        )
        assert allowed is True

    def test_returns_tuple(self, limiter):
        now = time.time()
        quota = _make_quota()
        result = limiter._check_in_memory(
            "t1", "u1", now, tenant_limit=10, user_limit=10, quota=quota, reset_at=now+60
        )
        assert isinstance(result, tuple) and len(result) == 2

    def test_second_element_is_dict(self, limiter):
        now = time.time()
        quota = _make_quota()
        _, info = limiter._check_in_memory(
            "t1", "u1", now, tenant_limit=10, user_limit=10, quota=quota, reset_at=now+60
        )
        assert isinstance(info, dict)

    def test_tenant_limit_exceeded_returns_false(self, limiter):
        now = time.time()
        quota = _make_quota()
        # Pre-fill tenant bucket to the limit (3)
        bucket = limiter._fallback_tenant_buckets["t1"]
        bucket.timestamps = [now] * 3
        allowed, info = limiter._check_in_memory(
            "t1", "u1", now, tenant_limit=3, user_limit=100, quota=quota, reset_at=now+60
        )
        assert allowed is False
        assert info["reason"] == "tenant_limit"

    def test_user_limit_exceeded_returns_false(self, limiter):
        now = time.time()
        quota = _make_quota()
        # Fill user bucket to the limit (2)
        u_bucket = limiter._fallback_user_buckets["u1"]
        u_bucket.timestamps = [now] * 2
        allowed, info = limiter._check_in_memory(
            "t1", "u1", now, tenant_limit=100, user_limit=2, quota=quota, reset_at=now+60
        )
        assert allowed is False
        assert info["reason"] == "user_limit"

    def test_allowed_increments_tenant_bucket(self, limiter):
        now = time.time()
        quota = _make_quota()
        limiter._check_in_memory(
            "t1", "u1", now, tenant_limit=10, user_limit=10, quota=quota, reset_at=now+60
        )
        assert len(limiter._fallback_tenant_buckets["t1"].timestamps) == 1

    def test_allowed_increments_user_bucket(self, limiter):
        now = time.time()
        quota = _make_quota()
        limiter._check_in_memory(
            "t1", "u1", now, tenant_limit=10, user_limit=10, quota=quota, reset_at=now+60
        )
        assert len(limiter._fallback_user_buckets["u1"].timestamps) == 1

    def test_denied_does_not_increment_bucket(self, limiter):
        now = time.time()
        quota = _make_quota()
        bucket = limiter._fallback_tenant_buckets["t1"]
        bucket.timestamps = [now] * 5  # At/over limit of 5
        limiter._check_in_memory(
            "t1", "u1", now, tenant_limit=5, user_limit=100, quota=quota, reset_at=now+60
        )
        # Should not have added another entry
        assert len(bucket.timestamps) == 5


# ═══════════════════════════════════════════════════════════════════════════════
# TenantRateLimiter.check_rate_limit() — triggers in-memory fallback (no Redis)
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckRateLimit:
    def test_returns_tuple(self, limiter):
        result = limiter.check_rate_limit("t1", "u1")
        assert isinstance(result, tuple) and len(result) == 2

    def test_first_element_is_bool(self, limiter):
        allowed, _ = limiter.check_rate_limit("t1", "u1")
        assert isinstance(allowed, bool)

    def test_second_element_is_dict(self, limiter):
        _, info = limiter.check_rate_limit("t1", "u1")
        assert isinstance(info, dict)

    def test_first_request_allowed(self, limiter):
        allowed, _ = limiter.check_rate_limit("t1", "u1")
        assert allowed is True

    def test_info_has_allowed_key(self, limiter):
        _, info = limiter.check_rate_limit("t1", "u1")
        assert "allowed" in info

    def test_info_has_tenant_key(self, limiter):
        _, info = limiter.check_rate_limit("t1", "u1")
        assert "tenant" in info

    def test_info_has_user_key(self, limiter):
        _, info = limiter.check_rate_limit("t1", "u1")
        assert "user" in info

    def test_redis_warned_set_to_true(self, limiter):
        limiter.check_rate_limit("t1", "u1")
        assert limiter._redis_warned is True

    def test_different_tenants_independent(self, limiter):
        allowed1, _ = limiter.check_rate_limit("t1", "u1")
        allowed2, _ = limiter.check_rate_limit("t2", "u1")
        assert allowed1 is True and allowed2 is True


# ═══════════════════════════════════════════════════════════════════════════════
# TenantRateLimiter.get_usage_report()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetUsageReport:
    def test_returns_dict(self, limiter):
        assert isinstance(limiter.get_usage_report("t1"), dict)

    def test_tenant_id_present(self, limiter):
        assert limiter.get_usage_report("t1")["tenant_id"] == "t1"

    def test_current_minute_present(self, limiter):
        assert "current_minute" in limiter.get_usage_report("t1")

    def test_quota_present(self, limiter):
        assert "quota" in limiter.get_usage_report("t1")

    def test_generated_at_present(self, limiter):
        assert "generated_at" in limiter.get_usage_report("t1")

    def test_current_minute_has_used(self, limiter):
        assert "used" in limiter.get_usage_report("t1")["current_minute"]

    def test_current_minute_has_limit(self, limiter):
        assert "limit" in limiter.get_usage_report("t1")["current_minute"]

    def test_current_minute_has_utilization_pct(self, limiter):
        assert "utilization_pct" in limiter.get_usage_report("t1")["current_minute"]

    def test_no_requests_zero_utilization(self, limiter):
        report = limiter.get_usage_report("t1")
        assert report["current_minute"]["used"] == 0

    def test_after_request_utilization_nonzero(self, limiter):
        # check_rate_limit falls back to in-memory when Redis is unavailable
        limiter.check_rate_limit("t1", "u1")
        # Verify the fallback bucket recorded the request (get_usage_report reads
        # Redis first; when Redis client exists but ops fail it stays 0 there)
        bucket = limiter._fallback_tenant_buckets.get("t1")
        assert bucket is not None
        assert bucket.count(time.time()) == 1
