# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_delegation_depth.py
# REM: Coverage depth tests for core/delegation.py
# REM: Targets: DelegationManager delegate/revoke/check/cleanup logic (pure unit tests)

import pytest
from datetime import datetime, timezone, timedelta


@pytest.fixture
def mgr():
    """Fresh DelegationManager with no Redis (in-memory only)."""
    from core.delegation import DelegationManager
    m = DelegationManager()
    m._redis = None  # force in-memory only
    return m


CAPS = ["filesystem.read:/data/*", "filesystem.write:/app/*", "network.http:api/*"]


# ═══════════════════════════════════════════════════════════════════════════════
# DelegationStatus enum
# ═══════════════════════════════════════════════════════════════════════════════

class TestDelegationStatus:
    def test_active_value(self):
        from core.delegation import DelegationStatus
        assert DelegationStatus.ACTIVE.value == "active"

    def test_revoked_value(self):
        from core.delegation import DelegationStatus
        assert DelegationStatus.REVOKED.value == "revoked"

    def test_expired_value(self):
        from core.delegation import DelegationStatus
        assert DelegationStatus.EXPIRED.value == "expired"


# ═══════════════════════════════════════════════════════════════════════════════
# CapabilityDelegation dataclass
# ═══════════════════════════════════════════════════════════════════════════════

class TestCapabilityDelegation:
    def test_is_valid_active_unexpired(self):
        from core.delegation import CapabilityDelegation, DelegationStatus
        now = datetime.now(timezone.utc)
        d = CapabilityDelegation(
            delegation_id="del-001",
            grantor_id="agent-a",
            grantee_id="agent-b",
            capability="filesystem.read:/data/*",
            constraints={},
            created_at=now,
            expires_at=now + timedelta(hours=1),
        )
        assert d.is_valid() is True

    def test_is_valid_expired(self):
        from core.delegation import CapabilityDelegation, DelegationStatus
        now = datetime.now(timezone.utc)
        d = CapabilityDelegation(
            delegation_id="del-002",
            grantor_id="agent-a",
            grantee_id="agent-b",
            capability="filesystem.read:/data/*",
            constraints={},
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
        )
        assert d.is_valid() is False

    def test_is_valid_revoked(self):
        from core.delegation import CapabilityDelegation, DelegationStatus
        now = datetime.now(timezone.utc)
        d = CapabilityDelegation(
            delegation_id="del-003",
            grantor_id="agent-a",
            grantee_id="agent-b",
            capability="filesystem.read:/data/*",
            constraints={},
            created_at=now,
            expires_at=now + timedelta(hours=1),
            status=DelegationStatus.REVOKED,
        )
        assert d.is_valid() is False

    def test_to_dict_contains_required_fields(self):
        from core.delegation import CapabilityDelegation
        now = datetime.now(timezone.utc)
        d = CapabilityDelegation(
            delegation_id="del-004",
            grantor_id="agent-a",
            grantee_id="agent-b",
            capability="filesystem.read:/data/*",
            constraints={"max_files": 100},
            created_at=now,
            expires_at=now + timedelta(hours=1),
        )
        d_dict = d.to_dict()
        assert d_dict["delegation_id"] == "del-004"
        assert d_dict["grantor_id"] == "agent-a"
        assert d_dict["capability"] == "filesystem.read:/data/*"
        assert "status" in d_dict
        assert "expires_at" in d_dict


# ═══════════════════════════════════════════════════════════════════════════════
# DelegationManager.delegate()
# ═══════════════════════════════════════════════════════════════════════════════

