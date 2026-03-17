# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_trust_levels_depth.py
# REM: Depth coverage for core/trust_levels.py
# REM: Enums, dataclasses, TrustLevelManager all methods — pure in-memory.

import pytest
from datetime import datetime, timedelta, timezone

from core.trust_levels import (
    PROMOTION_REQUIREMENTS,
    REVERIFICATION_CONFIG,
    TRUST_LEVEL_CONSTRAINTS,
    AgentTrustLevel,
    AgentTrustRecord,
    TrustLevelManager,
)


# ═══════════════════════════════════════════════════════════════════════════════
# AgentTrustLevel enum
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgentTrustLevelEnum:
    def test_quarantine(self):
        assert AgentTrustLevel.QUARANTINE == "quarantine"

    def test_probation(self):
        assert AgentTrustLevel.PROBATION == "probation"

    def test_resident(self):
        assert AgentTrustLevel.RESIDENT == "resident"

    def test_citizen(self):
        assert AgentTrustLevel.CITIZEN == "citizen"

    def test_agent(self):
        assert AgentTrustLevel.AGENT == "agent"

    def test_all_unique(self):
        vals = [t.value for t in AgentTrustLevel]
        assert len(vals) == len(set(vals))

    def test_five_levels(self):
        assert len(list(AgentTrustLevel)) == 5


# ═══════════════════════════════════════════════════════════════════════════════
# TRUST_LEVEL_CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestTrustLevelConstraints:
    def test_quarantine_cannot_access_external(self):
        c = TRUST_LEVEL_CONSTRAINTS[AgentTrustLevel.QUARANTINE]
        assert c.can_access_external is False

    def test_quarantine_cannot_spawn_agents(self):
        c = TRUST_LEVEL_CONSTRAINTS[AgentTrustLevel.QUARANTINE]
        assert c.can_spawn_agents is False

    def test_quarantine_requires_approval_for_all(self):
        c = TRUST_LEVEL_CONSTRAINTS[AgentTrustLevel.QUARANTINE]
        assert c.requires_approval_for_all is True

    def test_quarantine_low_rate_limit(self):
        assert TRUST_LEVEL_CONSTRAINTS[AgentTrustLevel.QUARANTINE].max_actions_per_minute == 5

    def test_probation_cannot_access_external(self):
        assert TRUST_LEVEL_CONSTRAINTS[AgentTrustLevel.PROBATION].can_access_external is False

    def test_resident_can_access_external(self):
        assert TRUST_LEVEL_CONSTRAINTS[AgentTrustLevel.RESIDENT].can_access_external is True

    def test_resident_cannot_spawn_agents(self):
        assert TRUST_LEVEL_CONSTRAINTS[AgentTrustLevel.RESIDENT].can_spawn_agents is False

    def test_citizen_can_spawn_agents(self):
        assert TRUST_LEVEL_CONSTRAINTS[AgentTrustLevel.CITIZEN].can_spawn_agents is True

    def test_agent_highest_rate_limit(self):
        assert TRUST_LEVEL_CONSTRAINTS[AgentTrustLevel.AGENT].max_actions_per_minute == 300

    def test_agent_can_access_external(self):
        assert TRUST_LEVEL_CONSTRAINTS[AgentTrustLevel.AGENT].can_access_external is True

    def test_all_levels_have_constraints(self):
        for level in AgentTrustLevel:
            assert level in TRUST_LEVEL_CONSTRAINTS


