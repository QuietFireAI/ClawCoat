# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_coverage_boost2.py
# REM: Coverage tests for manners.py, threat_response.py, and executor.py.

import pytest
from datetime import datetime, timedelta, timezone


# ═══════════════════════════════════════════════════════════════════════════════
# core/manners.py — Enums, data classes, MannersEngine
# ═══════════════════════════════════════════════════════════════════════════════

class TestMannersPrincipleEnum:
    def test_all_five_principles_exist(self):
        from core.manners import MannersPrinciple
        names = {p.name for p in MannersPrinciple}
        assert names == {
            "HUMAN_CONTROL", "TRANSPARENCY", "VALUE_ALIGNMENT", "PRIVACY", "SECURITY"
        }

    def test_values_have_manners_prefix(self):
        from core.manners import MannersPrinciple
        for p in MannersPrinciple:
            assert p.value.startswith("manners_")


class TestComplianceStatusEnum:
    def test_all_five_statuses_exist(self):
        from core.manners import ComplianceStatus
        names = {s.name for s in ComplianceStatus}
        assert names == {"EXEMPLARY", "COMPLIANT", "DEGRADED", "NON_COMPLIANT", "SUSPENDED"}

    def test_exemplary_value(self):
        from core.manners import ComplianceStatus
        assert ComplianceStatus.EXEMPLARY.value == "exemplary"

    def test_suspended_value(self):
        from core.manners import ComplianceStatus
        assert ComplianceStatus.SUSPENDED.value == "suspended"


class TestViolationTypeEnum:
    def test_all_fifteen_violation_types_exist(self):
        from core.manners import ViolationType
        assert len(list(ViolationType)) == 15

    def test_approval_bypass_exists(self):
        from core.manners import ViolationType
        assert ViolationType.APPROVAL_BYPASS.value == "approval_bypass"

    def test_injection_attempt_exists(self):
        from core.manners import ViolationType
        assert ViolationType.INJECTION_ATTEMPT.value == "injection_attempt"


class TestViolationMaps:
    def test_all_violation_types_in_principle_map(self):
        from core.manners import ViolationType, VIOLATION_PRINCIPLE_MAP
        for vt in ViolationType:
            assert vt in VIOLATION_PRINCIPLE_MAP

    def test_all_violation_types_have_severity(self):
        from core.manners import ViolationType, VIOLATION_SEVERITY
        for vt in ViolationType:
            assert vt in VIOLATION_SEVERITY
            assert 0.0 < VIOLATION_SEVERITY[vt] <= 1.0

    def test_approval_bypass_maps_to_human_control(self):
        from core.manners import ViolationType, MannersPrinciple, VIOLATION_PRINCIPLE_MAP
        assert VIOLATION_PRINCIPLE_MAP[ViolationType.APPROVAL_BYPASS] == MannersPrinciple.HUMAN_CONTROL

    def test_injection_attempt_maps_to_security(self):
        from core.manners import ViolationType, MannersPrinciple, VIOLATION_PRINCIPLE_MAP
        assert VIOLATION_PRINCIPLE_MAP[ViolationType.INJECTION_ATTEMPT] == MannersPrinciple.SECURITY

    def test_unauthorized_destructive_has_high_severity(self):
        from core.manners import ViolationType, VIOLATION_SEVERITY
        assert VIOLATION_SEVERITY[ViolationType.UNAUTHORIZED_DESTRUCTIVE] >= 0.30


class TestMannersViolation:
    def test_instantiation(self):
        from core.manners import (
            MannersViolation, ViolationType, MannersPrinciple, VIOLATION_PRINCIPLE_MAP, VIOLATION_SEVERITY
        )
        now = datetime.now(timezone.utc)
        vt = ViolationType.CAPABILITY_VIOLATION
        v = MannersViolation(
            agent_name="agent_test",
            violation_type=vt,
            principle=VIOLATION_PRINCIPLE_MAP[vt],
            severity=VIOLATION_SEVERITY[vt],
            timestamp=now,
            details="exceeded capability",
        )
        assert v.agent_name == "agent_test"
        assert v.auto_resolved is False
        assert v.action is None
        assert v.resource is None

    def test_to_dict_structure(self):
        from core.manners import (
            MannersViolation, ViolationType, MannersPrinciple, VIOLATION_PRINCIPLE_MAP, VIOLATION_SEVERITY
        )
        now = datetime.now(timezone.utc)
        vt = ViolationType.UNSIGNED_MESSAGE
        v = MannersViolation(
            agent_name="agent_x",
            violation_type=vt,
            principle=VIOLATION_PRINCIPLE_MAP[vt],
            severity=VIOLATION_SEVERITY[vt],
            timestamp=now,
            details="missing signature",
            action="send_message",
            resource="endpoint_a"
        )
        d = v.to_dict()
        assert d["agent_name"] == "agent_x"
        assert d["violation_type"] == "unsigned_message"
        assert d["action"] == "send_message"
        assert d["resource"] == "endpoint_a"
        assert d["auto_resolved"] is False
        assert "timestamp" in d