class TestDelegate:
    def test_delegate_success(self, mgr):
        ok, msg, did = mgr.delegate(
            grantor_id="agent-a",
            grantee_id="agent-b",
            capability="filesystem.read:/data/*",
            grantor_capabilities=CAPS,
        )
        assert ok is True
        assert did is not None

    def test_delegate_creates_indexes(self, mgr):
        mgr.delegate("agent-a", "agent-b", "filesystem.read:/data/*", CAPS)
        assert "agent-a" in mgr._by_grantor
        assert "agent-b" in mgr._by_grantee

    def test_delegate_self_rejected(self, mgr):
        ok, msg, did = mgr.delegate(
            grantor_id="agent-a",
            grantee_id="agent-a",
            capability="filesystem.read:/data/*",
            grantor_capabilities=CAPS,
        )
        assert ok is False
        assert "self" in msg.lower()
        assert did is None

    def test_delegate_without_capability_rejected(self, mgr):
        ok, msg, did = mgr.delegate(
            grantor_id="agent-a",
            grantee_id="agent-b",
            capability="network.admin:*",
            grantor_capabilities=CAPS,
        )
        assert ok is False
        assert did is None

    def test_delegate_duration_capped_at_24h(self, mgr):
        ok, msg, did = mgr.delegate(
            grantor_id="agent-a",
            grantee_id="agent-b",
            capability="filesystem.read:/data/*",
            grantor_capabilities=CAPS,
            duration_hours=999,
        )
        assert ok is True
        delegation = mgr._delegations[did]
        delta = delegation.expires_at - delegation.created_at
        assert delta.total_seconds() <= (24 * 3600) + 5  # small buffer for timing

    def test_delegate_with_constraints(self, mgr):
        ok, msg, did = mgr.delegate(
            grantor_id="agent-a",
            grantee_id="agent-b",
            capability="filesystem.read:/data/*",
            grantor_capabilities=CAPS,
            constraints={"max_ops": 50},
        )
        assert ok is True
        assert mgr._delegations[did].constraints == {"max_ops": 50}

    def test_delegate_chain_via_delegated_capability(self, mgr):
        # agent-a delegates to agent-b
        ok1, _, did1 = mgr.delegate("agent-a", "agent-b",
                                     "filesystem.read:/data/*", CAPS)
        assert ok1 is True
        # agent-b sub-delegates to agent-c using delegated capability
        ok2, _, did2 = mgr.delegate(
            "agent-b", "agent-c",
            "filesystem.read:/data/*",
            grantor_capabilities=[],
            parent_delegation_id=did1,
        )
        assert ok2 is True
        assert mgr._delegations[did2].delegation_depth == 1

    def test_delegate_chain_too_deep_rejected(self, mgr):
        did_prev = None
        for i in range(mgr.MAX_DELEGATION_DEPTH):
            grantor = f"agent-chain-{i}"
            grantee = f"agent-chain-{i+1}"
            caps_to_use = CAPS if i == 0 else []
            ok, _, did = mgr.delegate(
                grantor, grantee,
                "filesystem.read:/data/*",
                grantor_capabilities=caps_to_use,
                parent_delegation_id=did_prev,
            )
            assert ok is True, f"Step {i} failed"
            did_prev = did

        # One level too deep
        ok, msg, did = mgr.delegate(
            f"agent-chain-{mgr.MAX_DELEGATION_DEPTH}",
            "agent-chain-final",
            "filesystem.read:/data/*",
            grantor_capabilities=[],
            parent_delegation_id=did_prev,
        )
        assert ok is False
        assert "deep" in msg.lower()

    def test_delegate_parent_not_found_rejected(self, mgr):
        ok, msg, did = mgr.delegate(
            "agent-a", "agent-b",
            "filesystem.read:/data/*",
            grantor_capabilities=CAPS,
            parent_delegation_id="nonexistent-parent-id",
        )
        assert ok is False
        assert did is None


# ═══════════════════════════════════════════════════════════════════════════════
# DelegationManager.revoke()
# ═══════════════════════════════════════════════════════════════════════════════

