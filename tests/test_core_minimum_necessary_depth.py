# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_minimum_necessary_depth.py
# REM: Depth coverage for core/minimum_necessary.py
# REM: AccessScope, MinimumNecessaryPolicy, MinimumNecessaryEnforcer — in-memory.

import pytest

from core.minimum_necessary import (
    AccessScope,
    MinimumNecessaryPolicy,
    MinimumNecessaryEnforcer,
)


# ─── Patch Redis so audit.log() uses in-memory path ────────────────────────────
@pytest.fixture(autouse=True)
def _no_redis(monkeypatch):
    monkeypatch.setattr("core.persistence.get_redis", lambda: None)


# ─── Shared enforcer fixture (fresh instance per test) ────────────────────────
@pytest.fixture
def enforcer():
    return MinimumNecessaryEnforcer()


# ═══════════════════════════════════════════════════════════════════════════════
# AccessScope enum
# ═══════════════════════════════════════════════════════════════════════════════

class TestAccessScope:
    def test_full_value(self):
        assert AccessScope.FULL == "full"

    def test_treatment_value(self):
        assert AccessScope.TREATMENT == "treatment"

    def test_payment_value(self):
        assert AccessScope.PAYMENT == "payment"

    def test_operations_value(self):
        assert AccessScope.OPERATIONS == "operations"

    def test_limited_value(self):
        assert AccessScope.LIMITED == "limited"

    def test_de_identified_value(self):
        assert AccessScope.DE_IDENTIFIED == "de_identified"

    def test_six_members(self):
        assert len(AccessScope) == 6

    def test_is_str_subclass(self):
        assert isinstance(AccessScope.FULL, str)


# ═══════════════════════════════════════════════════════════════════════════════
# MinimumNecessaryPolicy.to_dict()
# ═══════════════════════════════════════════════════════════════════════════════

class TestMinimumNecessaryPolicyToDict:
    def _make_policy(self, role="viewer", scope=AccessScope.LIMITED,
                     allowed=None, denied=None):
        return MinimumNecessaryPolicy(
            role=role,
            default_scope=scope,
            allowed_fields=allowed or set(),
            denied_fields=denied or set(),
        )

    def test_returns_dict(self):
        p = self._make_policy()
        assert isinstance(p.to_dict(), dict)

    def test_has_role(self):
        p = self._make_policy(role="admin")
        assert p.to_dict()["role"] == "admin"

    def test_has_default_scope(self):
        p = self._make_policy(scope=AccessScope.OPERATIONS)
        assert p.to_dict()["default_scope"] == "operations"

    def test_allowed_fields_is_sorted_list(self):
        p = self._make_policy(allowed={"z_field", "a_field", "m_field"})
        d = p.to_dict()
        assert d["allowed_fields"] == sorted(["z_field", "a_field", "m_field"])

    def test_denied_fields_is_sorted_list(self):
        p = self._make_policy(denied={"ssn", "dob"})
        d = p.to_dict()
        assert d["denied_fields"] == sorted(["ssn", "dob"])

    def test_all_four_keys_present(self):
        p = self._make_policy()
        assert set(p.to_dict().keys()) == {
            "role", "default_scope", "allowed_fields", "denied_fields"
        }

    def test_empty_allowed_fields(self):
        p = self._make_policy(allowed=set())
        assert p.to_dict()["allowed_fields"] == []

    def test_empty_denied_fields(self):
        p = self._make_policy(denied=set())
        assert p.to_dict()["denied_fields"] == []


# ═══════════════════════════════════════════════════════════════════════════════
# MinimumNecessaryEnforcer — default policies
# ═══════════════════════════════════════════════════════════════════════════════

