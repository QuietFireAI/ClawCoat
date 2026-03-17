# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_coverage_boost5.py
# REM: Coverage tests for trust_levels.py, approval.py, rate_limiting.py

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock


# ═══════════════════════════════════════════════════════════════════════════════
# core/trust_levels.py — AgentTrustRecord data methods + TrustLevelManager
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgentTrustRecord:
    def _make_record(self, level="QUARANTINE", **kwargs):
        from core.trust_levels import AgentTrustRecord, AgentTrustLevel
        return AgentTrustRecord(
            agent_id="test_agent",
            trust_level=AgentTrustLevel[level],
            **kwargs
        )

    def test_success_rate_no_actions_returns_zero(self):
        rec = self._make_record()
        assert rec.success_rate() == 0.0

    def test_success_rate_with_actions(self):
        rec = self._make_record(total_actions=10, successful_actions=9)
        assert rec.success_rate() == pytest.approx(0.9)

    def test_period_success_rate_no_actions_returns_one(self):
        rec = self._make_record("CITIZEN")
        assert rec.period_success_rate() == 1.0

    def test_period_success_rate_with_actions(self):
        rec = self._make_record("CITIZEN", period_actions=4, period_successes=3)
        assert rec.period_success_rate() == pytest.approx(0.75)

    def test_reset_period_metrics_zeroes_all(self):
        rec = self._make_record("CITIZEN",
                                period_actions=10, period_successes=8,
                                period_failures=2, period_anomalies=1)
        rec.reset_period_metrics()
        assert rec.period_actions == 0
        assert rec.period_successes == 0
        assert rec.period_failures == 0
        assert rec.period_anomalies == 0

    def test_to_dict_all_keys_present(self):
        rec = self._make_record("RESIDENT")
        d = rec.to_dict()
        for key in ["agent_id", "trust_level", "success_rate", "period_success_rate",
                    "period_actions", "period_anomalies", "reverification_passed"]:
            assert key in d

    def test_to_dict_last_promotion_none_when_not_set(self):
        rec = self._make_record()
        d = rec.to_dict()
        assert d["last_promotion"] is None

    def test_to_dict_last_reverification_isoformat(self):
        now = datetime.now(timezone.utc)
        rec = self._make_record("CITIZEN", last_reverification=now)
        d = rec.to_dict()
        assert d["last_reverification"] == now.isoformat()


class TestTrustLevelManagerRegister:
    def setup_method(self):
        from core.trust_levels import TrustLevelManager
        self.mgr = TrustLevelManager()

    def test_register_agent_default_quarantine(self):
        from core.trust_levels import AgentTrustLevel
        with patch("core.trust_levels.audit"):
            rec = self.mgr.register_agent("rq_agent1")
        assert rec.trust_level == AgentTrustLevel.QUARANTINE
        assert "rq_agent1" in self.mgr._records

    def test_register_agent_skip_quarantine_goes_to_resident(self):
        from core.trust_levels import AgentTrustLevel
        with patch("core.trust_levels.audit"):
            rec = self.mgr.register_agent("rq_skip", skip_quarantine=True)
        assert rec.trust_level == AgentTrustLevel.RESIDENT

    def test_register_agent_explicit_citizen(self):
        from core.trust_levels import AgentTrustLevel
        with patch("core.trust_levels.audit"):
            rec = self.mgr.register_agent("rq_cit", initial_level=AgentTrustLevel.CITIZEN)
        assert rec.trust_level == AgentTrustLevel.CITIZEN

    def test_get_trust_level_registered(self):
        from core.trust_levels import AgentTrustLevel
        with patch("core.trust_levels.audit"):
            self.mgr.register_agent("rq_tl")
        level = self.mgr.get_trust_level("rq_tl")
        assert level == AgentTrustLevel.QUARANTINE

    def test_get_trust_level_unknown_returns_none(self):
        assert self.mgr.get_trust_level("nobody_xyz_9182") is None

    def test_get_constraints_unknown_agent_returns_quarantine_constraints(self):
        from core.trust_levels import TRUST_LEVEL_CONSTRAINTS, AgentTrustLevel
        constraints = self.mgr.get_constraints("nobody_xyz_9182")
        assert constraints.max_actions_per_minute == TRUST_LEVEL_CONSTRAINTS[AgentTrustLevel.QUARANTINE].max_actions_per_minute

    def test_get_constraints_known_resident(self):
        from core.trust_levels import AgentTrustLevel, TRUST_LEVEL_CONSTRAINTS
        with patch("core.trust_levels.audit"):
            self.mgr.register_agent("res_con", initial_level=AgentTrustLevel.RESIDENT)
        constraints = self.mgr.get_constraints("res_con")
        assert constraints == TRUST_LEVEL_CONSTRAINTS[AgentTrustLevel.RESIDENT]

    def test_get_all_records(self):
        with patch("core.trust_levels.audit"):
            self.mgr.register_agent("rec_a")
            self.mgr.register_agent("rec_b")
        records = self.mgr.get_all_records()
        assert len(records) >= 2

    def test_get_agents_by_level(self):
        from core.trust_levels import AgentTrustLevel
        with patch("core.trust_levels.audit"):
            self.mgr.register_agent("lvl_q1", initial_level=AgentTrustLevel.QUARANTINE)
            self.mgr.register_agent("lvl_r1", initial_level=AgentTrustLevel.RESIDENT)
        q_agents = self.mgr.get_agents_by_level(AgentTrustLevel.QUARANTINE)
        assert "lvl_q1" in q_agents
        assert "lvl_r1" not in q_agents


