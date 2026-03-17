# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_auth_dependencies_depth.py
# REM: Depth tests for core/auth_dependencies.py — pure helper functions, no FastAPI calls

import pytest
from unittest.mock import MagicMock

from core.auth import AuthResult
from core.auth_dependencies import (
    _extract_session_id,
    _resolve_rbac_user,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _auth(actor: str = "test_actor", permissions: list = None) -> AuthResult:
    return AuthResult(
        authenticated=True,
        actor=actor,
        method="api_key",
        permissions=permissions or [],
    )


def _rbac(by_username=None, by_id=None) -> MagicMock:
    """Return a mock rbac_manager with configurable lookups."""
    mgr = MagicMock()
    mgr.get_user_by_username.return_value = by_username
    mgr.get_user.return_value = by_id
    return mgr


# ═══════════════════════════════════════════════════════════════════════════════
# _extract_session_id
# ═══════════════════════════════════════════════════════════════════════════════

class TestExtractSessionId:
    def test_returns_empty_when_no_permissions(self):
        auth = _auth(permissions=[])
        assert _extract_session_id(auth) == ""

    def test_returns_empty_when_no_session_perm(self):
        auth = _auth(permissions=["read:data", "write:data"])
        assert _extract_session_id(auth) == ""

    def test_returns_session_id(self):
        auth = _auth(permissions=["session:abc123"])
        assert _extract_session_id(auth) == "abc123"

    def test_returns_session_id_from_mixed_permissions(self):
        auth = _auth(permissions=["read:data", "session:xyz789", "write:data"])
        assert _extract_session_id(auth) == "xyz789"

    def test_returns_first_session_perm(self):
        # Multiple session: entries — returns first
        auth = _auth(permissions=["session:first", "session:second"])
        assert _extract_session_id(auth) == "first"

    def test_returns_empty_for_similar_but_wrong_prefix(self):
        auth = _auth(permissions=["sessions:abc", "SESSION:abc"])
        assert _extract_session_id(auth) == ""

    def test_returns_full_uuid_session_id(self):
        sid = "550e8400-e29b-41d4-a716-446655440000"
        auth = _auth(permissions=[f"session:{sid}"])
        assert _extract_session_id(auth) == sid

    def test_returns_empty_string_type(self):
        auth = _auth(permissions=[])
        result = _extract_session_id(auth)
        assert isinstance(result, str)

    def test_session_with_colons_in_id(self):
        # ID containing extra colons — only strips the first "session:" prefix
        auth = _auth(permissions=["session:abc:def"])
        assert _extract_session_id(auth) == "abc:def"


# ═══════════════════════════════════════════════════════════════════════════════
# _resolve_rbac_user
# ═══════════════════════════════════════════════════════════════════════════════

class TestResolveRbacUser:
    def test_returns_none_when_not_found(self):
        auth = _auth(actor="unknown_actor")
        rbac = _rbac(by_username=None, by_id=None)
        assert _resolve_rbac_user(auth, rbac) is None

    def test_returns_user_found_by_username(self):
        user = MagicMock()
        auth = _auth(actor="alice")
        rbac = _rbac(by_username=user, by_id=None)
        result = _resolve_rbac_user(auth, rbac)
        assert result is user

    def test_returns_user_found_by_user_id_when_username_fails(self):
        user = MagicMock()
        auth = _auth(actor="alice")
        rbac = _rbac(by_username=None, by_id=user)
        result = _resolve_rbac_user(auth, rbac)
        assert result is user

    def test_parses_owner_colon_label_format(self):
        user = MagicMock()
        auth = _auth(actor="alice:api_key_label")
        rbac = _rbac(by_username=user, by_id=None)
        result = _resolve_rbac_user(auth, rbac)
        # get_user_by_username called with "alice" (before the colon)
        rbac.get_user_by_username.assert_called_with("alice")
        assert result is user

    def test_falls_through_to_full_actor_as_user_id(self):
        user = MagicMock()
        auth = _auth(actor="alice:label")
        # username lookup fails, first id lookup fails, full actor lookup succeeds
        mgr = MagicMock()
        mgr.get_user_by_username.return_value = None
        # First call returns None, second call returns the user
        mgr.get_user.side_effect = [None, user]
        result = _resolve_rbac_user(auth, mgr)
        assert result is user

    def test_username_lookup_called_with_parsed_name(self):
        auth = _auth(actor="bob")
        rbac = _rbac(by_username=None, by_id=None)
        _resolve_rbac_user(auth, rbac)
        rbac.get_user_by_username.assert_called_once_with("bob")

    def test_id_lookup_called_when_username_fails(self):
        auth = _auth(actor="bob")
        rbac = _rbac(by_username=None, by_id=None)
        _resolve_rbac_user(auth, rbac)
        rbac.get_user.assert_called_with("bob")

    def test_simple_actor_no_colon(self):
        # actor with no colon — actor_name equals actor
        user = MagicMock()
        auth = _auth(actor="simple_user")
        rbac = _rbac(by_username=user, by_id=None)
        result = _resolve_rbac_user(auth, rbac)
        assert result is user

    def test_returns_none_type_none(self):
        auth = _auth(actor="ghost")
        rbac = _rbac(by_username=None, by_id=None)
        result = _resolve_rbac_user(auth, rbac)
        assert result is None
