# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_session_management_depth.py
# REM: Depth coverage for core/session_management.py
# REM: SessionConfig, UserSession, SessionManager — in-memory.

import pytest
from datetime import datetime, timedelta, timezone

from core.session_management import (
    PRIVILEGED_IDLE_MINUTES,
    PRIVILEGED_ROLES,
    SessionConfig,
    SessionManager,
    UserSession,
)


# ─── Patch Redis so audit.log() uses in-memory path ────────────────────────────
@pytest.fixture(autouse=True)
def _no_redis(monkeypatch):
    monkeypatch.setattr("core.persistence.get_redis", lambda: None)


@pytest.fixture
def manager():
    """Bypass __init__ to avoid _load_from_redis() hitting security_store (Redis)."""
    m = object.__new__(SessionManager)
    m._config = SessionConfig()
    m._sessions = {}
    return m


def _create(manager, user_id="user-001", role="operator"):
    return manager.create_session(user_id, ip_address="127.0.0.1", user_agent="TestAgent/1.0", role=role)


# ═══════════════════════════════════════════════════════════════════════════════
# Module-level constants
# ═══════════════════════════════════════════════════════════════════════════════

class TestConstants:
    def test_privileged_roles_contains_admin(self):
        assert "admin" in PRIVILEGED_ROLES

    def test_privileged_roles_contains_security_officer(self):
        assert "security_officer" in PRIVILEGED_ROLES

    def test_privileged_roles_contains_super_admin(self):
        assert "super_admin" in PRIVILEGED_ROLES

    def test_privileged_roles_is_set(self):
        assert isinstance(PRIVILEGED_ROLES, set)

    def test_privileged_idle_minutes(self):
        assert PRIVILEGED_IDLE_MINUTES == 10


# ═══════════════════════════════════════════════════════════════════════════════
# SessionConfig defaults
# ═══════════════════════════════════════════════════════════════════════════════

class TestSessionConfig:
    def test_max_idle_minutes_default(self):
        assert SessionConfig().max_idle_minutes == 15

    def test_max_session_hours_default(self):
        assert SessionConfig().max_session_hours == 8

    def test_warning_before_logoff_seconds_default(self):
        assert SessionConfig().warning_before_logoff_seconds == 60

    def test_require_reauth_for_phi_default(self):
        assert SessionConfig().require_reauth_for_phi is True

    def test_custom_idle_minutes(self):
        assert SessionConfig(max_idle_minutes=5).max_idle_minutes == 5


# ═══════════════════════════════════════════════════════════════════════════════
# UserSession.to_dict()
# ═══════════════════════════════════════════════════════════════════════════════

class TestUserSessionToDict:
    def _make_session(self, **kwargs):
        defaults = dict(
            user_id="user-001",
            ip_address="10.0.0.1",
            user_agent="Mozilla/5.0",
            role="operator",
            mfa_verified=False,
        )
        defaults.update(kwargs)
        return UserSession(**defaults)

    def test_returns_dict(self):
        assert isinstance(self._make_session().to_dict(), dict)

    def test_session_id_present(self):
        s = self._make_session()
        assert "session_id" in s.to_dict()

    def test_user_id_present(self):
        s = self._make_session(user_id="user-999")
        assert s.to_dict()["user_id"] == "user-999"

    def test_created_at_is_isoformat(self):
        s = self._make_session()
        val = s.to_dict()["created_at"]
        datetime.fromisoformat(val)  # Must not raise

    def test_last_activity_is_isoformat(self):
        s = self._make_session()
        val = s.to_dict()["last_activity"]
        datetime.fromisoformat(val)  # Must not raise

    def test_expires_at_is_isoformat(self):
        s = self._make_session()
        val = s.to_dict()["expires_at"]
        datetime.fromisoformat(val)  # Must not raise

    def test_is_active_true(self):
        s = self._make_session()
        assert s.to_dict()["is_active"] is True

    def test_ip_address_present(self):
        s = self._make_session(ip_address="192.168.1.1")
        assert s.to_dict()["ip_address"] == "192.168.1.1"

    def test_user_agent_present(self):
        s = self._make_session(user_agent="TestBot/1.0")
        assert s.to_dict()["user_agent"] == "TestBot/1.0"

    def test_role_present(self):
        s = self._make_session(role="admin")
        assert s.to_dict()["role"] == "admin"

    def test_mfa_verified_present(self):
        s = self._make_session(mfa_verified=True)
        assert s.to_dict()["mfa_verified"] is True

    def test_ten_keys_present(self):
        s = self._make_session()
        expected = {
            "session_id", "user_id", "created_at", "last_activity",
            "expires_at", "is_active", "ip_address", "user_agent",
            "role", "mfa_verified"
        }
        assert set(s.to_dict().keys()) == expected