class TestPrincipleScore:
    def test_instantiation(self):
        from core.manners import PrincipleScore, MannersPrinciple
        ps = PrincipleScore(
            principle=MannersPrinciple.SECURITY,
            score=0.85,
            violations_count=2
        )
        assert ps.principle == MannersPrinciple.SECURITY
        assert ps.score == 0.85
        assert ps.violations_count == 2
        assert ps.last_violation is None


class TestMannersComplianceReport:
    def _make_report(self, score=1.0):
        from core.manners import (
            MannersComplianceReport, ComplianceStatus, MannersPrinciple, PrincipleScore
        )
        now = datetime.now(timezone.utc)
        principle_scores = {
            p.value: PrincipleScore(principle=p, score=score, violations_count=0)
            for p in MannersPrinciple
        }
        return MannersComplianceReport(
            agent_name="test_agent",
            overall_score=score,
            status=ComplianceStatus.EXEMPLARY,
            principle_scores=principle_scores,
            total_violations=0,
            violations_24h=0,
            evaluated_at=now,
        )

    def test_to_dict_has_required_keys(self):
        report = self._make_report()
        d = report.to_dict()
        assert "agent_name" in d
        assert "overall_score" in d
        assert "status" in d
        assert "principle_scores" in d
        assert "total_violations" in d
        assert "violations_24h" in d
        assert "evaluated_at" in d

    def test_to_dict_score_rounded(self):
        report = self._make_report(score=0.9876543)
        d = report.to_dict()
        assert d["overall_score"] == round(0.9876543, 3)

    def test_to_dict_status_is_string(self):
        report = self._make_report()
        d = report.to_dict()
        assert d["status"] == "exemplary"

    def test_to_dict_first_seen_none_when_not_set(self):
        report = self._make_report()
        d = report.to_dict()
        assert d["first_seen"] is None

    def test_to_dict_principle_scores_have_right_keys(self):
        report = self._make_report()
        d = report.to_dict()
        for key, ps in d["principle_scores"].items():
            assert "principle" in ps
            assert "score" in ps
            assert "violations_count" in ps
            assert "last_violation" in ps