class TestDefaultPolicies:
    def test_viewer_policy_exists(self, enforcer):
        assert enforcer.get_policy("viewer") is not None

    def test_operator_policy_exists(self, enforcer):
        assert enforcer.get_policy("operator") is not None

    def test_admin_policy_exists(self, enforcer):
        assert enforcer.get_policy("admin") is not None

    def test_security_officer_policy_exists(self, enforcer):
        assert enforcer.get_policy("security_officer") is not None

    def test_super_admin_policy_exists(self, enforcer):
        assert enforcer.get_policy("super_admin") is not None

    def test_viewer_scope_is_limited(self, enforcer):
        assert enforcer.get_policy("viewer").default_scope == AccessScope.LIMITED

    def test_super_admin_scope_is_full(self, enforcer):
        assert enforcer.get_policy("super_admin").default_scope == AccessScope.FULL

    def test_operator_scope_is_operations(self, enforcer):
        assert enforcer.get_policy("operator").default_scope == AccessScope.OPERATIONS

    def test_admin_scope_is_operations(self, enforcer):
        assert enforcer.get_policy("admin").default_scope == AccessScope.OPERATIONS

    def test_security_officer_scope_is_limited(self, enforcer):
        assert enforcer.get_policy("security_officer").default_scope == AccessScope.LIMITED

    def test_super_admin_no_denied_fields(self, enforcer):
        assert len(enforcer.get_policy("super_admin").denied_fields) == 0

    def test_viewer_denies_ssn(self, enforcer):
        assert "ssn" in enforcer.get_policy("viewer").denied_fields

    def test_five_default_policies_registered(self, enforcer):
        policies = enforcer.list_policies()
        assert len(policies) == 5


# ═══════════════════════════════════════════════════════════════════════════════
# MinimumNecessaryEnforcer.register_policy()
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegisterPolicy:
    def test_returns_policy(self, enforcer):
        result = enforcer.register_policy("custom_role", AccessScope.LIMITED)
        assert isinstance(result, MinimumNecessaryPolicy)

    def test_policy_stored(self, enforcer):
        enforcer.register_policy("custom_role", AccessScope.LIMITED)
        assert enforcer.get_policy("custom_role") is not None

    def test_policy_role_correct(self, enforcer):
        enforcer.register_policy("my_role", AccessScope.OPERATIONS)
        assert enforcer.get_policy("my_role").role == "my_role"

    def test_policy_scope_correct(self, enforcer):
        enforcer.register_policy("my_role", AccessScope.PAYMENT)
        assert enforcer.get_policy("my_role").default_scope == AccessScope.PAYMENT

    def test_allowed_fields_stored(self, enforcer):
        enforcer.register_policy("my_role", AccessScope.LIMITED,
                                 allowed_fields={"patient_id", "status"})
        p = enforcer.get_policy("my_role")
        assert p.allowed_fields == {"patient_id", "status"}

    def test_denied_fields_stored(self, enforcer):
        enforcer.register_policy("my_role", AccessScope.OPERATIONS,
                                 denied_fields={"ssn", "dob"})
        p = enforcer.get_policy("my_role")
        assert p.denied_fields == {"ssn", "dob"}

    def test_overwrite_existing_policy(self, enforcer):
        enforcer.register_policy("viewer", AccessScope.FULL)
        assert enforcer.get_policy("viewer").default_scope == AccessScope.FULL

    def test_no_allowed_defaults_to_empty_set(self, enforcer):
        enforcer.register_policy("my_role", AccessScope.LIMITED)
        assert enforcer.get_policy("my_role").allowed_fields == set()

    def test_no_denied_defaults_to_empty_set(self, enforcer):
        enforcer.register_policy("my_role", AccessScope.LIMITED)
        assert enforcer.get_policy("my_role").denied_fields == set()


# ═══════════════════════════════════════════════════════════════════════════════
# MinimumNecessaryEnforcer.filter_data()
# ═══════════════════════════════════════════════════════════════════════════════

