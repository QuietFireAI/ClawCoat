# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_threat_response_depth.py
# REM: Depth coverage for core/threat_response.py
# REM: ThreatLevel, ResponseAction, ThreatResponseEngine — in-memory.

import pytest
from datetime import datetime, timezone

from core.threat_response import (
    DEFAULT_INDICATORS,
    DEFAULT_POLICIES,
    ResponseAction,
    ResponsePolicy,
    ThreatEvent,
    ThreatIndicator,
    ThreatLevel,
    ThreatResponseEngine,
)


# ─── Patch Redis so audit.log() uses in-memory path ────────────────────────────
@pytest.fixture(autouse=True)
def _no_redis(monkeypatch):
    monkeypatch.setattr("core.persistence.get_redis", lambda: None)


@pytest.fixture(autouse=True)
def _reset_default_indicators():
    """Re-enable all default indicators before/after each test.

    ThreatResponseEngine.__init__ stores references to the shared ThreatIndicator
    objects in DEFAULT_INDICATORS (not copies). disable_indicator() mutates those
    objects, which bleeds into later tests that create fresh engine instances.
    """
    for ind in DEFAULT_INDICATORS:
        ind.enabled = True
    yield
    for ind in DEFAULT_INDICATORS:
        ind.enabled = True


@pytest.fixture
def engine():
    """Fresh ThreatResponseEngine — pure in-memory, no Redis deps."""
    return ThreatResponseEngine()