class TestMannersEngine:
    def setup_method(self):
        from core.manners import MannersEngine
        self.engine = MannersEngine()

    def test_init_has_empty_state(self):
        assert self.engine._violations == {}
        assert self.engine._first_seen == {}

    def test_register_agent(self):
        self.engine.register_agent("new_agent")
        assert "new_agent" in self.engine._first_seen
        assert "new_agent" in self.engine._violations

    def test_register_agent_twice_does_not_reset(self):
        self.engine.register_agent("stable_agent")
        first_seen = self.engine._first_seen["stable_agent"]
        self.engine.register_agent("stable_agent")
        assert self.engine._first_seen["stable_agent"] == first_seen

    def test_record_violation_creates_entry(self):
        from unittest.mock import patch, MagicMock
        from core.manners import ViolationType
        with patch("core.manners.audit") as mock_audit:
            mock_audit.log = MagicMock()
            v = self.engine.record_violation(
                agent_name="agent_bad",
                violation_type=ViolationType.UNAUDITED_ACTION,
                details="agent skipped audit"
            )
        assert v.agent_name == "agent_bad"
        assert v.violation_type == ViolationType.UNAUDITED_ACTION
        assert len(self.engine._violations["agent_bad"]) == 1

    def test_record_violation_sets_principle_and_severity(self):
        from unittest.mock import patch, MagicMock
        from core.manners import ViolationType, MannersPrinciple, VIOLATION_SEVERITY
        with patch("core.manners.audit") as mock_audit:
            mock_audit.log = MagicMock()
            v = self.engine.record_violation(
                agent_name="agent_x",
                violation_type=ViolationType.CROSS_TENANT_ACCESS,
                details="cross-tenant read"
            )
        assert v.principle == MannersPrinciple.PRIVACY
        assert v.severity == VIOLATION_SEVERITY[ViolationType.CROSS_TENANT_ACCESS]

    def test_evaluate_clean_agent_scores_1(self):
        self.engine.register_agent("clean_agent")
        report = self.engine.evaluate("clean_agent")
        assert report.overall_score == 1.0
        assert report.total_violations == 0

    def test_evaluate_agent_with_violation_scores_less(self):
        from unittest.mock import patch, MagicMock
        from core.manners import ViolationType
        self.engine.register_agent("bad_agent")
        with patch("core.manners.audit") as mock_audit:
            mock_audit.log = MagicMock()
            self.engine.record_violation(
                "bad_agent", ViolationType.APPROVAL_BYPASS, "bypassed"
            )
        report = self.engine.evaluate("bad_agent")
        assert report.overall_score < 1.0

    def test_evaluate_uses_cache_on_second_call(self):
        self.engine.register_agent("cached_agent")
        report1 = self.engine.evaluate("cached_agent")
        report2 = self.engine.evaluate("cached_agent")
        # Same object returned from cache
        assert report1 is report2

    def test_evaluate_all_returns_list(self):
        self.engine.register_agent("agent_a")
        self.engine.register_agent("agent_b")
        reports = self.engine.evaluate_all()
        assert len(reports) == 2

    def test_score_to_status_exemplary(self):
        from core.manners import ComplianceStatus
        status = self.engine._score_to_status(0.95)
        assert status == ComplianceStatus.EXEMPLARY

    def test_score_to_status_compliant(self):
        from core.manners import ComplianceStatus
        status = self.engine._score_to_status(0.80)
        assert status == ComplianceStatus.COMPLIANT

    def test_score_to_status_degraded(self):
        from core.manners import ComplianceStatus
        status = self.engine._score_to_status(0.60)
        assert status == ComplianceStatus.DEGRADED

    def test_score_to_status_non_compliant(self):
        from core.manners import ComplianceStatus
        status = self.engine._score_to_status(0.30)
        assert status == ComplianceStatus.NON_COMPLIANT

    def test_score_to_status_suspended(self):
        from core.manners import ComplianceStatus
        status = self.engine._score_to_status(0.10)
        assert status == ComplianceStatus.SUSPENDED

    def test_get_violations_filters_by_agent(self):
        from unittest.mock import patch, MagicMock
        from core.manners import ViolationType
        with patch("core.manners.audit") as mock_audit:
            mock_audit.log = MagicMock()
            self.engine.record_violation("agent_1", ViolationType.UNAUDITED_ACTION, "d1")
            self.engine.record_violation("agent_2", ViolationType.NON_QMS_MESSAGE, "d2")
        viols = self.engine.get_violations("agent_1")
        assert len(viols) == 1
        assert viols[0].agent_name == "agent_1"

    def test_get_compliance_summary_returns_dict(self):
        self.engine.register_agent("summary_agent")
        summary = self.engine.get_compliance_summary()
        assert isinstance(summary, dict)

    def test_check_action_allowed_clean_agent(self):
        self.engine.register_agent("allowed_agent")
        allowed, reason = self.engine.check_action_allowed("allowed_agent", "read_data")
        assert allowed is True

    def test_new_agent_grace_period_is_tracked(self):
        self.engine.register_agent("new_fresh_agent")
        report = self.engine.evaluate("new_fresh_agent")
        # New agent within 24h should be in grace period
        assert report.is_grace_period is True


# ═══════════════════════════════════════════════════════════════════════════════
# core/threat_response.py — ThreatLevel, ResponseAction, data classes, engine
# ═══════════════════════════════════════════════════════════════════════════════