# ═══════════════════════════════════════════════════════════════════════════════
# SessionManager._get_idle_timeout()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetIdleTimeout:
    def test_operator_gets_default_timeout(self, manager):
        result = manager._get_idle_timeout("operator")
        assert result == timedelta(minutes=15)

    def test_admin_gets_privileged_timeout(self, manager):
        result = manager._get_idle_timeout("admin")
        assert result == timedelta(minutes=10)

    def test_security_officer_gets_privileged_timeout(self, manager):
        result = manager._get_idle_timeout("security_officer")
        assert result == timedelta(minutes=10)

    def test_super_admin_gets_privileged_timeout(self, manager):
        result = manager._get_idle_timeout("super_admin")
        assert result == timedelta(minutes=10)

    def test_unknown_role_gets_default(self, manager):
        result = manager._get_idle_timeout("guest")
        assert result == timedelta(minutes=15)

    def test_case_insensitive_admin(self, manager):
        result = manager._get_idle_timeout("ADMIN")
        assert result == timedelta(minutes=10)

    def test_returns_timedelta(self, manager):
        assert isinstance(manager._get_idle_timeout("operator"), timedelta)


# ═══════════════════════════════════════════════════════════════════════════════
# SessionManager.create_session()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCreateSession:
    def test_returns_user_session(self, manager):
        assert isinstance(_create(manager), UserSession)

    def test_session_is_active(self, manager):
        assert _create(manager).is_active is True

    def test_user_id_stored(self, manager):
        s = _create(manager, user_id="user-777")
        assert s.user_id == "user-777"

    def test_role_stored(self, manager):
        s = _create(manager, role="admin")
        assert s.role == "admin"

    def test_session_id_generated(self, manager):
        s = _create(manager)
        assert s.session_id  # Non-empty

    def test_session_stored_in_manager(self, manager):
        s = _create(manager)
        assert s.session_id in manager._sessions

    def test_ip_address_stored(self, manager):
        s = manager.create_session("user-001", ip_address="10.10.10.10")
        assert s.ip_address == "10.10.10.10"

    def test_user_agent_stored(self, manager):
        s = manager.create_session("user-001", user_agent="Firefox/100")
        assert s.user_agent == "Firefox/100"

    def test_expires_at_is_8_hours_from_now(self, manager):
        before = datetime.now(timezone.utc)
        s = _create(manager)
        after = datetime.now(timezone.utc)
        expected_min = before + timedelta(hours=8)
        expected_max = after + timedelta(hours=8)
        assert expected_min <= s.expires_at <= expected_max

    def test_multiple_sessions_unique_ids(self, manager):
        s1 = _create(manager)
        s2 = _create(manager)
        assert s1.session_id != s2.session_id

    def test_multiple_sessions_all_stored(self, manager):
        _create(manager)
        _create(manager)
        assert len(manager._sessions) == 2


# ═══════════════════════════════════════════════════════════════════════════════
# SessionManager.touch_session()
# ═══════════════════════════════════════════════════════════════════════════════

class TestTouchSession:
    def test_returns_true_for_active_session(self, manager):
        s = _create(manager)
        assert manager.touch_session(s.session_id) is True

    def test_returns_false_for_unknown_session(self, manager):
        assert manager.touch_session("nonexistent-id") is False

    def test_updates_last_activity(self, manager):
        s = _create(manager)
        old = s.last_activity
        # Force last_activity to be old
        s.last_activity = old - timedelta(minutes=5)
        manager.touch_session(s.session_id)
        assert s.last_activity > old - timedelta(minutes=5)

    def test_returns_false_for_inactive_session(self, manager):
        s = _create(manager)
        s.is_active = False
        assert manager.touch_session(s.session_id) is False


# ═══════════════════════════════════════════════════════════════════════════════
# SessionManager.check_session()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckSession:
    def test_active_session_returns_true(self, manager):
        s = _create(manager)
        assert manager.check_session(s.session_id) is True

    def test_unknown_session_returns_false(self, manager):
        assert manager.check_session("does-not-exist") is False

    def test_expired_session_returns_false(self, manager):
        s = _create(manager)
        s.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        assert manager.check_session(s.session_id) is False

    def test_expired_session_is_terminated(self, manager):
        s = _create(manager)
        s.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        manager.check_session(s.session_id)
        # Session is removed from local cache after termination (prevents memory leak)
        assert s.session_id not in manager._sessions

    def test_idle_session_returns_false(self, manager):
        s = _create(manager, role="operator")
        s.last_activity = datetime.now(timezone.utc) - timedelta(minutes=20)
        assert manager.check_session(s.session_id) is False

    def test_idle_session_is_terminated(self, manager):
        s = _create(manager, role="operator")
        s.last_activity = datetime.now(timezone.utc) - timedelta(minutes=20)
        manager.check_session(s.session_id)
        # Session is removed from local cache after termination (prevents memory leak)
        assert s.session_id not in manager._sessions

    def test_inactive_session_returns_false(self, manager):
        s = _create(manager)
        s.is_active = False
        assert manager.check_session(s.session_id) is False

    def test_privileged_role_idles_faster(self, manager):
        # Admin idle timeout is 10 min; 12 min idle → should terminate
        s = _create(manager, role="admin")
        s.last_activity = datetime.now(timezone.utc) - timedelta(minutes=12)
        assert manager.check_session(s.session_id) is False

    def test_returns_bool(self, manager):
        s = _create(manager)
        assert isinstance(manager.check_session(s.session_id), bool)