class TestRevoke:
    def test_revoke_existing_delegation(self, mgr):
        _, _, did = mgr.delegate("agent-a", "agent-b",
                                  "filesystem.read:/data/*", CAPS)
        ok, msg = mgr.revoke(did, revoked_by="admin", reason="security review")
        assert ok is True
        assert mgr._delegations[did].status.value == "revoked"

    def test_revoke_nonexistent_delegation(self, mgr):
        ok, msg = mgr.revoke("del-nonexistent", revoked_by="admin", reason="test")
        assert ok is False

    def test_revoke_already_revoked_returns_false(self, mgr):
        _, _, did = mgr.delegate("agent-a", "agent-b",
                                  "filesystem.read:/data/*", CAPS)
        mgr.revoke(did, "admin", "first")
        ok, msg = mgr.revoke(did, "admin", "second")
        assert ok is False

    def test_revoke_cascades_to_children(self, mgr):
        _, _, did_parent = mgr.delegate("agent-a", "agent-b",
                                         "filesystem.read:/data/*", CAPS)
        _, _, did_child = mgr.delegate(
            "agent-b", "agent-c",
            "filesystem.read:/data/*",
            grantor_capabilities=[],
            parent_delegation_id=did_parent,
        )
        ok, msg = mgr.revoke(did_parent, "admin", "cascade test")
        assert ok is True
        assert mgr._delegations[did_child].status.value == "revoked"

    def test_revoke_sets_revoked_by(self, mgr):
        _, _, did = mgr.delegate("agent-a", "agent-b",
                                  "filesystem.read:/data/*", CAPS)
        mgr.revoke(did, revoked_by="security-officer", reason="audit")
        assert mgr._delegations[did].revoked_by == "security-officer"

    def test_revoke_sets_revocation_reason(self, mgr):
        _, _, did = mgr.delegate("agent-a", "agent-b",
                                  "filesystem.read:/data/*", CAPS)
        mgr.revoke(did, "admin", reason="policy violation")
        assert mgr._delegations[did].revocation_reason == "policy violation"


# ═══════════════════════════════════════════════════════════════════════════════
# check_delegated_permission()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckDelegatedPermission:
    def test_has_permission_via_delegation(self, mgr):
        _, _, did = mgr.delegate("agent-a", "agent-b",
                                  "filesystem.read:/data/*", CAPS)
        has_perm, delegation_id = mgr.check_delegated_permission(
            "agent-b", "filesystem.read:/data/*"
        )
        assert has_perm is True
        assert delegation_id == did

    def test_no_permission_not_delegated(self, mgr):
        has_perm, delegation_id = mgr.check_delegated_permission(
            "agent-nobody", "filesystem.read:/data/*"
        )
        assert has_perm is False
        assert delegation_id is None

    def test_no_permission_after_revocation(self, mgr):
        _, _, did = mgr.delegate("agent-a", "agent-b",
                                  "filesystem.read:/data/*", CAPS)
        mgr.revoke(did, "admin", "test")
        has_perm, _ = mgr.check_delegated_permission(
            "agent-b", "filesystem.read:/data/*"
        )
        assert has_perm is False

    def test_no_permission_wrong_capability(self, mgr):
        mgr.delegate("agent-a", "agent-b", "filesystem.read:/data/*", CAPS)
        has_perm, _ = mgr.check_delegated_permission(
            "agent-b", "filesystem.write:/prod/*"
        )
        assert has_perm is False


# ═══════════════════════════════════════════════════════════════════════════════
# get_grantee_capabilities() / get_grantor_delegations()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetCapabilities:
    def test_get_grantee_capabilities_active(self, mgr):
        mgr.delegate("agent-a", "agent-b", "filesystem.read:/data/*", CAPS)
        caps = mgr.get_grantee_capabilities("agent-b")
        assert len(caps) >= 1
        assert caps[0]["capability"] == "filesystem.read:/data/*"

    def test_get_grantee_capabilities_empty_for_unknown(self, mgr):
        caps = mgr.get_grantee_capabilities("agent-nobody")
        assert caps == []

    def test_get_grantee_capabilities_excludes_revoked(self, mgr):
        _, _, did = mgr.delegate("agent-a", "agent-b",
                                  "filesystem.read:/data/*", CAPS)
        mgr.revoke(did, "admin", "test")
        caps = mgr.get_grantee_capabilities("agent-b")
        assert len(caps) == 0

    def test_get_grantor_delegations(self, mgr):
        mgr.delegate("agent-a", "agent-b", "filesystem.read:/data/*", CAPS)
        mgr.delegate("agent-a", "agent-c", "filesystem.write:/app/*", CAPS)
        dels = mgr.get_grantor_delegations("agent-a")
        assert len(dels) == 2

    def test_get_grantor_delegations_empty(self, mgr):
        dels = mgr.get_grantor_delegations("agent-nobody")
        assert dels == []