class TestTrustLevelManagerRecordActions:
    def setup_method(self):
        from core.trust_levels import TrustLevelManager, AgentTrustLevel
        self.mgr = TrustLevelManager()
        with patch("core.trust_levels.audit"):
            self.mgr.register_agent("act_agent", initial_level=AgentTrustLevel.RESIDENT)

    def test_record_action_unknown_agent_no_error(self):
        self.mgr.record_action("nobody_xyz", success=True)

    def test_record_action_success_increments_counts(self):
        self.mgr.record_action("act_agent", success=True)
        rec = self.mgr._records["act_agent"]
        assert rec.total_actions == 1
        assert rec.successful_actions == 1
        assert rec.period_actions == 1
        assert rec.period_successes == 1

    def test_record_action_failure_increments_failures(self):
        self.mgr.record_action("act_agent", success=False)
        rec = self.mgr._records["act_agent"]
        assert rec.failed_actions == 1
        assert rec.period_failures == 1

    def test_record_action_anomaly_increments_anomaly_counts(self):
        self.mgr.record_action("act_agent", success=True, triggered_anomaly=True)
        rec = self.mgr._records["act_agent"]
        assert rec.anomalies_triggered == 1
        assert rec.period_anomalies == 1

    def test_record_action_three_anomalies_triggers_auto_demote(self):
        from core.trust_levels import AgentTrustLevel
        with patch("core.trust_levels.audit"):
            for _ in range(3):
                self.mgr.record_action("act_agent", success=False, triggered_anomaly=True)
        rec = self.mgr._records["act_agent"]
        assert rec.trust_level != AgentTrustLevel.RESIDENT

    def test_record_approval_decision_unknown_no_error(self):
        self.mgr.record_approval_decision("nobody_xyz", approved=True)

    def test_record_approval_granted(self):
        self.mgr.record_approval_decision("act_agent", approved=True)
        assert self.mgr._records["act_agent"].approvals_granted == 1

    def test_record_approval_denied(self):
        self.mgr.record_approval_decision("act_agent", approved=False)
        assert self.mgr._records["act_agent"].approvals_denied == 1

    def test_record_five_denials_auto_demote(self):
        from core.trust_levels import AgentTrustLevel
        with patch("core.trust_levels.audit"):
            for _ in range(5):
                self.mgr.record_approval_decision("act_agent", approved=False)
        rec = self.mgr._records["act_agent"]
        assert rec.trust_level != AgentTrustLevel.RESIDENT