# ═══════════════════════════════════════════════════════════════════════════════
# AgentTrustRecord — computed properties
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgentTrustRecord:
    def test_success_rate_zero_actions(self):
        r = AgentTrustRecord(agent_id="a", trust_level=AgentTrustLevel.QUARANTINE)
        assert r.success_rate() == 0.0

    def test_success_rate_all_success(self):
        r = AgentTrustRecord(agent_id="a", trust_level=AgentTrustLevel.QUARANTINE)
        r.total_actions = 10
        r.successful_actions = 10
        assert r.success_rate() == 1.0

    def test_success_rate_partial(self):
        r = AgentTrustRecord(agent_id="a", trust_level=AgentTrustLevel.QUARANTINE)
        r.total_actions = 4
        r.successful_actions = 3
        assert r.success_rate() == pytest.approx(0.75)

    def test_period_success_rate_no_period_actions(self):
        r = AgentTrustRecord(agent_id="a", trust_level=AgentTrustLevel.QUARANTINE)
        # No period actions → returns 1.0 (no failures = perfect)
        assert r.period_success_rate() == 1.0

    def test_period_success_rate_with_actions(self):
        r = AgentTrustRecord(agent_id="a", trust_level=AgentTrustLevel.QUARANTINE)
        r.period_actions = 10
        r.period_successes = 9
        assert r.period_success_rate() == pytest.approx(0.9)

    def test_reset_period_metrics_zeroes_all(self):
        r = AgentTrustRecord(agent_id="a", trust_level=AgentTrustLevel.QUARANTINE)
        r.period_actions = 10
        r.period_successes = 9
        r.period_failures = 1
        r.period_anomalies = 2
        r.reset_period_metrics()
        assert r.period_actions == 0
        assert r.period_successes == 0
        assert r.period_failures == 0
        assert r.period_anomalies == 0

    def test_to_dict_has_agent_id(self):
        r = AgentTrustRecord(agent_id="a", trust_level=AgentTrustLevel.QUARANTINE)
        assert r.to_dict()["agent_id"] == "a"

    def test_to_dict_has_trust_level(self):
        r = AgentTrustRecord(agent_id="a", trust_level=AgentTrustLevel.CITIZEN)
        assert r.to_dict()["trust_level"] == "citizen"

    def test_to_dict_has_success_rate(self):
        r = AgentTrustRecord(agent_id="a", trust_level=AgentTrustLevel.QUARANTINE)
        r.total_actions = 10
        r.successful_actions = 8
        assert r.to_dict()["success_rate"] == pytest.approx(0.8)

    def test_to_dict_last_promotion_none(self):
        r = AgentTrustRecord(agent_id="a", trust_level=AgentTrustLevel.QUARANTINE)
        assert r.to_dict()["last_promotion"] is None

    def test_to_dict_last_reverification_none(self):
        r = AgentTrustRecord(agent_id="a", trust_level=AgentTrustLevel.QUARANTINE)
        assert r.to_dict()["last_reverification"] is None

    def test_to_dict_registered_at_is_iso(self):
        r = AgentTrustRecord(agent_id="a", trust_level=AgentTrustLevel.QUARANTINE)
        assert "T" in r.to_dict()["registered_at"]


# ═══════════════════════════════════════════════════════════════════════════════
# TrustLevelManager fixture
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mgr():
    return TrustLevelManager()


# ═══════════════════════════════════════════════════════════════════════════════
# register_agent()
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegisterAgent:
    def test_registers_at_quarantine_by_default(self, mgr):
        record = mgr.register_agent("agent-001")
        assert record.trust_level == AgentTrustLevel.QUARANTINE

    def test_skip_quarantine_starts_at_resident(self, mgr):
        record = mgr.register_agent("agent-002", skip_quarantine=True)
        assert record.trust_level == AgentTrustLevel.RESIDENT

    def test_custom_initial_level(self, mgr):
        record = mgr.register_agent("agent-003", initial_level=AgentTrustLevel.PROBATION)
        assert record.trust_level == AgentTrustLevel.PROBATION

    def test_record_stored(self, mgr):
        mgr.register_agent("agent-001")
        assert mgr.get_trust_level("agent-001") == AgentTrustLevel.QUARANTINE

    def test_returns_trust_record(self, mgr):
        record = mgr.register_agent("agent-001")
        assert isinstance(record, AgentTrustRecord)
        assert record.agent_id == "agent-001"


# ═══════════════════════════════════════════════════════════════════════════════
# get_trust_level() / get_constraints()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetTrustLevelAndConstraints:
    def test_get_trust_level_unknown_returns_none(self, mgr):
        assert mgr.get_trust_level("nobody") is None

    def test_get_trust_level_registered(self, mgr):
        mgr.register_agent("agent-001")
        assert mgr.get_trust_level("agent-001") == AgentTrustLevel.QUARANTINE

    def test_get_constraints_unknown_returns_quarantine(self, mgr):
        c = mgr.get_constraints("nobody")
        assert c.requires_approval_for_all is True
        assert c.can_access_external is False

    def test_get_constraints_resident(self, mgr):
        mgr.register_agent("agent-001", initial_level=AgentTrustLevel.RESIDENT)
        c = mgr.get_constraints("agent-001")
        assert c.can_access_external is True

    def test_get_constraints_agent(self, mgr):
        mgr.register_agent("agent-001", initial_level=AgentTrustLevel.AGENT)
        c = mgr.get_constraints("agent-001")
        assert c.can_spawn_agents is True
        assert c.max_actions_per_minute == 300