def _make_event(threat_level=ThreatLevel.CRITICAL, agent_id="agent-001"):
    return ThreatEvent(
        event_id="threat_testevt",
        indicator_id="ti_test",
        threat_level=threat_level,
        agent_id=agent_id,
        description="test event",
        evidence={},
        detected_at=datetime.now(timezone.utc),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ThreatLevel enum
# ═══════════════════════════════════════════════════════════════════════════════

class TestThreatLevel:
    def test_critical_value(self):
        assert ThreatLevel.CRITICAL == "critical"

    def test_high_value(self):
        assert ThreatLevel.HIGH == "high"

    def test_medium_value(self):
        assert ThreatLevel.MEDIUM == "medium"

    def test_low_value(self):
        assert ThreatLevel.LOW == "low"

    def test_info_value(self):
        assert ThreatLevel.INFO == "info"

    def test_five_members(self):
        assert len(ThreatLevel) == 5

    def test_is_str_subclass(self):
        assert isinstance(ThreatLevel.CRITICAL, str)


# ═══════════════════════════════════════════════════════════════════════════════
# ResponseAction enum
# ═══════════════════════════════════════════════════════════════════════════════

class TestResponseAction:
    def test_quarantine_value(self):
        assert ResponseAction.QUARANTINE == "quarantine"

    def test_demote_value(self):
        assert ResponseAction.DEMOTE == "demote"

    def test_rate_limit_value(self):
        assert ResponseAction.RATE_LIMIT == "rate_limit"

    def test_revoke_delegations_value(self):
        assert ResponseAction.REVOKE_DELEGATIONS == "revoke_delegations"

    def test_block_external_value(self):
        assert ResponseAction.BLOCK_EXTERNAL == "block_external"

    def test_alert_value(self):
        assert ResponseAction.ALERT == "alert"

    def test_log_value(self):
        assert ResponseAction.LOG == "log"

    def test_seven_members(self):
        assert len(ResponseAction) == 7

    def test_is_str_subclass(self):
        assert isinstance(ResponseAction.QUARANTINE, str)


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT_INDICATORS
# ═══════════════════════════════════════════════════════════════════════════════

class TestDefaultIndicators:
    def test_five_indicators(self):
        assert len(DEFAULT_INDICATORS) == 5

    def test_critical_anomaly_burst_present(self):
        ids = [i.indicator_id for i in DEFAULT_INDICATORS]
        assert "ti_critical_anomaly_burst" in ids

    def test_capability_probing_present(self):
        ids = [i.indicator_id for i in DEFAULT_INDICATORS]
        assert "ti_capability_probing" in ids

    def test_approval_bypass_attempt_present(self):
        ids = [i.indicator_id for i in DEFAULT_INDICATORS]
        assert "ti_approval_bypass_attempt" in ids

    def test_excessive_failures_present(self):
        ids = [i.indicator_id for i in DEFAULT_INDICATORS]
        assert "ti_excessive_failures" in ids

    def test_signature_failure_present(self):
        ids = [i.indicator_id for i in DEFAULT_INDICATORS]
        assert "ti_signature_failure" in ids

    def test_critical_anomaly_burst_threat_level(self):
        ind = next(i for i in DEFAULT_INDICATORS if i.indicator_id == "ti_critical_anomaly_burst")
        assert ind.threat_level == ThreatLevel.CRITICAL

    def test_capability_probing_threat_level(self):
        ind = next(i for i in DEFAULT_INDICATORS if i.indicator_id == "ti_capability_probing")
        assert ind.threat_level == ThreatLevel.HIGH

    def test_approval_bypass_threat_level(self):
        ind = next(i for i in DEFAULT_INDICATORS if i.indicator_id == "ti_approval_bypass_attempt")
        assert ind.threat_level == ThreatLevel.CRITICAL

    def test_excessive_failures_threat_level(self):
        ind = next(i for i in DEFAULT_INDICATORS if i.indicator_id == "ti_excessive_failures")
        assert ind.threat_level == ThreatLevel.HIGH

    def test_signature_failure_threat_level(self):
        ind = next(i for i in DEFAULT_INDICATORS if i.indicator_id == "ti_signature_failure")
        assert ind.threat_level == ThreatLevel.CRITICAL

    def test_all_enabled_by_default(self):
        assert all(i.enabled for i in DEFAULT_INDICATORS)

    def test_critical_anomaly_burst_actions(self):
        ind = next(i for i in DEFAULT_INDICATORS if i.indicator_id == "ti_critical_anomaly_burst")
        assert ResponseAction.QUARANTINE in ind.response_actions


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT_POLICIES
# ═══════════════════════════════════════════════════════════════════════════════

class TestDefaultPolicies:
    def test_four_policies(self):
        assert len(DEFAULT_POLICIES) == 4

    def test_critical_policy_present(self):
        assert ThreatLevel.CRITICAL in DEFAULT_POLICIES

    def test_high_policy_present(self):
        assert ThreatLevel.HIGH in DEFAULT_POLICIES

    def test_medium_policy_present(self):
        assert ThreatLevel.MEDIUM in DEFAULT_POLICIES

    def test_low_policy_present(self):
        assert ThreatLevel.LOW in DEFAULT_POLICIES

    def test_critical_notify_admins(self):
        assert DEFAULT_POLICIES[ThreatLevel.CRITICAL].notify_admins is True

    def test_high_notify_admins(self):
        assert DEFAULT_POLICIES[ThreatLevel.HIGH].notify_admins is True

    def test_medium_notify_admins(self):
        # Zero-tolerance: all levels notify
        assert DEFAULT_POLICIES[ThreatLevel.MEDIUM].notify_admins is True

    def test_low_notify_admins(self):
        assert DEFAULT_POLICIES[ThreatLevel.LOW].notify_admins is True

    def test_critical_actions_include_quarantine(self):
        assert ResponseAction.QUARANTINE in DEFAULT_POLICIES[ThreatLevel.CRITICAL].actions

    def test_medium_actions_include_quarantine(self):
        # Zero-tolerance: even MEDIUM quarantines immediately
        assert ResponseAction.QUARANTINE in DEFAULT_POLICIES[ThreatLevel.MEDIUM].actions

    def test_all_policies_are_response_policy(self):
        assert all(isinstance(p, ResponsePolicy) for p in DEFAULT_POLICIES.values())


# ═══════════════════════════════════════════════════════════════════════════════
# ThreatResponseEngine.__init__()
# ═══════════════════════════════════════════════════════════════════════════════

class TestThreatResponseEngineInit:
    def test_five_indicators_loaded(self, engine):
        assert len(engine._indicators) == 5

    def test_four_policies_loaded(self, engine):
        assert len(engine._policies) == 4

    def test_events_empty(self, engine):
        assert engine._events == []

    def test_no_last_trigger_attribute(self, engine):
        # Zero-tolerance: cooldown tracking removed
        assert not hasattr(engine, "_last_trigger")

    def test_seven_action_handlers(self, engine):
        assert len(engine._action_handlers) == 7

    def test_quarantine_handler_registered(self, engine):
        assert ResponseAction.QUARANTINE in engine._action_handlers

    def test_demote_handler_registered(self, engine):
        assert ResponseAction.DEMOTE in engine._action_handlers

    def test_rate_limit_handler_registered(self, engine):
        assert ResponseAction.RATE_LIMIT in engine._action_handlers

    def test_revoke_delegations_handler_registered(self, engine):
        assert ResponseAction.REVOKE_DELEGATIONS in engine._action_handlers

    def test_block_external_handler_registered(self, engine):
        assert ResponseAction.BLOCK_EXTERNAL in engine._action_handlers

    def test_alert_handler_registered(self, engine):
        assert ResponseAction.ALERT in engine._action_handlers

    def test_log_handler_registered(self, engine):
        assert ResponseAction.LOG in engine._action_handlers


# ═══════════════════════════════════════════════════════════════════════════════
# ThreatResponseEngine._matches_pattern()
# ═══════════════════════════════════════════════════════════════════════════════

class TestMatchesPattern:
    def test_critical_severity_matches_immediately(self, engine):
        # Zero-tolerance: matching severity fires on first occurrence
        pattern = {"anomaly_severity": "critical"}
        assert engine._matches_pattern(pattern, "any_type", "critical", {}) is True

    def test_count_threshold_field_ignored(self, engine):
        # Zero-tolerance: count_threshold is not a recognised criterion — ignored
        pattern = {"anomaly_severity": "critical", "count_threshold": 999, "window_minutes": 5}
        assert engine._matches_pattern(pattern, "any_type", "critical", {}) is True

    def test_severity_mismatch_returns_false(self, engine):
        pattern = {"anomaly_severity": "critical"}
        assert engine._matches_pattern(pattern, "any_type", "high", {}) is False

    def test_anomaly_type_mismatch_returns_false(self, engine):
        # anomaly_type in pattern and doesn't match → early False
        pattern = {"anomaly_type": "capability_probe", "anomaly_severity": "critical"}
        assert engine._matches_pattern(pattern, "wrong_type", "critical", {}) is False

    def test_anomaly_type_only_matches(self, engine):
        # REM: H6 fix: matching anomaly_type with count_threshold=1 fires immediately
        pattern = {"anomaly_type": "capability_probe"}
        assert engine._matches_pattern(pattern, "capability_probe", "high", {}) is True

    def test_no_relevant_keys_returns_false(self, engine):
        # Pattern with only threshold fields — no positive match criterion → False
        pattern = {"failure_rate_threshold": 0.5, "min_actions": 20, "window_minutes": 30}
        assert engine._matches_pattern(pattern, "any_type", "high", {}) is False

    def test_empty_pattern_returns_false(self, engine):
        assert engine._matches_pattern({}, "x", "y", {}) is False

    def test_returns_bool(self, engine):
        result = engine._matches_pattern({"anomaly_severity": "critical"}, "t", "critical", {})
        assert isinstance(result, bool)


# ═══════════════════════════════════════════════════════════════════════════════
# ThreatResponseEngine.evaluate_anomaly()
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvaluateAnomaly:
    def test_no_match_returns_none(self, engine):
        result = engine.evaluate_anomaly("agent-001", "unknown_type", "low", {})
        assert result is None

    def test_single_occurrence_indicator_fires(self, engine):
        # ti_approval_bypass_attempt has count_threshold=1 — fires on first call
        result = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert result is not None

    def test_returned_event_is_threat_event(self, engine):
        result = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert isinstance(result, ThreatEvent)

    def test_event_id_has_prefix(self, engine):
        result = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert result.event_id.startswith("threat_")

    def test_event_indicator_id(self, engine):
        # Use severity="medium" so only ti_approval_bypass_attempt (type-match) fires,
        # not ti_critical_anomaly_burst (severity="critical" only)
        result = engine.evaluate_anomaly("agent-001", "approval_bypass", "medium", {})
        assert result.indicator_id == "ti_approval_bypass_attempt"

    def test_event_agent_id(self, engine):
        result = engine.evaluate_anomaly("agent-007", "approval_bypass", "critical", {})
        assert result.agent_id == "agent-007"

    def test_event_threat_level_is_critical(self, engine):
        result = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert result.threat_level == ThreatLevel.CRITICAL

    def test_evidence_stored_in_event(self, engine):
        evidence = {"request_count": 5, "window": "5m"}
        result = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", evidence)
        assert result.evidence == evidence

    def test_event_appended_to_events(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert len(engine._events) == 1

    def test_zero_tolerance_same_agent_fires_twice(self, engine):
        # Zero-tolerance: no cooldown — same agent fires on every matching call
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        result2 = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert result2 is not None

    def test_zero_tolerance_multiple_events_recorded(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert len(engine._events) == 2

    def test_different_agent_also_fires(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        result2 = engine.evaluate_anomaly("agent-002", "approval_bypass", "critical", {})
        assert result2 is not None

    def test_disabled_indicator_skipped(self, engine):
        engine.disable_indicator("ti_approval_bypass_attempt")
        result = engine.evaluate_anomaly("agent-001", "approval_bypass", "medium", {})
        assert result is None

    def test_medium_indicator_fires_immediately(self, engine):
        # Zero-tolerance: MEDIUM quarantines immediately — no confirmation gate
        custom = ThreatIndicator(
            indicator_id="ti_custom_medium_test",
            name="Custom Medium",
            description="Test indicator",
            threat_level=ThreatLevel.MEDIUM,
            pattern={"anomaly_severity": "critical"},
            response_actions=[ResponseAction.ALERT],
        )
        engine.add_indicator(custom)
        engine.disable_indicator("ti_critical_anomaly_burst")
        engine.disable_indicator("ti_approval_bypass_attempt")
        engine.disable_indicator("ti_signature_failure")
        result = engine.evaluate_anomaly("agent-001", "any_type", "critical", {})
        assert result is not None
        # ALERT handler returns True → action recorded
        assert "alert" in result.response_actions_taken


# ═══════════════════════════════════════════════════════════════════════════════
# Action handlers (stub/failure-safe tests)
# ═══════════════════════════════════════════════════════════════════════════════

class TestActionHandlers:
    def test_block_external_returns_false(self, engine):
        # Stub — not yet implemented, always returns False
        event = _make_event()
        result = engine._handle_block_external("agent-001", event)
        assert result is False

    def test_alert_returns_true(self, engine):
        event = _make_event()
        result = engine._handle_alert("agent-001", event)
        assert result is True

    def test_log_returns_true(self, engine):
        event = _make_event()
        result = engine._handle_log("agent-001", event)
        assert result is True

    def test_quarantine_returns_bool_on_failure(self, engine):
        # trust_manager not available in unit test — returns False
        event = _make_event()
        result = engine._handle_quarantine("agent-001", event)
        assert isinstance(result, bool)

    def test_demote_returns_bool_on_failure(self, engine):
        event = _make_event()
        result = engine._handle_demote("agent-001", event)
        assert isinstance(result, bool)


# ═══════════════════════════════════════════════════════════════════════════════
# ThreatResponseEngine.get_recent_threats()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetRecentThreats:
    def test_empty_initially(self, engine):
        assert engine.get_recent_threats() == []

    def test_returns_list(self, engine):
        assert isinstance(engine.get_recent_threats(), list)

    def test_returns_dict_items(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        result = engine.get_recent_threats()
        assert isinstance(result[0], dict)

    def test_has_event_id(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert "event_id" in engine.get_recent_threats()[0]

    def test_has_indicator_id(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert "indicator_id" in engine.get_recent_threats()[0]

    def test_has_threat_level(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert "threat_level" in engine.get_recent_threats()[0]

    def test_agent_id_correct(self, engine):
        engine.evaluate_anomaly("agent-999", "approval_bypass", "critical", {})
        assert engine.get_recent_threats()[0]["agent_id"] == "agent-999"

    def test_has_detected_at(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert "detected_at" in engine.get_recent_threats()[0]

    def test_has_actions_taken(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert "actions_taken" in engine.get_recent_threats()[0]

    def test_has_resolved(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert "resolved" in engine.get_recent_threats()[0]

    def test_limit_respected(self, engine):
        # Use distinct agents to avoid cooldown
        for i in range(6):
            engine.evaluate_anomaly(f"agent-{i:03d}", "approval_bypass", "critical", {})
        result = engine.get_recent_threats(limit=3)
        assert len(result) == 3

    def test_eleven_keys_in_result(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        expected = {
            "event_id", "indicator_id", "threat_level", "agent_id",
            "description", "detected_at", "actions_taken", "resolved",
            "human_reviewed", "human_reviewed_by", "human_reviewed_at",
        }
        assert set(engine.get_recent_threats()[0].keys()) == expected

    def test_human_reviewed_false_by_default(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert engine.get_recent_threats()[0]["human_reviewed"] is False

    def test_human_reviewed_by_none_by_default(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert engine.get_recent_threats()[0]["human_reviewed_by"] is None

    def test_resolved_false_by_default(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert engine.get_recent_threats()[0]["resolved"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# ThreatResponseEngine.get_threat_stats()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetThreatStats:
    def test_returns_dict(self, engine):
        assert isinstance(engine.get_threat_stats(), dict)

    def test_total_threats_zero_initially(self, engine):
        assert engine.get_threat_stats()["total_threats"] == 0

    def test_last_24h_zero_initially(self, engine):
        assert engine.get_threat_stats()["last_24h"] == 0

    def test_unresolved_zero_initially(self, engine):
        assert engine.get_threat_stats()["unresolved"] == 0

    def test_auto_responses_zero_initially(self, engine):
        assert engine.get_threat_stats()["auto_responses"] == 0

    def test_by_level_present(self, engine):
        assert "by_level" in engine.get_threat_stats()

    def test_by_level_is_dict(self, engine):
        assert isinstance(engine.get_threat_stats()["by_level"], dict)

    def test_by_level_has_all_threat_levels(self, engine):
        by_level = engine.get_threat_stats()["by_level"]
        for level in ThreatLevel:
            assert level.value in by_level

    def test_total_threats_increments(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert engine.get_threat_stats()["total_threats"] == 1

    def test_unresolved_increments(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert engine.get_threat_stats()["unresolved"] == 1

    def test_last_24h_counts_recent(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert engine.get_threat_stats()["last_24h"] == 1

    def test_five_required_keys_present(self, engine):
        stats = engine.get_threat_stats()
        required = {"total_threats", "last_24h", "by_level", "unresolved", "auto_responses"}
        assert required.issubset(stats.keys())

    def test_multiple_events_counted(self, engine):
        engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        engine.evaluate_anomaly("agent-002", "approval_bypass", "critical", {})
        assert engine.get_threat_stats()["total_threats"] == 2


# ═══════════════════════════════════════════════════════════════════════════════
# ThreatResponseEngine.add_indicator()
# ═══════════════════════════════════════════════════════════════════════════════

class TestAddIndicator:
    def _new_indicator(self, indicator_id="ti_custom_new"):
        return ThreatIndicator(
            indicator_id=indicator_id,
            name="Custom",
            description="Test",
            threat_level=ThreatLevel.LOW,
            pattern={},
            response_actions=[ResponseAction.LOG],
        )

    def test_indicator_added(self, engine):
        initial = len(engine._indicators)
        engine.add_indicator(self._new_indicator())
        assert len(engine._indicators) == initial + 1

    def test_indicator_retrievable_by_id(self, engine):
        engine.add_indicator(self._new_indicator("ti_custom_retrieve"))
        assert "ti_custom_retrieve" in engine._indicators

    def test_existing_indicator_overwritten(self, engine):
        override = ThreatIndicator(
            indicator_id="ti_critical_anomaly_burst",
            name="Overridden",
            description="Overridden",
            threat_level=ThreatLevel.LOW,
            pattern={},
            response_actions=[ResponseAction.LOG],
        )
        engine.add_indicator(override)
        assert engine._indicators["ti_critical_anomaly_burst"].name == "Overridden"


# ═══════════════════════════════════════════════════════════════════════════════
# ThreatResponseEngine.disable_indicator() / enable_indicator()
# ═══════════════════════════════════════════════════════════════════════════════

class TestDisableEnableIndicator:
    def test_disable_sets_enabled_false(self, engine):
        engine.disable_indicator("ti_critical_anomaly_burst")
        assert engine._indicators["ti_critical_anomaly_burst"].enabled is False

    def test_enable_sets_enabled_true(self, engine):
        engine.disable_indicator("ti_critical_anomaly_burst")
        engine.enable_indicator("ti_critical_anomaly_burst")
        assert engine._indicators["ti_critical_anomaly_burst"].enabled is True

    def test_disable_unknown_id_no_error(self, engine):
        engine.disable_indicator("nonexistent_id")  # Should not raise

    def test_enable_unknown_id_no_error(self, engine):
        engine.enable_indicator("nonexistent_id")  # Should not raise

    def test_disable_does_not_add_new_key(self, engine):
        initial = len(engine._indicators)
        engine.disable_indicator("nonexistent_id")
        assert len(engine._indicators) == initial

    def test_disabled_prevents_evaluate_trigger(self, engine):
        engine.disable_indicator("ti_approval_bypass_attempt")
        result = engine.evaluate_anomaly("agent-001", "approval_bypass", "medium", {})
        assert result is None

    def test_reenable_allows_evaluate_trigger(self, engine):
        engine.disable_indicator("ti_approval_bypass_attempt")
        engine.enable_indicator("ti_approval_bypass_attempt")
        result = engine.evaluate_anomaly("agent-001", "approval_bypass", "medium", {})
        assert result is not None


# ═══════════════════════════════════════════════════════════════════════════════
# ThreatResponseEngine.resolve_threat()
# ═══════════════════════════════════════════════════════════════════════════════

class TestResolveThreat:
    def test_resolve_unknown_event_returns_false(self, engine):
        assert engine.resolve_threat("nonexistent_id", "admin") is False

    def test_resolve_known_event_returns_true(self, engine):
        event = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert engine.resolve_threat(event.event_id, "admin@clawfilters.com") is True

    def test_resolved_flag_set(self, engine):
        event = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        engine.resolve_threat(event.event_id, "admin")
        assert event.resolved is True

    def test_human_reviewed_flag_set(self, engine):
        event = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        engine.resolve_threat(event.event_id, "admin")
        assert event.human_reviewed is True

    def test_human_reviewed_by_set(self, engine):
        event = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        engine.resolve_threat(event.event_id, "admin@clawfilters.com")
        assert event.human_reviewed_by == "admin@clawfilters.com"

    def test_human_reviewed_at_is_datetime(self, engine):
        event = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        engine.resolve_threat(event.event_id, "admin")
        assert isinstance(event.human_reviewed_at, datetime)

    def test_resolved_reflected_in_recent_threats(self, engine):
        event = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        engine.resolve_threat(event.event_id, "admin")
        threat_dict = next(
            t for t in engine.get_recent_threats()
            if t["event_id"] == event.event_id
        )
        assert threat_dict["resolved"] is True

    def test_resolve_reduces_unresolved_stats(self, engine):
        event = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        assert engine.get_threat_stats()["unresolved"] == 1
        engine.resolve_threat(event.event_id, "admin")
        assert engine.get_threat_stats()["unresolved"] == 0

    def test_resolve_second_time_also_returns_true(self, engine):
        # Resolving an already-resolved event is idempotent
        event = engine.evaluate_anomaly("agent-001", "approval_bypass", "critical", {})
        engine.resolve_threat(event.event_id, "admin")
        assert engine.resolve_threat(event.event_id, "admin2") is True