class TestTrustLevelManagerPromoteDemote:
    def setup_method(self):
        from core.trust_levels import TrustLevelManager, AgentTrustLevel
        self.mgr = TrustLevelManager()
        with patch("core.trust_levels.audit"):
            self.mgr.register_agent("pd_agent", initial_level=AgentTrustLevel.QUARANTINE)
            self.mgr.register_agent("res_agent", initial_level=AgentTrustLevel.RESIDENT)
            self.mgr.register_agent("apex_agent", initial_level=AgentTrustLevel.AGENT)

    def test_check_promotion_eligibility_unknown_agent(self):
        eligible, reason = self.mgr.check_promotion_eligibility("nobody_xyz_9182")
        assert eligible is False
        assert "not found" in reason.lower()

    def test_check_promotion_eligibility_at_apex(self):
        eligible, reason = self.mgr.check_promotion_eligibility("apex_agent")
        assert eligible is False
        assert "highest" in reason.lower()

    def test_check_promotion_eligibility_not_enough_days(self):
        eligible, reason = self.mgr.check_promotion_eligibility("pd_agent")
        assert eligible is False
        assert "days" in reason.lower()

    def test_check_promotion_eligibility_blocked(self):
        rec = self.mgr._records["pd_agent"]
        rec.promotion_blocked_until = datetime.now(timezone.utc) + timedelta(days=1)
        rec.promotion_blocked_reason = "Test block"
        eligible, reason = self.mgr.check_promotion_eligibility("pd_agent")
        assert eligible is False
        assert "blocked" in reason.lower()

    def test_promote_unknown_agent_returns_false(self):
        success, msg = self.mgr.promote("nobody_xyz_9182", promoted_by="admin")
        assert success is False

    def test_promote_skip_eligibility_check(self):
        from core.trust_levels import AgentTrustLevel
        with patch("core.trust_levels.audit"):
            success, msg = self.mgr.promote("pd_agent", promoted_by="admin", skip_eligibility_check=True)
        assert success is True
        assert self.mgr._records["pd_agent"].trust_level == AgentTrustLevel.PROBATION

    def test_promote_apex_agent_already_at_top(self):
        with patch("core.trust_levels.audit"):
            success, msg = self.mgr.promote("apex_agent", promoted_by="admin", skip_eligibility_check=True)
        assert success is False
        assert "highest" in msg.lower()

    def test_promote_resets_days_at_current_level(self):
        self.mgr._records["pd_agent"].days_at_current_level = 99
        with patch("core.trust_levels.audit"):
            self.mgr.promote("pd_agent", promoted_by="admin", skip_eligibility_check=True)
        assert self.mgr._records["pd_agent"].days_at_current_level == 0

    def test_demote_unknown_agent_returns_false(self):
        success, msg = self.mgr.demote("nobody_xyz_9182", demoted_by="admin", reason="test")
        assert success is False

    def test_demote_at_quarantine_lowest_level(self):
        with patch("core.trust_levels.audit"):
            success, msg = self.mgr.demote("pd_agent", demoted_by="admin", reason="test")
        assert success is False
        assert "lowest" in msg.lower()

    def test_demote_from_resident_to_probation(self):
        from core.trust_levels import AgentTrustLevel
        with patch("core.trust_levels.audit"):
            success, msg = self.mgr.demote("res_agent", demoted_by="admin", reason="Bad behavior")
        assert success is True
        assert self.mgr._records["res_agent"].trust_level == AgentTrustLevel.PROBATION
        assert self.mgr._records["res_agent"].promotion_blocked_until is not None
        assert self.mgr._records["res_agent"].promotion_blocked_reason == "Bad behavior"

    def test_quarantine_unknown_agent_returns_false(self):
        result = self.mgr.quarantine("nobody_xyz_9182", quarantined_by="admin", reason="test")
        assert result is False

    def test_quarantine_from_citizen(self):
        from core.trust_levels import AgentTrustLevel
        with patch("core.trust_levels.audit"):
            self.mgr.register_agent("cit_q_agent", initial_level=AgentTrustLevel.CITIZEN)
            result = self.mgr.quarantine("cit_q_agent", quarantined_by="admin", reason="Breach")
        assert result is True
        assert self.mgr._records["cit_q_agent"].trust_level == AgentTrustLevel.QUARANTINE
        assert "Emergency quarantine" in self.mgr._records["cit_q_agent"].promotion_blocked_reason