# ═══════════════════════════════════════════════════════════════════════════════
# record_action()
# ═══════════════════════════════════════════════════════════════════════════════

class TestRecordAction:
    def test_success_increments_counts(self, mgr):
        mgr.register_agent("agent-001")
        mgr.record_action("agent-001", success=True)
        record = mgr._records["agent-001"]
        assert record.total_actions == 1
        assert record.successful_actions == 1

    def test_failure_increments_failed(self, mgr):
        mgr.register_agent("agent-001")
        mgr.record_action("agent-001", success=False)
        record = mgr._records["agent-001"]
        assert record.failed_actions == 1

    def test_anomaly_increments_anomaly_count(self, mgr):
        mgr.register_agent("agent-001")
        mgr.record_action("agent-001", success=False, triggered_anomaly=True)
        assert mgr._records["agent-001"].anomalies_triggered == 1

    def test_three_anomalies_trigger_auto_demote(self, mgr):
        mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        for _ in range(3):
            mgr.record_action("agent-001", success=False, triggered_anomaly=True)
        # Should be demoted from CITIZEN to RESIDENT
        assert mgr.get_trust_level("agent-001") != AgentTrustLevel.CITIZEN

    def test_period_metrics_incremented(self, mgr):
        mgr.register_agent("agent-001")
        mgr.record_action("agent-001", success=True)
        record = mgr._records["agent-001"]
        assert record.period_actions == 1
        assert record.period_successes == 1

    def test_unknown_agent_no_error(self, mgr):
        # Should not raise
        mgr.record_action("nobody", success=True)


# ═══════════════════════════════════════════════════════════════════════════════
# record_approval_decision()
# ═══════════════════════════════════════════════════════════════════════════════

class TestRecordApprovalDecision:
    def test_approved_increments_granted(self, mgr):
        mgr.register_agent("agent-001")
        mgr.record_approval_decision("agent-001", approved=True)
        assert mgr._records["agent-001"].approvals_granted == 1

    def test_denied_increments_denied(self, mgr):
        mgr.register_agent("agent-001")
        mgr.record_approval_decision("agent-001", approved=False)
        assert mgr._records["agent-001"].approvals_denied == 1

    def test_five_denials_trigger_auto_demote(self, mgr):
        mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        for _ in range(5):
            mgr.record_approval_decision("agent-001", approved=False)
        assert mgr.get_trust_level("agent-001") != AgentTrustLevel.CITIZEN

    def test_unknown_agent_no_error(self, mgr):
        mgr.record_approval_decision("nobody", approved=False)


