# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_approval_depth.py
# REM: Depth coverage for core/approval.py
# REM: Enums, ApprovalGate CRUD and decisions — all pure in-memory.

import pytest
from datetime import datetime, timezone

from core.approval import (
    DEFAULT_APPROVAL_RULES,
    ApprovalGate,
    ApprovalPriority,
    ApprovalRule,
    ApprovalStatus,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Enum tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestApprovalStatus:
    def test_pending(self):
        assert ApprovalStatus.PENDING == "pending"

    def test_approved(self):
        assert ApprovalStatus.APPROVED == "approved"

    def test_rejected(self):
        assert ApprovalStatus.REJECTED == "rejected"

    def test_expired(self):
        assert ApprovalStatus.EXPIRED == "expired"

    def test_cancelled(self):
        assert ApprovalStatus.CANCELLED == "cancelled"

    def test_more_info_requested(self):
        assert ApprovalStatus.MORE_INFO_REQUESTED == "more_info_requested"

    def test_all_unique(self):
        vals = [s.value for s in ApprovalStatus]
        assert len(vals) == len(set(vals))


class TestApprovalPriority:
    def test_low(self):
        assert ApprovalPriority.LOW == "low"

    def test_normal(self):
        assert ApprovalPriority.NORMAL == "normal"

    def test_high(self):
        assert ApprovalPriority.HIGH == "high"

    def test_urgent(self):
        assert ApprovalPriority.URGENT == "urgent"


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT_APPROVAL_RULES
# ═══════════════════════════════════════════════════════════════════════════════

class TestDefaultApprovalRules:
    def test_rules_is_non_empty_list(self):
        assert isinstance(DEFAULT_APPROVAL_RULES, list)
        assert len(DEFAULT_APPROVAL_RULES) > 0

    def test_filesystem_delete_rule_exists(self):
        rule_ids = [r.rule_id for r in DEFAULT_APPROVAL_RULES]
        assert "rule-filesystem-delete" in rule_ids

    def test_anomaly_rule_exists(self):
        rule_ids = [r.rule_id for r in DEFAULT_APPROVAL_RULES]
        assert "rule-anomaly-flagged" in rule_ids

    def test_all_rules_have_rule_id(self):
        for r in DEFAULT_APPROVAL_RULES:
            assert r.rule_id

    def test_all_rules_enabled_by_default(self):
        for r in DEFAULT_APPROVAL_RULES:
            assert r.enabled is True


# ═══════════════════════════════════════════════════════════════════════════════
# ApprovalGate fixture
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def gate():
    return ApprovalGate()


def _make_rule(rule_id="test-rule", action_pattern="test.*", conditions=None, timeout_seconds=60):
    return ApprovalRule(
        rule_id=rule_id,
        name="Test Rule",
        description="Test",
        action_pattern=action_pattern,
        conditions=conditions or [],
        priority=ApprovalPriority.NORMAL,
        timeout_seconds=timeout_seconds,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# add_rule() / remove_rule()
# ═══════════════════════════════════════════════════════════════════════════════

class TestAddRemoveRule:
    def test_add_rule_stored(self, gate):
        rule = _make_rule("new-rule")
        gate.add_rule(rule)
        assert "new-rule" in gate._rules

    def test_remove_existing_rule_returns_true(self, gate):
        gate.add_rule(_make_rule("new-rule"))
        assert gate.remove_rule("new-rule") is True

    def test_remove_nonexistent_returns_false(self, gate):
        assert gate.remove_rule("does-not-exist") is False

    def test_remove_clears_rule(self, gate):
        gate.add_rule(_make_rule("new-rule"))
        gate.remove_rule("new-rule")
        assert "new-rule" not in gate._rules


# ═══════════════════════════════════════════════════════════════════════════════
# check_requires_approval()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckRequiresApproval:
    def test_no_matching_rule_returns_none(self, gate):
        # Remove all rules first
        gate._rules.clear()
        result = gate.check_requires_approval("any-agent", "any-action", {})
        assert result is None

    def test_matching_action_pattern_returns_rule(self, gate):
        gate._rules.clear()
        rule = _make_rule("del-rule", action_pattern="filesystem.delete*", conditions=[])
        gate.add_rule(rule)
        result = gate.check_requires_approval("agent", "filesystem.delete_file", {})
        assert result is not None
        assert result.rule_id == "del-rule"

    def test_disabled_rule_skipped(self, gate):
        gate._rules.clear()
        rule = ApprovalRule(
            rule_id="disabled-rule",
            name="Disabled",
            description="Disabled",
            action_pattern="*",
            enabled=False,
        )
        gate.add_rule(rule)
        result = gate.check_requires_approval("agent", "any_action", {})
        assert result is None

    def test_agent_pattern_no_match_skipped(self, gate):
        gate._rules.clear()
        rule = ApprovalRule(
            rule_id="specific-rule",
            name="Specific",
            description="Only matches openclaw agents",
            agent_pattern="openclaw:*",
            action_pattern="*",
        )
        gate.add_rule(rule)
        result = gate.check_requires_approval("other-agent", "any_action", {})
        assert result is None

    def test_condition_first_agent_action(self, gate):
        gate._rules.clear()
        rule = _make_rule("first-action-rule", action_pattern="*", conditions=["first_agent_action"])
        gate.add_rule(rule)
        # Unknown agent → condition met
        result = gate.check_requires_approval("brand-new-agent-xyz", "do_something", {})
        assert result is not None

    def test_condition_first_agent_action_known_agent_skipped(self, gate):
        gate._rules.clear()
        rule = _make_rule("first-action-rule", action_pattern="*", conditions=["first_agent_action"])
        gate.add_rule(rule)
        gate._known_agents.add("known-agent")
        result = gate.check_requires_approval("known-agent", "do_something", {})
        assert result is None

    def test_condition_anomaly_flagged(self, gate):
        gate._rules.clear()
        rule = _make_rule("anomaly-rule", action_pattern="*", conditions=["anomaly_flagged"])
        gate.add_rule(rule)
        result = gate.check_requires_approval("agent", "action", {}, context={"anomaly_flagged": True})
        assert result is not None

    def test_condition_anomaly_not_flagged(self, gate):
        gate._rules.clear()
        rule = _make_rule("anomaly-rule", action_pattern="*", conditions=["anomaly_flagged"])
        gate.add_rule(rule)
        result = gate.check_requires_approval("agent", "action", {}, context={"anomaly_flagged": False})
        assert result is None

    def test_condition_value_above_threshold(self, gate):
        gate._rules.clear()
        rule = _make_rule("value-rule", action_pattern="*", conditions=["value_above_threshold:100"])
        gate.add_rule(rule)
        result = gate.check_requires_approval("agent", "action", {"value": 200})
        assert result is not None

    def test_condition_value_below_threshold(self, gate):
        gate._rules.clear()
        rule = _make_rule("value-rule", action_pattern="*", conditions=["value_above_threshold:100"])
        gate.add_rule(rule)
        result = gate.check_requires_approval("agent", "action", {"value": 50})
        assert result is None

    def test_condition_first_time_domain(self, gate):
        gate._rules.clear()
        rule = _make_rule("domain-rule", action_pattern="external.*", conditions=["first_time_domain"])
        gate.add_rule(rule)
        result = gate.check_requires_approval(
            "agent", "external.get", {}, context={"domain": "new-domain.com"}
        )
        assert result is not None

    def test_condition_known_domain_skipped(self, gate):
        gate._rules.clear()
        rule = _make_rule("domain-rule", action_pattern="external.*", conditions=["first_time_domain"])
        gate.add_rule(rule)
        gate._known_domains.add("known-domain.com")
        result = gate.check_requires_approval(
            "agent", "external.get", {}, context={"domain": "known-domain.com"}
        )
        assert result is None

    def test_condition_scope_expansion(self, gate):
        gate._rules.clear()
        rule = _make_rule("scope-rule", action_pattern="*", conditions=["scope_expansion"])
        gate.add_rule(rule)
        result = gate.check_requires_approval(
            "agent", "identity.credential_update",
            {"old_scopes": ["read"], "new_scopes": ["read", "write"]}
        )
        assert result is not None

    def test_condition_no_scope_expansion(self, gate):
        gate._rules.clear()
        rule = _make_rule("scope-rule", action_pattern="*", conditions=["scope_expansion"])
        gate.add_rule(rule)
        result = gate.check_requires_approval(
            "agent", "identity.credential_update",
            {"old_scopes": ["read", "write"], "new_scopes": ["read"]}
        )
        assert result is None


# ═══════════════════════════════════════════════════════════════════════════════
# create_request()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCreateRequest:
    def test_creates_request_with_appr_prefix(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "Testing", {}, rule)
        assert req.request_id.startswith("APPR-")

    def test_request_stored_in_pending(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "Testing", {}, rule)
        assert req.request_id in gate._pending_requests

    def test_request_status_pending(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "Testing", {}, rule)
        assert req.status == ApprovalStatus.PENDING

    def test_request_has_expiry(self, gate):
        rule = _make_rule(timeout_seconds=3600)
        req = gate.create_request("agent-001", "test_action", "Testing", {}, rule)
        assert req.expires_at is not None

    def test_request_risk_factors_included(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule, risk_factors=["data_loss"])
        assert "data_loss" in req.risk_factors

    def test_notification_callback_called(self, gate):
        rule = _make_rule()
        events = []
        gate.register_notification_callback(lambda event, req: events.append(event))
        gate.create_request("agent-001", "test_action", "T", {}, rule)
        assert "new_request" in events


# ═══════════════════════════════════════════════════════════════════════════════
# approve()
# ═══════════════════════════════════════════════════════════════════════════════

class TestApprove:
    def test_approve_pending_returns_true(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        result = gate.approve(req.request_id, "admin", "looks good")
        assert result is True

    def test_approve_sets_status_approved(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        gate.approve(req.request_id, "admin")
        completed = gate._completed_requests[req.request_id]
        assert completed.status == ApprovalStatus.APPROVED

    def test_approve_sets_decided_by(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        gate.approve(req.request_id, "admin-user")
        completed = gate._completed_requests[req.request_id]
        assert completed.decided_by == "admin-user"

    def test_approve_moves_to_completed(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        gate.approve(req.request_id, "admin")
        assert req.request_id not in gate._pending_requests
        assert req.request_id in gate._completed_requests

    def test_approve_adds_agent_to_known(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-new-known", "test_action", "T", {}, rule)
        gate.approve(req.request_id, "admin")
        assert "agent-new-known" in gate._known_agents

    def test_approve_nonexistent_returns_false(self, gate):
        assert gate.approve("APPR-NONEXISTENT", "admin") is False

    def test_approve_notes_stored(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        gate.approve(req.request_id, "admin", "approved with conditions")
        completed = gate._completed_requests[req.request_id]
        assert completed.decision_notes == "approved with conditions"


# ═══════════════════════════════════════════════════════════════════════════════
# reject()
# ═══════════════════════════════════════════════════════════════════════════════

class TestReject:
    def test_reject_pending_returns_true(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        assert gate.reject(req.request_id, "admin", "too risky") is True

    def test_reject_sets_status_rejected(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        gate.reject(req.request_id, "admin")
        completed = gate._completed_requests[req.request_id]
        assert completed.status == ApprovalStatus.REJECTED

    def test_reject_moves_to_completed(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        gate.reject(req.request_id, "admin")
        assert req.request_id not in gate._pending_requests
        assert req.request_id in gate._completed_requests

    def test_reject_nonexistent_returns_false(self, gate):
        assert gate.reject("APPR-NONEXISTENT", "admin") is False

    def test_reject_sets_decided_by(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        gate.reject(req.request_id, "security-team")
        completed = gate._completed_requests[req.request_id]
        assert completed.decided_by == "security-team"


# ═══════════════════════════════════════════════════════════════════════════════
# request_more_info()
# ═══════════════════════════════════════════════════════════════════════════════

class TestRequestMoreInfo:
    def test_returns_true_for_pending(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        result = gate.request_more_info(req.request_id, "admin", ["What is the purpose?"])
        assert result is True

    def test_sets_status_more_info_requested(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        gate.request_more_info(req.request_id, "admin", ["Question 1?"])
        assert req.status == ApprovalStatus.MORE_INFO_REQUESTED

    def test_questions_in_decision_notes(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        gate.request_more_info(req.request_id, "admin", ["Why?", "What?"])
        assert "Why?" in req.decision_notes

    def test_returns_false_for_nonexistent(self, gate):
        assert gate.request_more_info("APPR-NONEXISTENT", "admin", ["Q?"]) is False


# ═══════════════════════════════════════════════════════════════════════════════
# get_approval_status()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetApprovalStatus:
    def test_pending_request_status(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        status = gate.get_approval_status(req.request_id)
        assert status is not None
        assert status["status"] == "pending"
        assert status["request_id"] == req.request_id

    def test_completed_request_status_after_approve(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        gate.approve(req.request_id, "admin")
        status = gate.get_approval_status(req.request_id)
        assert status is not None
        assert status["status"] == "approved"

    def test_completed_request_status_after_reject(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "test_action", "T", {}, rule)
        gate.reject(req.request_id, "admin")
        status = gate.get_approval_status(req.request_id)
        assert status["status"] == "rejected"

    def test_nonexistent_request_returns_none(self, gate):
        assert gate.get_approval_status("APPR-NONEXISTENT") is None

    def test_status_has_agent_id(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-status-test", "test_action", "T", {}, rule)
        status = gate.get_approval_status(req.request_id)
        assert status["agent_id"] == "agent-status-test"

    def test_status_has_action(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "my_special_action", "T", {}, rule)
        status = gate.get_approval_status(req.request_id)
        assert status["action"] == "my_special_action"


# ═══════════════════════════════════════════════════════════════════════════════
# get_pending_requests()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetPendingRequests:
    def test_returns_all_pending(self, gate):
        rule = _make_rule()
        gate.create_request("agent-001", "action1", "T", {}, rule)
        gate.create_request("agent-002", "action2", "T", {}, rule)
        pending = gate.get_pending_requests()
        assert len(pending) >= 2

    def test_filter_by_agent_id(self, gate):
        rule = _make_rule()
        gate.create_request("agent-filter-001", "action", "T", {}, rule)
        gate.create_request("agent-filter-002", "action", "T", {}, rule)
        pending = gate.get_pending_requests(agent_id="agent-filter-001")
        assert all(r.agent_id == "agent-filter-001" for r in pending)

    def test_filter_by_priority(self, gate):
        rule_normal = _make_rule("normal-rule")
        rule_urgent = ApprovalRule(
            rule_id="urgent-rule", name="Urgent", description="Urgent",
            action_pattern="urgent.*", priority=ApprovalPriority.URGENT,
        )
        gate.add_rule(rule_urgent)
        gate.create_request("agent-001", "urgent.action", "T", {}, rule_urgent)
        gate.create_request("agent-001", "normal_action", "T", {}, rule_normal)
        urgent_only = gate.get_pending_requests(priority=ApprovalPriority.URGENT)
        assert all(r.priority == ApprovalPriority.URGENT for r in urgent_only)

    def test_approved_request_not_in_pending(self, gate):
        rule = _make_rule()
        req = gate.create_request("agent-001", "action", "T", {}, rule)
        gate.approve(req.request_id, "admin")
        pending_ids = [r.request_id for r in gate.get_pending_requests()]
        assert req.request_id not in pending_ids

    def test_sorted_urgent_first(self, gate):
        rule_low = ApprovalRule(
            rule_id="rule-low", name="Low", description="Low",
            action_pattern="low.*", priority=ApprovalPriority.LOW,
        )
        rule_urgent = ApprovalRule(
            rule_id="rule-urgent-prio", name="Urgent", description="Urgent",
            action_pattern="urgent2.*", priority=ApprovalPriority.URGENT,
        )
        gate.add_rule(rule_low)
        gate.add_rule(rule_urgent)
        gate.create_request("agent", "low.action", "T", {}, rule_low)
        gate.create_request("agent", "urgent2.action", "T", {}, rule_urgent)
        pending = gate.get_pending_requests()
        priorities = [r.priority for r in pending]
        urgent_idx = next((i for i, p in enumerate(priorities) if p == ApprovalPriority.URGENT), None)
        low_idx = next((i for i, p in enumerate(priorities) if p == ApprovalPriority.LOW), None)
        if urgent_idx is not None and low_idx is not None:
            assert urgent_idx < low_idx