class TestTrustLevelManagerReverification:
    def setup_method(self):
        from core.trust_levels import TrustLevelManager, AgentTrustLevel
        self.mgr = TrustLevelManager()
        with patch("core.trust_levels.audit"):
            self.mgr.register_agent("cit_agent", initial_level=AgentTrustLevel.CITIZEN)
            self.mgr.register_agent("q_agent", initial_level=AgentTrustLevel.QUARANTINE)

    def test_needs_reverification_unknown_agent(self):
        needs, _ = self.mgr.needs_reverification("nobody_xyz_9182")
        assert needs is False

    def test_needs_reverification_quarantine_no_config(self):
        needs, reason = self.mgr.needs_reverification("q_agent")
        assert needs is False
        assert "not require" in reason.lower()

    def test_needs_reverification_citizen_no_promotion_not_due(self):
        needs, _ = self.mgr.needs_reverification("cit_agent")
        assert needs is False

    def test_needs_reverification_citizen_past_interval_first_time(self):
        rec = self.mgr._records["cit_agent"]
        rec.last_promotion = datetime.now(timezone.utc) - timedelta(days=10)
        needs, reason = self.mgr.needs_reverification("cit_agent")
        assert needs is True
        assert "initial" in reason.lower()

    def test_needs_reverification_with_recent_reverif_not_due(self):
        rec = self.mgr._records["cit_agent"]
        rec.last_reverification = datetime.now(timezone.utc) - timedelta(days=1)
        needs, _ = self.mgr.needs_reverification("cit_agent")
        assert needs is False

    def test_needs_reverification_with_overdue_reverif(self):
        rec = self.mgr._records["cit_agent"]
        rec.last_reverification = datetime.now(timezone.utc) - timedelta(days=8)
        needs, _ = self.mgr.needs_reverification("cit_agent")
        assert needs is True

    def test_perform_reverification_unknown_agent(self):
        passed, reason, _ = self.mgr.perform_reverification("nobody_xyz_9182")
        assert passed is False
        assert "not found" in reason.lower()

    def test_perform_reverification_quarantine_auto_passes(self):
        passed, reason, _ = self.mgr.perform_reverification("q_agent")
        assert passed is True
        assert "no re-verification required" in reason.lower()

    def test_perform_reverification_citizen_pass_good_metrics(self):
        from core.trust_levels import AgentTrustLevel
        rec = self.mgr._records["cit_agent"]
        rec.period_actions = 30
        rec.period_successes = 30
        rec.period_failures = 0
        rec.period_anomalies = 0
        with patch("core.trust_levels.audit"):
            passed, reason, details = self.mgr.perform_reverification("cit_agent")
        assert passed is True
        assert rec.period_actions == 0  # Reset

    def test_perform_reverification_citizen_fail_low_activity(self):
        from core.trust_levels import AgentTrustLevel
        rec = self.mgr._records["cit_agent"]
        rec.period_actions = 5  # Below min of 20
        rec.period_successes = 5
        rec.period_failures = 0
        rec.period_anomalies = 0
        with patch("core.trust_levels.audit"):
            passed, reason, details = self.mgr.perform_reverification("cit_agent")
        assert passed is False
        assert self.mgr._records["cit_agent"].trust_level != AgentTrustLevel.CITIZEN

    def test_run_system_reverification_returns_summary(self):
        with patch("core.trust_levels.audit"):
            results = self.mgr.run_system_reverification()
        assert isinstance(results["checked"], int)
        assert isinstance(results["passed"], int)
        assert isinstance(results["failed"], int)
        assert "details" in results

    def test_run_system_reverification_counts_agents(self):
        with patch("core.trust_levels.audit"):
            results = self.mgr.run_system_reverification()
        assert results["checked"] >= 2  # cit_agent + q_agent

    def test_get_reverification_status_returns_dict(self):
        status = self.mgr.get_reverification_status()
        assert "total_agents" in status
        assert "agents" in status
        assert isinstance(status["agents"], list)
        assert status["total_agents"] >= 2


# ═══════════════════════════════════════════════════════════════════════════════
# core/approval.py — ApprovalGate
# ═══════════════════════════════════════════════════════════════════════════════

class TestApprovalEnums:
    def test_approval_status_has_all_values(self):
        from core.approval import ApprovalStatus
        names = {s.name for s in ApprovalStatus}
        assert names >= {"PENDING", "APPROVED", "REJECTED", "EXPIRED", "CANCELLED", "MORE_INFO_REQUESTED"}

    def test_approval_priority_has_all_values(self):
        from core.approval import ApprovalPriority
        names = {p.name for p in ApprovalPriority}
        assert names >= {"LOW", "NORMAL", "HIGH", "URGENT"}


class TestApprovalGateSetup:
    def setup_method(self):
        from core.approval import ApprovalGate
        self.gate = ApprovalGate()

    def test_default_rules_loaded(self):
        assert len(self.gate._rules) >= 5

    def test_add_rule(self):
        from core.approval import ApprovalRule
        rule = ApprovalRule(rule_id="tc_rule_add", name="Test Add", description="Add test")
        self.gate.add_rule(rule)
        assert "tc_rule_add" in self.gate._rules

    def test_remove_rule_existing_returns_true(self):
        result = self.gate.remove_rule("rule-filesystem-delete")
        assert result is True
        assert "rule-filesystem-delete" not in self.gate._rules

    def test_remove_rule_nonexistent_returns_false(self):
        result = self.gate.remove_rule("nonexistent_rule_xyz_9182")
        assert result is False

    def test_check_requires_approval_disabled_rule_skipped(self):
        from core.approval import ApprovalRule
        self.gate._rules.clear()
        rule = ApprovalRule(rule_id="tc_disabled", name="Disabled", description="D", enabled=False)
        self.gate.add_rule(rule)
        matched = self.gate.check_requires_approval("any_agent", "any_action", {}, {})
        assert matched is None

    def test_register_notification_callback(self):
        cb = MagicMock()
        self.gate.register_notification_callback(cb)
        assert cb in self.gate._notification_callbacks