class TestThreatLevelEnum:
    def test_all_five_levels_exist(self):
        from core.threat_response import ThreatLevel
        names = {t.name for t in ThreatLevel}
        assert names == {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"}

    def test_values_lowercase(self):
        from core.threat_response import ThreatLevel
        for t in ThreatLevel:
            assert t.value == t.value.lower()


class TestResponseActionEnum:
    def test_all_seven_actions_exist(self):
        from core.threat_response import ResponseAction
        names = {a.name for a in ResponseAction}
        assert names == {
            "QUARANTINE", "DEMOTE", "RATE_LIMIT", "REVOKE_DELEGATIONS",
            "BLOCK_EXTERNAL", "ALERT", "LOG"
        }

    def test_quarantine_value(self):
        from core.threat_response import ResponseAction
        assert ResponseAction.QUARANTINE.value == "quarantine"


class TestThreatIndicator:
    def test_instantiation_with_defaults(self):
        from core.threat_response import ThreatIndicator, ThreatLevel, ResponseAction
        ind = ThreatIndicator(
            indicator_id="test_ind",
            name="Test Indicator",
            description="A test threat indicator",
            threat_level=ThreatLevel.HIGH,
            pattern={"count_threshold": 5},
            response_actions=[ResponseAction.ALERT]
        )
        assert ind.enabled is True
        assert ind.cooldown_minutes == 5

    def test_default_indicators_not_empty(self):
        from core.threat_response import DEFAULT_INDICATORS
        assert len(DEFAULT_INDICATORS) > 0

    def test_each_default_indicator_has_response_actions(self):
        from core.threat_response import DEFAULT_INDICATORS
        for ind in DEFAULT_INDICATORS:
            assert len(ind.response_actions) > 0
            assert ind.indicator_id
            assert ind.threat_level


class TestThreatEvent:
    def test_instantiation(self):
        from core.threat_response import ThreatEvent, ThreatLevel
        import uuid
        now = datetime.now(timezone.utc)
        event = ThreatEvent(
            event_id=str(uuid.uuid4()),
            indicator_id="ti_test",
            threat_level=ThreatLevel.HIGH,
            agent_id="agent_123",
            description="Test threat",
            evidence={"count": 5},
            detected_at=now
        )
        assert event.human_reviewed is False
        assert event.resolved is False
        assert event.response_actions_taken == []


class TestResponsePolicy:
    def test_default_policies_have_all_levels(self):
        from core.threat_response import DEFAULT_POLICIES, ThreatLevel
        for level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH, ThreatLevel.MEDIUM, ThreatLevel.LOW]:
            assert level in DEFAULT_POLICIES

    def test_critical_policy_does_not_require_confirmation(self):
        from core.threat_response import DEFAULT_POLICIES, ThreatLevel
        policy = DEFAULT_POLICIES[ThreatLevel.CRITICAL]
        assert policy.require_confirmation is False

    def test_medium_policy_requires_confirmation(self):
        from core.threat_response import DEFAULT_POLICIES, ThreatLevel
        policy = DEFAULT_POLICIES[ThreatLevel.MEDIUM]
        assert policy.require_confirmation is True


class TestThreatResponseEngine:
    def setup_method(self):
        from core.threat_response import ThreatResponseEngine
        self.engine = ThreatResponseEngine()

    def test_init_loads_default_indicators(self):
        from core.threat_response import DEFAULT_INDICATORS
        for ind in DEFAULT_INDICATORS:
            assert ind.indicator_id in self.engine._indicators

    def test_get_recent_threats_empty_initially(self):
        threats = self.engine.get_recent_threats()
        assert threats == []

    def test_get_threat_stats_empty(self):
        stats = self.engine.get_threat_stats()
        assert stats["total_threats"] == 0
        assert stats["last_24h"] == 0
        assert stats["unresolved"] == 0
        assert "by_level" in stats

    def test_add_custom_indicator(self):
        from core.threat_response import ThreatIndicator, ThreatLevel, ResponseAction
        ind = ThreatIndicator(
            indicator_id="custom_ind_001",
            name="Custom Indicator",
            description="A custom indicator",
            threat_level=ThreatLevel.LOW,
            pattern={"type": "custom"},
            response_actions=[ResponseAction.LOG]
        )
        self.engine.add_indicator(ind)
        assert "custom_ind_001" in self.engine._indicators

    def test_disable_indicator(self):
        indicator_id = "ti_critical_anomaly_burst"
        self.engine.disable_indicator(indicator_id)
        assert self.engine._indicators[indicator_id].enabled is False
        # Restore shared state — DEFAULT_INDICATORS objects are shared references
        self.engine.enable_indicator(indicator_id)

    def test_enable_indicator_after_disable(self):
        indicator_id = "ti_capability_probing"
        self.engine.disable_indicator(indicator_id)
        self.engine.enable_indicator(indicator_id)
        assert self.engine._indicators[indicator_id].enabled is True

    def test_disable_nonexistent_indicator_does_not_raise(self):
        # Should not raise - just silently ignores unknown IDs
        self.engine.disable_indicator("nonexistent_indicator_id")

    def test_handle_alert_returns_true(self):
        from core.threat_response import ThreatEvent, ThreatLevel
        import uuid
        event = ThreatEvent(
            event_id=str(uuid.uuid4()),
            indicator_id="ti_test",
            threat_level=ThreatLevel.LOW,
            agent_id="agent_a",
            description="Test alert",
            evidence={},
            detected_at=datetime.now(timezone.utc)
        )
        result = self.engine._handle_alert("agent_a", event)
        assert result is True

    def test_handle_log_returns_true(self):
        from core.threat_response import ThreatEvent, ThreatLevel
        import uuid
        event = ThreatEvent(
            event_id=str(uuid.uuid4()),
            indicator_id="ti_test",
            threat_level=ThreatLevel.INFO,
            agent_id="agent_b",
            description="Test log",
            evidence={},
            detected_at=datetime.now(timezone.utc)
        )
        result = self.engine._handle_log("agent_b", event)
        assert result is True

    def test_handle_block_external_returns_false(self):
        # Stub: not yet implemented, returns False
        from core.threat_response import ThreatEvent, ThreatLevel
        import uuid
        event = ThreatEvent(
            event_id=str(uuid.uuid4()),
            indicator_id="ti_test",
            threat_level=ThreatLevel.HIGH,
            agent_id="agent_c",
            description="Block test",
            evidence={},
            detected_at=datetime.now(timezone.utc)
        )
        result = self.engine._handle_block_external("agent_c", event)
        assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# toolroom/executor.py — ExecutionResult, execute_function_tool, constants