# ═══════════════════════════════════════════════════════════════════════════════
# check_promotion_eligibility()
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckPromotionEligibility:
    def test_unknown_agent_not_eligible(self, mgr):
        eligible, reason = mgr.check_promotion_eligibility("nobody")
        assert eligible is False
        assert "not found" in reason.lower()

    def test_agent_level_already_at_max(self, mgr):
        mgr.register_agent("agent-001", initial_level=AgentTrustLevel.AGENT)
        eligible, reason = mgr.check_promotion_eligibility("agent-001")
        assert eligible is False
        assert "highest" in reason.lower()

    def test_not_enough_days(self, mgr):
        record = mgr.register_agent("agent-001")
        record.days_at_current_level = 0  # Need 3 for quarantine
        eligible, reason = mgr.check_promotion_eligibility("agent-001")
        assert eligible is False
        assert "days" in reason.lower()

    def test_not_enough_actions(self, mgr):
        record = mgr.register_agent("agent-001")
        record.days_at_current_level = 3
        record.successful_actions = 0  # Need 50 for quarantine
        eligible, reason = mgr.check_promotion_eligibility("agent-001")
        assert eligible is False
        assert "action" in reason.lower()

    def test_success_rate_too_low(self, mgr):
        record = mgr.register_agent("agent-001")
        record.days_at_current_level = 3
        record.successful_actions = 50
        record.total_actions = 100  # 50% < 0.98
        eligible, reason = mgr.check_promotion_eligibility("agent-001")
        assert eligible is False
        assert "success rate" in reason.lower()

    def test_too_many_anomalies(self, mgr):
        record = mgr.register_agent("agent-001")
        record.days_at_current_level = 3
        record.successful_actions = 50
        record.total_actions = 51  # 98%
        record.anomalies_triggered = 1  # max is 0 for QUARANTINE
        eligible, reason = mgr.check_promotion_eligibility("agent-001")
        assert eligible is False
        assert "anomal" in reason.lower()

    def test_too_many_denied_approvals(self, mgr):
        record = mgr.register_agent("agent-001")
        record.days_at_current_level = 3
        record.successful_actions = 50
        record.total_actions = 51
        record.anomalies_triggered = 0
        record.approvals_denied = 1  # max is 0 for QUARANTINE
        eligible, reason = mgr.check_promotion_eligibility("agent-001")
        assert eligible is False
        assert "denied" in reason.lower()

    def test_eligible_when_all_met(self, mgr):
        record = mgr.register_agent("agent-001")
        record.days_at_current_level = 3
        record.successful_actions = 50
        record.total_actions = 51  # 98%
        record.anomalies_triggered = 0
        record.approvals_denied = 0
        eligible, reason = mgr.check_promotion_eligibility("agent-001")
        assert eligible is True

    def test_promotion_blocked_until_future(self, mgr):
        record = mgr.register_agent("agent-001")
        record.promotion_blocked_until = datetime.now(timezone.utc) + timedelta(days=1)
        record.promotion_blocked_reason = "security incident"
        eligible, reason = mgr.check_promotion_eligibility("agent-001")
        assert eligible is False
        assert "blocked" in reason.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# promote()
# ═══════════════════════════════════════════════════════════════════════════════

class TestPromote:
    def test_promote_unknown_agent_fails(self, mgr):
        ok, reason = mgr.promote("nobody", "admin", skip_eligibility_check=True)
        assert ok is False

    def test_promote_agent_level_fails(self, mgr):
        mgr.register_agent("agent-001", initial_level=AgentTrustLevel.AGENT)
        ok, reason = mgr.promote("agent-001", "admin", skip_eligibility_check=True)
        assert ok is False
        assert "highest" in reason.lower()

    def test_promote_quarantine_to_probation(self, mgr):
        mgr.register_agent("agent-001")
        ok, reason = mgr.promote("agent-001", "admin", skip_eligibility_check=True)
        assert ok is True
        assert mgr.get_trust_level("agent-001") == AgentTrustLevel.PROBATION

    def test_promote_chain(self, mgr):
        mgr.register_agent("agent-001")
        levels = [AgentTrustLevel.PROBATION, AgentTrustLevel.RESIDENT, AgentTrustLevel.CITIZEN, AgentTrustLevel.AGENT]
        for expected in levels:
            ok, _ = mgr.promote("agent-001", "admin", skip_eligibility_check=True)
            assert ok is True
            assert mgr.get_trust_level("agent-001") == expected

    def test_promote_resets_days_at_level(self, mgr):
        record = mgr.register_agent("agent-001")
        record.days_at_current_level = 10
        mgr.promote("agent-001", "admin", skip_eligibility_check=True)
        assert record.days_at_current_level == 0

    def test_promote_ineligible_fails(self, mgr):
        mgr.register_agent("agent-001")  # days=0, need 3
        ok, reason = mgr.promote("agent-001", "admin", skip_eligibility_check=False)
        assert ok is False


# ═══════════════════════════════════════════════════════════════════════════════
# demote()
# ═══════════════════════════════════════════════════════════════════════════════