# ═══════════════════════════════════════════════════════════════════════════════
# SessionManager.terminate_session()
# ═══════════════════════════════════════════════════════════════════════════════

class TestTerminateSession:
    def test_returns_true_for_active_session(self, manager):
        s = _create(manager)
        assert manager.terminate_session(s.session_id) is True

    def test_returns_false_for_unknown_session(self, manager):
        assert manager.terminate_session("nonexistent") is False

    def test_returns_false_for_already_inactive(self, manager):
        s = _create(manager)
        manager.terminate_session(s.session_id)
        assert manager.terminate_session(s.session_id) is False

    def test_session_is_removed_after_terminate(self, manager):
        # Terminated sessions are evicted from the local cache (no memory leak)
        s = _create(manager)
        manager.terminate_session(s.session_id)
        assert s.session_id not in manager._sessions

    def test_session_no_longer_in_dict_after_terminate(self, manager):
        # Session is removed from local cache after termination (not merely marked inactive)
        s = _create(manager)
        manager.terminate_session(s.session_id)
        assert s.session_id not in manager._sessions

    def test_custom_reason_accepted(self, manager):
        s = _create(manager)
        assert manager.terminate_session(s.session_id, reason="admin_force") is True


# ═══════════════════════════════════════════════════════════════════════════════
# SessionManager.terminate_all_user_sessions()
# ═══════════════════════════════════════════════════════════════════════════════

class TestTerminateAllUserSessions:
    def test_returns_count_of_terminated(self, manager):
        _create(manager, user_id="user-A")
        _create(manager, user_id="user-A")
        assert manager.terminate_all_user_sessions("user-A") == 2

    def test_only_terminates_target_user(self, manager):
        s_a = _create(manager, user_id="user-A")
        s_b = _create(manager, user_id="user-B")
        manager.terminate_all_user_sessions("user-A")
        assert manager._sessions[s_b.session_id].is_active is True

    def test_no_sessions_returns_zero(self, manager):
        assert manager.terminate_all_user_sessions("nobody") == 0

    def test_already_inactive_not_counted(self, manager):
        s = _create(manager, user_id="user-A")
        s.is_active = False
        assert manager.terminate_all_user_sessions("user-A") == 0


# ═══════════════════════════════════════════════════════════════════════════════
# SessionManager.get_session()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetSession:
    def test_returns_session_by_id(self, manager):
        s = _create(manager)
        result = manager.get_session(s.session_id)
        assert result is s

    def test_returns_none_for_unknown(self, manager):
        assert manager.get_session("nonexistent") is None


# ═══════════════════════════════════════════════════════════════════════════════
# SessionManager.get_active_sessions()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetActiveSessions:
    def test_returns_list(self, manager):
        assert isinstance(manager.get_active_sessions(), list)

    def test_empty_initially(self, manager):
        assert manager.get_active_sessions() == []

    def test_returns_active_sessions(self, manager):
        _create(manager)
        _create(manager)
        assert len(manager.get_active_sessions()) == 2

    def test_excludes_inactive_sessions(self, manager):
        s = _create(manager)
        manager.terminate_session(s.session_id)
        assert manager.get_active_sessions() == []

    def test_filter_by_user_id(self, manager):
        _create(manager, user_id="user-A")
        _create(manager, user_id="user-B")
        result = manager.get_active_sessions(user_id="user-A")
        assert len(result) == 1
        assert result[0].user_id == "user-A"

    def test_filter_by_user_id_no_match(self, manager):
        _create(manager, user_id="user-A")
        assert manager.get_active_sessions(user_id="user-Z") == []


# ═══════════════════════════════════════════════════════════════════════════════
# SessionManager.cleanup_expired()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCleanupExpired:
    def test_returns_int(self, manager):
        assert isinstance(manager.cleanup_expired(), int)

    def test_no_sessions_returns_zero(self, manager):
        assert manager.cleanup_expired() == 0

    def test_active_non_expired_not_cleaned(self, manager):
        _create(manager)
        assert manager.cleanup_expired() == 0

    def test_expired_session_cleaned(self, manager):
        s = _create(manager)
        s.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        assert manager.cleanup_expired() == 1

    def test_idle_session_cleaned(self, manager):
        s = _create(manager, role="operator")
        s.last_activity = datetime.now(timezone.utc) - timedelta(minutes=20)
        assert manager.cleanup_expired() == 1

    def test_already_inactive_not_counted(self, manager):
        s = _create(manager)
        s.is_active = False
        assert manager.cleanup_expired() == 0

    def test_multiple_expired_all_cleaned(self, manager):
        for _ in range(3):
            s = _create(manager)
            s.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        assert manager.cleanup_expired() == 3

    def test_cleaned_sessions_removed_from_cache(self, manager):
        # Expired sessions are evicted from local cache after cleanup (no memory leak)
        s = _create(manager)
        s.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        manager.cleanup_expired()
        assert s.session_id not in manager._sessions