# ═══════════════════════════════════════════════════════════════════════════════

class TestExecutionResultDataclass:
    def test_instantiation_with_defaults(self):
        from toolroom.executor import ExecutionResult
        result = ExecutionResult(tool_id="test_tool", success=True)
        assert result.exit_code == 0
        assert result.stdout == ""
        assert result.stderr == ""
        assert result.duration_seconds == 0.0
        assert result.error_message == ""
        assert result.output_data == {}

    def test_to_dict_has_all_fields(self):
        from toolroom.executor import ExecutionResult
        result = ExecutionResult(
            tool_id="my_tool",
            success=True,
            exit_code=0,
            stdout="hello",
            stderr="",
            duration_seconds=0.15,
            output_data={"key": "value"}
        )
        d = result.to_dict()
        assert d["tool_id"] == "my_tool"
        assert d["success"] is True
        assert d["exit_code"] == 0
        assert d["stdout"] == "hello"
        assert d["duration_seconds"] == 0.15
        assert d["output_data"] == {"key": "value"}

    def test_failed_result(self):
        from toolroom.executor import ExecutionResult
        result = ExecutionResult(
            tool_id="fail_tool",
            success=False,
            exit_code=-1,
            error_message="timed out"
        )
        assert result.success is False
        d = result.to_dict()
        assert d["error_message"] == "timed out"


class TestExecutorConstants:
    def test_blocked_env_vars_contains_secrets(self):
        from toolroom.executor import BLOCKED_ENV_VARS
        assert "MCP_API_KEY" in BLOCKED_ENV_VARS
        assert "JWT_SECRET_KEY" in BLOCKED_ENV_VARS
        assert "DATABASE_URL" in BLOCKED_ENV_VARS

    def test_restricted_path_does_not_include_opt(self):
        from toolroom.executor import RESTRICTED_PATH
        assert "/opt" not in RESTRICTED_PATH
        assert "/usr/local/bin" in RESTRICTED_PATH


class TestExecuteFunctionTool:
    def test_successful_function_returns_dict_output(self):
        from toolroom.executor import execute_function_tool

        def my_func(x, y):
            return {"sum": x + y}

        result = execute_function_tool(
            tool_id="add_tool",
            func=my_func,
            inputs={"x": 3, "y": 4},
            agent_id="test_agent"
        )
        assert result.success is True
        assert result.exit_code == 0
        assert result.output_data == {"sum": 7}
        assert result.duration_seconds >= 0

    def test_function_returning_string_wraps_in_dict(self):
        from toolroom.executor import execute_function_tool

        def greet(name):
            return f"Hello, {name}!"

        result = execute_function_tool(
            tool_id="greet_tool",
            func=greet,
            inputs={"name": "world"}
        )
        assert result.success is True
        assert result.output_data == {"result": "Hello, world!"}

    def test_function_returning_none_gives_empty_output(self):
        from toolroom.executor import execute_function_tool

        def do_nothing():
            return None

        result = execute_function_tool(
            tool_id="noop_tool",
            func=do_nothing,
            inputs={}
        )
        assert result.success is True
        assert result.output_data == {}

    def test_function_raising_exception_returns_failure(self):
        from toolroom.executor import execute_function_tool

        def fail_func():
            raise ValueError("something went wrong")

        result = execute_function_tool(
            tool_id="fail_tool",
            func=fail_func,
            inputs={}
        )
        assert result.success is False
        assert result.exit_code == -1
        assert "something went wrong" in result.error_message

    def test_function_non_dict_non_str_result_converts_to_string(self):
        from toolroom.executor import execute_function_tool

        def return_number():
            return 42

        result = execute_function_tool(
            tool_id="num_tool",
            func=return_number,
            inputs={}
        )
        assert result.success is True
        assert result.output_data == {"result": "42"}