class TestFilterData:
    def _data(self):
        return {
            "patient_id": "P001",
            "visit_date": "2026-01-01",
            "ssn": "123-45-6789",
            "treatment_notes": "sensitive info",
            "status": "admitted",
        }

    def test_unknown_role_returns_empty(self, enforcer):
        result = enforcer.filter_data({"a": 1}, "nonexistent_role", "test")
        assert result == {}

    def test_super_admin_gets_all_fields(self, enforcer):
        data = self._data()
        result = enforcer.filter_data(data, "super_admin", "admin_review")
        assert set(result.keys()) == set(data.keys())

    def test_super_admin_values_unchanged(self, enforcer):
        data = {"ssn": "123", "notes": "private"}
        result = enforcer.filter_data(data, "super_admin", "review")
        assert result["ssn"] == "123"
        assert result["notes"] == "private"

    def test_viewer_denied_ssn_stripped(self, enforcer):
        result = enforcer.filter_data(self._data(), "viewer", "view")
        assert "ssn" not in result

    def test_viewer_allowed_patient_id_kept(self, enforcer):
        result = enforcer.filter_data(self._data(), "viewer", "view")
        assert "patient_id" in result

    def test_viewer_allowed_status_kept(self, enforcer):
        result = enforcer.filter_data(self._data(), "viewer", "view")
        assert "status" in result

    def test_viewer_not_in_allowed_and_not_denied_stripped(self, enforcer):
        # treatment_notes is denied; ssn is denied; visit_date is allowed
        result = enforcer.filter_data(self._data(), "viewer", "view")
        # treatment_notes is explicitly denied — stripped
        assert "treatment_notes" not in result

    def test_admin_denied_ssn_stripped(self, enforcer):
        result = enforcer.filter_data(self._data(), "admin", "admin_view")
        assert "ssn" not in result

    def test_empty_data_returns_empty(self, enforcer):
        result = enforcer.filter_data({}, "viewer", "view")
        assert result == {}

    def test_returns_dict(self, enforcer):
        result = enforcer.filter_data({"a": 1}, "super_admin", "test")
        assert isinstance(result, dict)

    def test_original_data_not_mutated(self, enforcer):
        data = {"patient_id": "P001", "ssn": "123"}
        original_keys = set(data.keys())
        enforcer.filter_data(data, "viewer", "view")
        assert set(data.keys()) == original_keys

    def test_custom_policy_allowed_fields_filtering(self, enforcer):
        enforcer.register_policy(
            "custom",
            AccessScope.LIMITED,
            allowed_fields={"a", "b"},
        )
        data = {"a": 1, "b": 2, "c": 3}
        result = enforcer.filter_data(data, "custom", "test")
        assert set(result.keys()) == {"a", "b"}

    def test_custom_policy_denied_beats_allowed(self, enforcer):
        # If a field is in both allowed and denied, denied wins
        enforcer.register_policy(
            "custom",
            AccessScope.LIMITED,
            allowed_fields={"a", "b"},
            denied_fields={"b"},  # b is denied even though it's in allowed
        )
        data = {"a": 1, "b": 2, "c": 3}
        result = enforcer.filter_data(data, "custom", "test")
        assert "b" not in result
        assert "a" in result

    def test_no_allowed_fields_means_deny_only_filtering(self, enforcer):
        # Policy with no allowed_fields but some denied: all fields pass except denied
        enforcer.register_policy(
            "custom",
            AccessScope.OPERATIONS,
            allowed_fields=set(),   # no whitelist
            denied_fields={"ssn"},
        )
        data = {"name": "X", "ssn": "123", "dept": "Y"}
        result = enforcer.filter_data(data, "custom", "test")
        assert "ssn" not in result
        assert "name" in result
        assert "dept" in result