class TestApprovalGateConditions:
    def setup_method(self):
        from core.approval import ApprovalGate
        self.gate = ApprovalGate()

    def _eval(self, condition, agent_id="agent1", action="read", payload=None, context=None):
        return self.gate._evaluate_condition(
            condition, agent_id=agent_id, action=action,
            payload=payload or {}, context=context or {}
        )

    def test_first_time_domain_new_domain_true(self):
        assert self._eval("first_time_domain", payload={"domain": "newsite.example.com"}) is True

    def test_first_time_domain_known_domain_false(self):
        self.gate._known_domains.add("known.example.com")
        assert self._eval("first_time_domain", payload={"domain": "known.example.com"}) is False

    def test_first_time_domain_no_domain_false(self):
        assert self._eval("first_time_domain", payload={}) is False

    def test_first_agent_action_new_agent_true(self):
        assert self._eval("first_agent_action", agent_id="brand_new_xyz") is True

    def test_first_agent_action_known_agent_false(self):
        self.gate._known_agents.add("known_old_agent")
        assert self._eval("first_agent_action", agent_id="known_old_agent") is False

    def test_anomaly_flagged_true_when_set(self):
        assert self._eval("anomaly_flagged", context={"anomaly_flagged": True}) is True

    def test_anomaly_flagged_false_when_not_set(self):
        assert self._eval("anomaly_flagged") is False

    def test_value_above_threshold_above(self):
        assert self._eval("value_above_threshold:1000", payload={"value": 5000}) is True

    def test_value_above_threshold_below(self):
        assert self._eval("value_above_threshold:1000", payload={"value": 500}) is False

    def test_value_above_threshold_amount_key(self):
        assert self._eval("value_above_threshold:100", payload={"amount": 200}) is True

    def test_first_did_registration_new_did_true(self):
        assert self._eval("first_did_registration", payload={"did": "did:web:new.example"}) is True

    def test_scope_expansion_new_scopes_true(self):
        result = self._eval("scope_expansion",
                            payload={"old_scopes": ["read"], "new_scopes": ["read", "write"]})
        assert result is True

    def test_scope_expansion_no_new_scopes_false(self):
        result = self._eval("scope_expansion",
                            payload={"old_scopes": ["read", "write"], "new_scopes": ["read"]})
        assert result is False

    def test_unknown_condition_returns_false(self):
        assert self._eval("totally_unknown_condition_xyz_9182") is False