class TestDemote:
    def test_demote_unknown_agent_fails(self, mgr):
        ok, reason = mgr.demote("nobody", "admin", "test")
        assert ok is False

    def test_demote_quarantine_fails(self, mgr):
        mgr.register_agent("agent-001")  # already at QUARANTINE
        ok, reason = mgr.demote("agent-001", "admin", "test")
        assert ok is False
        assert "lowest" in reason.lower()

    def test_demote_citizen_to_resident(self, mgr):
        mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        ok, reason = mgr.demote("agent-001", "admin", "misbehaved")
        assert ok is True
        assert mgr.get_trust_level("agent-001") == AgentTrustLevel.RESIDENT

    def test_demote_sets_promotion_block(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        mgr.demote("agent-001", "admin", "reason", block_promotion_days=7)
        assert record.promotion_blocked_until is not None

    def test_demote_sets_reason(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        mgr.demote("agent-001", "admin", "policy violation")
        assert record.promotion_blocked_reason == "policy violation"


# ═══════════════════════════════════════════════════════════════════════════════
# quarantine()
# ═══════════════════════════════════════════════════════════════════════════════

class TestQuarantine:
    def test_quarantine_unknown_returns_false(self, mgr):
        assert mgr.quarantine("nobody", "admin", "test") is False

    def test_quarantine_citizen_jumps_to_quarantine(self, mgr):
        mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        result = mgr.quarantine("agent-001", "admin", "security incident")
        assert result is True
        assert mgr.get_trust_level("agent-001") == AgentTrustLevel.QUARANTINE

    def test_quarantine_sets_30_day_block(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.RESIDENT)
        mgr.quarantine("agent-001", "admin", "suspicious activity")
        delta = record.promotion_blocked_until - datetime.now(timezone.utc)
        assert delta.days >= 29

    def test_quarantine_reason_in_block(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.RESIDENT)
        mgr.quarantine("agent-001", "admin", "attack detected")
        assert "attack detected" in record.promotion_blocked_reason


# ═══════════════════════════════════════════════════════════════════════════════
# get_all_records() / get_agents_by_level()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetRecords:
    def test_get_all_records_empty(self, mgr):
        assert mgr.get_all_records() == []

    def test_get_all_records_after_register(self, mgr):
        mgr.register_agent("agent-001")
        mgr.register_agent("agent-002")
        assert len(mgr.get_all_records()) == 2

    def test_get_agents_by_level_empty(self, mgr):
        assert mgr.get_agents_by_level(AgentTrustLevel.QUARANTINE) == []

    def test_get_agents_by_level_correct(self, mgr):
        mgr.register_agent("agent-001")
        mgr.register_agent("agent-002")
        agents = mgr.get_agents_by_level(AgentTrustLevel.QUARANTINE)
        assert "agent-001" in agents
        assert "agent-002" in agents

    def test_get_agents_by_level_filters_correctly(self, mgr):
        mgr.register_agent("q-agent")
        mgr.register_agent("r-agent", initial_level=AgentTrustLevel.RESIDENT)
        q_agents = mgr.get_agents_by_level(AgentTrustLevel.QUARANTINE)
        assert "q-agent" in q_agents
        assert "r-agent" not in q_agents


# ═══════════════════════════════════════════════════════════════════════════════
# needs_reverification()
# ═══════════════════════════════════════════════════════════════════════════════

class TestNeedsReverification:
    def test_unknown_agent_returns_false(self, mgr):
        needs, reason = mgr.needs_reverification("nobody")
        assert needs is False

    def test_quarantine_does_not_need_reverification(self, mgr):
        mgr.register_agent("agent-001")
        needs, reason = mgr.needs_reverification("agent-001")
        assert needs is False
        assert "does not require" in reason.lower()

    def test_probation_does_not_need_reverification(self, mgr):
        mgr.register_agent("agent-001", initial_level=AgentTrustLevel.PROBATION)
        needs, reason = mgr.needs_reverification("agent-001")
        assert needs is False

    def test_citizen_no_promotion_no_reverification_yet(self, mgr):
        mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        needs, reason = mgr.needs_reverification("agent-001")
        assert needs is False

    def test_citizen_promoted_long_ago_needs_reverification(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        record.last_promotion = datetime.now(timezone.utc) - timedelta(days=8)
        needs, reason = mgr.needs_reverification("agent-001")
        assert needs is True

    def test_citizen_last_reverification_recent_no_need(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        record.last_reverification = datetime.now(timezone.utc) - timedelta(days=2)
        needs, reason = mgr.needs_reverification("agent-001")
        assert needs is False

    def test_citizen_last_reverification_overdue(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        record.last_reverification = datetime.now(timezone.utc) - timedelta(days=10)
        needs, reason = mgr.needs_reverification("agent-001")
        assert needs is True


# ═══════════════════════════════════════════════════════════════════════════════
# perform_reverification()
# ═══════════════════════════════════════════════════════════════════════════════

class TestPerformReverification:
    def test_unknown_agent_fails(self, mgr):
        passed, reason, _ = mgr.perform_reverification("nobody")
        assert passed is False
        assert "not found" in reason.lower()

    def test_quarantine_no_reverification_required(self, mgr):
        mgr.register_agent("agent-001")
        passed, reason, details = mgr.perform_reverification("agent-001")
        assert passed is True
        assert "no re-verification required" in reason.lower()

    def test_citizen_passes_with_good_metrics(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        record.period_actions = 30
        record.period_successes = 29
        record.period_failures = 1
        record.period_anomalies = 0
        passed, reason, _ = mgr.perform_reverification("agent-001")
        assert passed is True

    def test_citizen_fails_insufficient_activity(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        record.period_actions = 5  # Need 20 for CITIZEN
        record.period_successes = 5
        record.period_failures = 0
        record.period_anomalies = 0
        passed, reason, _ = mgr.perform_reverification("agent-001")
        assert passed is False
        assert "activity" in reason.lower() or "insufficient" in reason.lower()

    def test_citizen_fails_low_success_rate(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        record.period_actions = 100
        record.period_successes = 80  # 80% < 95% required
        record.period_failures = 20
        record.period_anomalies = 0
        passed, reason, _ = mgr.perform_reverification("agent-001")
        assert passed is False

    def test_citizen_fails_too_many_anomalies(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        record.period_actions = 25
        record.period_successes = 25
        record.period_failures = 0
        record.period_anomalies = 2  # Max 1 for CITIZEN
        passed, reason, _ = mgr.perform_reverification("agent-001")
        assert passed is False

    def test_reverification_resets_period_metrics(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        record.period_actions = 30
        record.period_successes = 29
        record.period_failures = 1
        record.period_anomalies = 0
        mgr.perform_reverification("agent-001")
        assert record.period_actions == 0

    def test_failed_reverification_demotes_agent(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        record.period_actions = 5  # Insufficient — forces fail
        mgr.perform_reverification("agent-001")
        assert mgr.get_trust_level("agent-001") == AgentTrustLevel.RESIDENT

    def test_returns_details_dict(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        record.period_actions = 30
        record.period_successes = 29
        _, _, details = mgr.perform_reverification("agent-001")
        assert "agent_id" in details
        assert "trust_level" in details


# ═══════════════════════════════════════════════════════════════════════════════
# run_system_reverification()
# ═══════════════════════════════════════════════════════════════════════════════

class TestRunSystemReverification:
    def test_empty_system(self, mgr):
        results = mgr.run_system_reverification()
        assert results["checked"] == 0

    def test_counts_agents_checked(self, mgr):
        mgr.register_agent("agent-001")
        mgr.register_agent("agent-002", initial_level=AgentTrustLevel.CITIZEN)
        results = mgr.run_system_reverification()
        assert results["checked"] == 2

    def test_quarantine_agents_skipped(self, mgr):
        mgr.register_agent("agent-001")  # QUARANTINE — no reverification needed
        results = mgr.run_system_reverification()
        assert results["skipped"] == 1
        assert results["verified"] == 0

    def test_results_has_required_keys(self, mgr):
        results = mgr.run_system_reverification()
        for key in ["checked", "verified", "passed", "failed", "skipped", "details"]:
            assert key in results

    def test_citizen_due_for_reverification_is_verified(self, mgr):
        record = mgr.register_agent("agent-001", initial_level=AgentTrustLevel.CITIZEN)
        record.last_reverification = datetime.now(timezone.utc) - timedelta(days=10)
        record.period_actions = 30
        record.period_successes = 29
        results = mgr.run_system_reverification()
        assert results["verified"] >= 1