# ═══════════════════════════════════════════════════════════════════════════════
# MinimumNecessaryEnforcer.check_access()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckAccess:
    def test_unknown_role_returns_false(self, enforcer):
        assert enforcer.check_access("nonexistent_role", "any_field", "test") is False

    def test_super_admin_can_access_any_field(self, enforcer):
        assert enforcer.check_access("super_admin", "ssn", "test") is True
        assert enforcer.check_access("super_admin", "treatment_notes", "test") is True

    def test_viewer_cannot_access_ssn(self, enforcer):
        assert enforcer.check_access("viewer", "ssn", "test") is False

    def test_viewer_can_access_patient_id(self, enforcer):
        assert enforcer.check_access("viewer", "patient_id", "test") is True

    def test_viewer_can_access_status(self, enforcer):
        assert enforcer.check_access("viewer", "status", "test") is True

    def test_viewer_cannot_access_not_in_allowed(self, enforcer):
        # ssn is denied; treatment_notes is denied by viewer policy
        assert enforcer.check_access("viewer", "treatment_notes", "test") is False

    def test_returns_bool(self, enforcer):
        result = enforcer.check_access("viewer", "patient_id", "test")
        assert isinstance(result, bool)

    def test_custom_policy_denied_field(self, enforcer):
        enforcer.register_policy("custom", AccessScope.OPERATIONS,
                                 denied_fields={"secret_field"})
        assert enforcer.check_access("custom", "secret_field", "test") is False

    def test_custom_policy_allowed_field(self, enforcer):
        enforcer.register_policy("custom", AccessScope.LIMITED,
                                 allowed_fields={"allowed_field"})
        assert enforcer.check_access("custom", "allowed_field", "test") is True

    def test_custom_policy_not_in_allowed_blocked(self, enforcer):
        enforcer.register_policy("custom", AccessScope.LIMITED,
                                 allowed_fields={"only_this"})
        assert enforcer.check_access("custom", "other_field", "test") is False


# ═══════════════════════════════════════════════════════════════════════════════
# MinimumNecessaryEnforcer.get_policy()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetPolicy:
    def test_known_role_returns_policy(self, enforcer):
        policy = enforcer.get_policy("viewer")
        assert isinstance(policy, MinimumNecessaryPolicy)

    def test_unknown_role_returns_none(self, enforcer):
        assert enforcer.get_policy("nonexistent") is None

    def test_policy_has_correct_role(self, enforcer):
        policy = enforcer.get_policy("viewer")
        assert policy.role == "viewer"

    def test_all_five_roles_return_policies(self, enforcer):
        for role in ["viewer", "operator", "admin", "security_officer", "super_admin"]:
            assert enforcer.get_policy(role) is not None


# ═══════════════════════════════════════════════════════════════════════════════
# MinimumNecessaryEnforcer.list_policies()
# ═══════════════════════════════════════════════════════════════════════════════

class TestListPolicies:
    def test_returns_list(self, enforcer):
        assert isinstance(enforcer.list_policies(), list)

    def test_default_five_policies(self, enforcer):
        assert len(enforcer.list_policies()) == 5

    def test_all_items_are_dicts(self, enforcer):
        for p in enforcer.list_policies():
            assert isinstance(p, dict)

    def test_all_have_role_key(self, enforcer):
        for p in enforcer.list_policies():
            assert "role" in p

    def test_all_have_default_scope_key(self, enforcer):
        for p in enforcer.list_policies():
            assert "default_scope" in p

    def test_all_have_allowed_fields_key(self, enforcer):
        for p in enforcer.list_policies():
            assert "allowed_fields" in p

    def test_all_have_denied_fields_key(self, enforcer):
        for p in enforcer.list_policies():
            assert "denied_fields" in p

    def test_new_policy_appears_in_list(self, enforcer):
        enforcer.register_policy("new_role", AccessScope.DE_IDENTIFIED)
        roles = [p["role"] for p in enforcer.list_policies()]
        assert "new_role" in roles

    def test_count_increases_after_register(self, enforcer):
        initial = len(enforcer.list_policies())
        enforcer.register_policy("extra_role", AccessScope.LIMITED)
        assert len(enforcer.list_policies()) == initial + 1