class TestApprovalGateRequests:
    def setup_method(self):
        from core.approval import ApprovalGate, ApprovalRule
        self.gate = ApprovalGate()
        self.gate._rules.clear()
        self.rule = ApprovalRule(
            rule_id="tc_basic_rule",
            name="Test Basic",
            description="Basic test rule",
            action_pattern="*",
            timeout_seconds=3600
        )
        self.gate.add_rule(self.rule)

    def _create(self, agent_id="tc_agent", action="read", **kwargs):
        with patch("core.approval.audit"):
            return self.gate.create_request(
                agent_id=agent_id, action=action,
                description="Test action",
                payload={"key": "value"},
                rule=self.rule, **kwargs
            )

    def test_create_request_id_format(self):
        req = self._create()
        assert req.request_id.startswith("APPR-")

    def test_create_request_stored_in_pending(self):
        req = self._create()
        assert req.request_id in self.gate._pending_requests

    def test_create_request_fires_callbacks(self):
        events = []
        self.gate.register_notification_callback(lambda evt, r: events.append(evt))
        self._create()
        assert "new_request" in events

    def test_create_request_callback_exception_does_not_propagate(self):
        self.gate.register_notification_callback(lambda e, r: (_ for _ in ()).throw(ValueError("oops")))
        # Should not raise — errors in callbacks are swallowed
        req = self._create()
        assert req is not None

    def test_approve_pending_returns_true(self):
        req = self._create()
        with patch("core.approval.audit"):
            result = self.gate.approve(req.request_id, decided_by="admin", notes="OK")
        assert result is True

    def test_approve_sets_status_approved(self):
        from core.approval import ApprovalStatus
        req = self._create()
        with patch("core.approval.audit"):
            self.gate.approve(req.request_id, decided_by="admin")
        assert req.status == ApprovalStatus.APPROVED
        assert req.decided_by == "admin"

    def test_approve_adds_agent_to_known(self):
        req = self._create(agent_id="tc_new_known_agent")
        with patch("core.approval.audit"):
            self.gate.approve(req.request_id, decided_by="admin")
        assert "tc_new_known_agent" in self.gate._known_agents

    def test_approve_with_domain_adds_to_known_domains(self):
        with patch("core.approval.audit"):
            req = self.gate.create_request(
                agent_id="dom_agent", action="external",
                description="External call",
                payload={"domain": "tc.example.com"},
                rule=self.rule
            )
            self.gate.approve(req.request_id, decided_by="admin")
        assert "tc.example.com" in self.gate._known_domains

    def test_approve_moves_to_completed(self):
        req = self._create()
        with patch("core.approval.audit"):
            self.gate.approve(req.request_id, decided_by="admin")
        assert req.request_id not in self.gate._pending_requests
        assert req.request_id in self.gate._completed_requests

    def test_approve_nonexistent_returns_false(self):
        with patch("core.approval.audit"):
            result = self.gate.approve("APPR-NONEXISTENT-XYZ-9182", decided_by="admin")
        assert result is False

    def test_reject_pending_returns_true(self):
        req = self._create()
        with patch("core.approval.audit"):
            result = self.gate.reject(req.request_id, decided_by="admin", notes="Too risky")
        assert result is True

    def test_reject_sets_status_rejected(self):
        from core.approval import ApprovalStatus
        req = self._create()
        with patch("core.approval.audit"):
            self.gate.reject(req.request_id, decided_by="admin")
        assert req.status == ApprovalStatus.REJECTED

    def test_reject_nonexistent_returns_false(self):
        with patch("core.approval.audit"):
            result = self.gate.reject("APPR-NONEXISTENT-XYZ-9182", decided_by="admin")
        assert result is False

    def test_request_more_info_returns_true(self):
        req = self._create()
        result = self.gate.request_more_info(req.request_id, "admin", ["What purpose?"])
        assert result is True

    def test_request_more_info_sets_status(self):
        from core.approval import ApprovalStatus
        req = self._create()
        self.gate.request_more_info(req.request_id, "admin", ["Q1?", "Q2?"])
        assert req.status == ApprovalStatus.MORE_INFO_REQUESTED
        assert "Q1?" in req.decision_notes

    def test_request_more_info_nonexistent_returns_false(self):
        result = self.gate.request_more_info("NONEXISTENT-XYZ-9182", "admin", ["Q?"])
        assert result is False

    def test_get_approval_status_pending(self):
        req = self._create()
        status = self.gate.get_approval_status(req.request_id)
        assert status is not None
        assert status["status"] == "pending"
        assert status["agent_id"] == "tc_agent"
        assert status["action"] == "read"

    def test_get_approval_status_completed_after_approve(self):
        req = self._create()
        with patch("core.approval.audit"):
            self.gate.approve(req.request_id, decided_by="admin")
        status = self.gate.get_approval_status(req.request_id)
        assert status is not None
        assert status["status"] == "approved"

    def test_get_approval_status_nonexistent_returns_none(self):
        status = self.gate.get_approval_status("APPR-TOTALLY-NONEXISTENT-XYZ-9182")
        assert status is None

    def test_get_pending_requests_all(self):
        self._create(agent_id="tc_pa1")
        self._create(agent_id="tc_pa2")
        pending = self.gate.get_pending_requests()
        assert len(pending) >= 2

    def test_get_pending_requests_filter_by_agent(self):
        self._create(agent_id="tc_filter_agent")
        self._create(agent_id="tc_other_agent")
        pending = self.gate.get_pending_requests(agent_id="tc_filter_agent")
        assert all(r.agent_id == "tc_filter_agent" for r in pending)
        assert len(pending) >= 1

    def test_get_pending_requests_filter_by_priority(self):
        from core.approval import ApprovalPriority
        pending = self.gate.get_pending_requests(priority=ApprovalPriority.URGENT)
        assert isinstance(pending, list)

    def test_get_pending_requests_sorted_by_priority(self):
        from core.approval import ApprovalRule, ApprovalPriority
        urgent_rule = ApprovalRule(
            rule_id="tc_urgent_rule", name="Urgent", description="U",
            priority=ApprovalPriority.URGENT, timeout_seconds=60
        )
        self.gate.add_rule(urgent_rule)
        with patch("core.approval.audit"):
            req_normal = self.gate.create_request(
                agent_id="tc_sort_normal", action="read", description="Normal",
                payload={}, rule=self.rule
            )
            req_urgent = self.gate.create_request(
                agent_id="tc_sort_urgent", action="read", description="Urgent",
                payload={}, rule=urgent_rule
            )
        pending = self.gate.get_pending_requests()
        ids = [r.request_id for r in pending]
        assert ids.index(req_urgent.request_id) < ids.index(req_normal.request_id)

    def test_dict_to_request_valid(self):
        from core.approval import ApprovalStatus
        now = datetime.now(timezone.utc)
        data = {
            "request_id": "APPR-DICTTEST001",
            "agent_id": "tc_dict_agent",
            "action": "read",
            "description": "Test",
            "payload": {},
            "priority": "normal",
            "created_at": now.isoformat(),
            "expires_at": None,
            "status": "pending",
        }
        req = self.gate._dict_to_request(data)
        assert req is not None
        assert req.request_id == "APPR-DICTTEST001"

    def test_dict_to_request_invalid_returns_none(self):
        req = self.gate._dict_to_request({"broken": True, "missing_required": None})
        assert req is None

    def test_request_to_dict_has_all_keys(self):
        req = self._create()
        d = self.gate._request_to_dict(req)
        for key in ["request_id", "agent_id", "action", "status", "payload",
                    "decided_by", "decided_at", "risk_factors"]:
            assert key in d

    def test_wait_for_decision_nonexistent_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown approval request"):
            self.gate.wait_for_decision("APPR-TOTALLY-FAKE-XYZ-9182")

    def test_wait_for_decision_timeout_expires_request(self):
        from core.approval import ApprovalStatus
        req = self._create()
        with patch("core.approval.audit"):
            result = self.gate.wait_for_decision(req.request_id, timeout=0.001)
        assert result.status == ApprovalStatus.EXPIRED