# ═══════════════════════════════════════════════════════════════════════════════
# cleanup_expired()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCleanupExpired:
    def test_cleanup_marks_expired(self, mgr):
        from core.delegation import CapabilityDelegation, DelegationStatus
        now = datetime.now(timezone.utc)
        d = CapabilityDelegation(
            delegation_id="del-exp-001",
            grantor_id="agent-a",
            grantee_id="agent-b",
            capability="filesystem.read:/data/*",
            constraints={},
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
        )
        mgr._delegations["del-exp-001"] = d
        count = mgr.cleanup_expired()
        assert count >= 1
        assert mgr._delegations["del-exp-001"].status == DelegationStatus.EXPIRED

    def test_cleanup_does_not_affect_active(self, mgr):
        _, _, did = mgr.delegate("agent-a", "agent-b",
                                  "filesystem.read:/data/*", CAPS)
        count = mgr.cleanup_expired()
        assert mgr._delegations[did].status.value == "active"

    def test_cleanup_cascades_to_children(self, mgr):
        from core.delegation import CapabilityDelegation, DelegationStatus
        now = datetime.now(timezone.utc)
        parent = CapabilityDelegation(
            delegation_id="del-exp-parent",
            grantor_id="agent-a",
            grantee_id="agent-b",
            capability="filesystem.read:/data/*",
            constraints={},
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
        )
        child = CapabilityDelegation(
            delegation_id="del-exp-child",
            grantor_id="agent-b",
            grantee_id="agent-c",
            capability="filesystem.read:/data/*",
            constraints={},
            created_at=now - timedelta(hours=2),
            expires_at=now + timedelta(hours=1),
            parent_delegation_id="del-exp-parent",
        )
        mgr._delegations["del-exp-parent"] = parent
        mgr._delegations["del-exp-child"] = child
        mgr.cleanup_expired()
        assert mgr._delegations["del-exp-child"].status == DelegationStatus.EXPIRED

    def test_cleanup_returns_zero_when_none_expired(self, mgr):
        _, _, did = mgr.delegate("agent-a", "agent-b",
                                  "filesystem.read:/data/*", CAPS)
        count = mgr.cleanup_expired()
        assert count == 0


# ═══════════════════════════════════════════════════════════════════════════════
# get_delegation_stats()
# ═══════════════════════════════════════════════════════════════════════════════

class TestDelegationStats:
    def test_stats_active_count(self, mgr):
        mgr.delegate("agent-a", "agent-b", "filesystem.read:/data/*", CAPS)
        mgr.delegate("agent-a", "agent-c", "filesystem.write:/app/*", CAPS)
        stats = mgr.get_delegation_stats()
        assert stats["active"] >= 2

    def test_stats_revoked_count(self, mgr):
        _, _, did = mgr.delegate("agent-a", "agent-b",
                                  "filesystem.read:/data/*", CAPS)
        mgr.revoke(did, "admin", "test")
        stats = mgr.get_delegation_stats()
        assert stats["revoked"] >= 1

    def test_stats_empty_manager(self, mgr):
        stats = mgr.get_delegation_stats()
        assert stats["active"] == 0
        assert stats["revoked"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# load_from_redis() — no Redis available
# ═══════════════════════════════════════════════════════════════════════════════

class TestLoadFromRedis:
    def test_load_with_no_redis_returns_zero(self, mgr):
        count = mgr.load_from_redis()
        assert count == 0

    def test_delegation_ids_by_grantor(self, mgr):
        _, _, did = mgr.delegate("agent-a", "agent-b",
                                  "filesystem.read:/data/*", CAPS)
        ids = mgr.get_delegation_ids_by_grantor("agent-a")
        assert did in ids

    def test_delegation_ids_by_grantee(self, mgr):
        _, _, did = mgr.delegate("agent-a", "agent-b",
                                  "filesystem.read:/data/*", CAPS)
        ids = mgr.get_delegation_ids_by_grantee("agent-b")
        assert did in ids