# ═══════════════════════════════════════════════════════════════════════════════
# core/rate_limiting.py — RateLimiter
# ═══════════════════════════════════════════════════════════════════════════════

class TestRateLimiterBasic:
    def setup_method(self):
        from core.rate_limiting import RateLimiter
        self.limiter = RateLimiter()

    def test_get_tier_quarantine_maps_to_minimal(self):
        from core.rate_limiting import RateLimitTier
        assert self.limiter.get_tier_for_trust_level("quarantine") == RateLimitTier.MINIMAL

    def test_get_tier_probation_maps_to_restricted(self):
        from core.rate_limiting import RateLimitTier
        assert self.limiter.get_tier_for_trust_level("probation") == RateLimitTier.RESTRICTED

    def test_get_tier_resident_maps_to_standard(self):
        from core.rate_limiting import RateLimitTier
        assert self.limiter.get_tier_for_trust_level("resident") == RateLimitTier.STANDARD

    def test_get_tier_citizen_maps_to_elevated(self):
        from core.rate_limiting import RateLimitTier
        assert self.limiter.get_tier_for_trust_level("citizen") == RateLimitTier.ELEVATED

    def test_get_tier_unknown_defaults_to_minimal(self):
        from core.rate_limiting import RateLimitTier
        assert self.limiter.get_tier_for_trust_level("unknown_xyz") == RateLimitTier.MINIMAL

    def test_first_request_allowed(self):
        allowed, info = self.limiter.check_rate_limit("rl_agent_1", trust_level="resident")
        assert allowed is True
        assert info["allowed"] is True

    def test_rate_info_contains_tier(self):
        _, info = self.limiter.check_rate_limit("rl_agent_2", trust_level="citizen")
        assert info["tier"] == "elevated"

    def test_read_action_half_cost(self):
        _, info = self.limiter.check_rate_limit("rl_agent_3", trust_level="quarantine", action="read")
        assert info["action_cost"] == 0.5

    def test_delete_action_double_cost(self):
        _, info = self.limiter.check_rate_limit("rl_agent_4", trust_level="resident", action="delete")
        assert info["action_cost"] == 2.0

    def test_cost_override(self):
        _, info = self.limiter.check_rate_limit("rl_agent_5", trust_level="resident",
                                                 action="read", cost_override=5.0)
        assert info["action_cost"] == 5.0

    def test_subsequent_requests_increment_count(self):
        self.limiter.check_rate_limit("rl_count_agent", trust_level="resident")
        self.limiter.check_rate_limit("rl_count_agent", trust_level="resident")
        info = self.limiter.get_agent_rate_info("rl_count_agent")
        assert info["total_requests"] == 2

    def test_get_agent_rate_info_returns_none_for_unknown(self):
        result = self.limiter.get_agent_rate_info("nobody_xyz_9182")
        assert result is None

    def test_get_agent_rate_info_returns_dict_after_request(self):
        self.limiter.check_rate_limit("rl_info_agent", trust_level="resident")
        info = self.limiter.get_agent_rate_info("rl_info_agent")
        assert info is not None
        assert info["agent_id"] == "rl_info_agent"
        assert info["tier"] == "standard"
        assert "minute" in info
        assert "hour" in info
        assert "day" in info
        assert "total_requests" in info

    def test_reset_agent_limits_existing_returns_true(self):
        self.limiter.check_rate_limit("rl_reset_agent", trust_level="resident")
        with patch("core.rate_limiting.audit"):
            result = self.limiter.reset_agent_limits("rl_reset_agent", reset_by="admin")
        assert result is True
        assert "rl_reset_agent" not in self.limiter._agent_states

    def test_reset_agent_limits_nonexistent_returns_false(self):
        with patch("core.rate_limiting.audit"):
            result = self.limiter.reset_agent_limits("nobody_xyz_9182")
        assert result is False

    def test_update_tier_config_changes_config(self):
        from core.rate_limiting import RateLimitTier, RateLimitConfig
        new_config = RateLimitConfig(
            requests_per_minute=99,
            requests_per_hour=999,
            requests_per_day=9999,
            burst_size=9,
            cooldown_seconds=9
        )
        with patch("core.rate_limiting.audit"):
            self.limiter.update_tier_config(RateLimitTier.STANDARD, new_config, updated_by="admin")
        assert self.limiter._tier_configs[RateLimitTier.STANDARD].requests_per_minute == 99

    def test_get_all_rate_stats_empty(self):
        stats = self.limiter.get_all_rate_stats()
        assert stats["total_agents_tracked"] == 0
        assert stats["total_requests"] == 0
        assert stats["total_limited"] == 0

    def test_get_all_rate_stats_with_agents(self):
        self.limiter.check_rate_limit("rl_stats1", trust_level="resident")
        self.limiter.check_rate_limit("rl_stats2", trust_level="citizen")
        stats = self.limiter.get_all_rate_stats()
        assert stats["total_agents_tracked"] == 2
        assert stats["total_requests"] == 2
        assert "by_tier" in stats
        assert "top_requesters" in stats

    def test_get_all_rate_stats_top_requesters_sorted(self):
        for _ in range(3):
            self.limiter.check_rate_limit("rl_heavy_user", trust_level="resident")
        self.limiter.check_rate_limit("rl_light_user", trust_level="resident")
        stats = self.limiter.get_all_rate_stats()
        assert len(stats["top_requesters"]) >= 1
        assert stats["top_requesters"][0]["agent_id"] == "rl_heavy_user"


class TestRateLimiterLimitHits:
    def setup_method(self):
        from core.rate_limiting import RateLimiter, RateLimitTier, RateLimitConfig
        self.limiter = RateLimiter()
        # Set tiny limits: 2/min, burst=0 so effective limit=2
        tiny = RateLimitConfig(
            requests_per_minute=2,
            requests_per_hour=1000,
            requests_per_day=10000,
            burst_size=0,
            cooldown_seconds=5
        )
        with patch("core.rate_limiting.audit"):
            self.limiter.update_tier_config(RateLimitTier.STANDARD, tiny)

    def test_minute_limit_exceeded_after_two_requests(self):
        with patch("core.rate_limiting.audit"):
            # 1st and 2nd allowed
            self.limiter.check_rate_limit("rl_lim_agent", trust_level="resident", action="write")
            self.limiter.check_rate_limit("rl_lim_agent", trust_level="resident", action="write")
            # 3rd should be blocked (2*1.0=2 >= limit=2)
            allowed, info = self.limiter.check_rate_limit("rl_lim_agent", trust_level="resident", action="write")
        assert allowed is False
        assert info["reason"] == "minute_limit"

    def test_cooldown_blocks_after_limit(self):
        with patch("core.rate_limiting.audit"):
            # Hit the minute limit
            for _ in range(3):
                self.limiter.check_rate_limit("rl_cd_agent", trust_level="resident", action="write")
            # Next request should be in cooldown
            allowed, info = self.limiter.check_rate_limit("rl_cd_agent", trust_level="resident")
        assert allowed is False
        assert info["reason"] == "cooldown"

    def test_state_tracks_total_limited(self):
        with patch("core.rate_limiting.audit"):
            for _ in range(5):
                self.limiter.check_rate_limit("rl_tl_agent", trust_level="resident", action="write")
        state = self.limiter._agent_states.get("rl_tl_agent")
        assert state is not None
        assert state.total_limited >= 1
