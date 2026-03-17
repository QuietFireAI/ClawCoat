# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_coverage_boost.py
# REM: Coverage tests for pure-Python modules currently at 0% or low coverage.
# REM: Targets: compliance.py, semantic_matching.py, rotation.py (dataclasses),
# REM:          auth_dependencies helpers, tenant_rate_limiting._InMemoryBucket,
# REM:          alias wrapper modules.

import pytest
from datetime import datetime, timedelta, timezone


# ═══════════════════════════════════════════════════════════════════════════════
# core/compliance.py — ComplianceFramework, ControlStatus, dataclasses, engine
# ═══════════════════════════════════════════════════════════════════════════════

class TestComplianceFrameworkEnum:
    def test_all_four_frameworks_exist(self):
        from core.compliance import ComplianceFramework
        names = {f.name for f in ComplianceFramework}
        assert names == {"SOC2", "ISO27001", "NIST", "CUSTOM"}

    def test_values_are_lowercase_strings(self):
        from core.compliance import ComplianceFramework
        for f in ComplianceFramework:
            assert f.value == f.value.lower()

    def test_soc2_value(self):
        from core.compliance import ComplianceFramework
        assert ComplianceFramework.SOC2.value == "soc2"

    def test_iso_value(self):
        from core.compliance import ComplianceFramework
        assert ComplianceFramework.ISO27001.value == "iso27001"


class TestControlStatusEnum:
    def test_all_five_statuses_exist(self):
        from core.compliance import ControlStatus
        names = {s.name for s in ControlStatus}
        assert names == {"COMPLIANT", "PARTIAL", "NON_COMPLIANT", "NOT_APPLICABLE", "NEEDS_EVIDENCE"}

    def test_default_status_is_needs_evidence(self):
        from core.compliance import ComplianceControl, ComplianceFramework, ControlStatus
        ctrl = ComplianceControl(
            control_id="CC6.1",
            framework=ComplianceFramework.SOC2,
            title="Test",
            description="desc",
            category="Access",
            evidence_required=["logs"]
        )
        assert ctrl.status == ControlStatus.NEEDS_EVIDENCE


class TestComplianceControl:
    def test_instantiation_with_defaults(self):
        from core.compliance import ComplianceControl, ComplianceFramework, ControlStatus
        ctrl = ComplianceControl(
            control_id="CC7.1",
            framework=ComplianceFramework.SOC2,
            title="Monitoring",
            description="Monitor events",
            category="Operations",
            evidence_required=["anomaly_detection", "security_alerts"]
        )
        assert ctrl.control_id == "CC7.1"
        assert ctrl.framework == ComplianceFramework.SOC2
        assert ctrl.evidence_collected == []
        assert ctrl.notes == ""
        assert ctrl.last_assessed is None
        assert ctrl.assessor is None
        assert ctrl.status == ControlStatus.NEEDS_EVIDENCE

    def test_instantiation_with_all_fields(self):
        from core.compliance import ComplianceControl, ComplianceFramework, ControlStatus
        now = datetime.now(timezone.utc)
        ctrl = ComplianceControl(
            control_id="CC6.2",
            framework=ComplianceFramework.SOC2,
            title="New User",
            description="Register users",
            category="Access",
            evidence_required=["agent_registration"],
            status=ControlStatus.COMPLIANT,
            evidence_collected=[{"type": "log", "count": 5}],
            notes="Verified manually",
            last_assessed=now,
            assessor="admin"
        )
        assert ctrl.status == ControlStatus.COMPLIANT
        assert len(ctrl.evidence_collected) == 1
        assert ctrl.assessor == "admin"


class TestSOC2Controls:
    def test_soc2_controls_list_not_empty(self):
        from core.compliance import SOC2_CONTROLS
        assert len(SOC2_CONTROLS) > 0

    def test_each_control_has_required_fields(self):
        from core.compliance import SOC2_CONTROLS
        for ctrl in SOC2_CONTROLS:
            assert "control_id" in ctrl
            assert "category" in ctrl
            assert "title" in ctrl
            assert "description" in ctrl
            assert "evidence_required" in ctrl
            assert isinstance(ctrl["evidence_required"], list)

    def test_cc6_controls_present(self):
        from core.compliance import SOC2_CONTROLS
        ids = {c["control_id"] for c in SOC2_CONTROLS}
        assert "CC6.1" in ids
        assert "CC6.2" in ids
        assert "CC6.3" in ids


class TestComplianceReport:
    def _make_report(self):
        from core.compliance import (
            ComplianceControl, ComplianceFramework, ComplianceReport, ControlStatus
        )
        now = datetime.now(timezone.utc)
        ctrl = ComplianceControl(
            control_id="CC6.1",
            framework=ComplianceFramework.SOC2,
            title="Logical Access",
            description="desc",
            category="Access",
            evidence_required=["logs"],
            status=ControlStatus.COMPLIANT,
            last_assessed=now
        )
        return ComplianceReport(
            report_id="rpt_soc2_abc12345",
            framework=ComplianceFramework.SOC2,
            generated_at=now,
            generated_by="test_runner",
            period_start=now - timedelta(days=30),
            period_end=now,
            controls=[ctrl],
            summary={"total_controls": 1, "compliant": 1, "compliance_percentage": 100.0},
            evidence_summary={"logs": 3}
        )

    def test_to_dict_has_required_keys(self):
        report = self._make_report()
        d = report.to_dict()
        assert "report_id" in d
        assert "framework" in d
        assert "generated_at" in d
        assert "generated_by" in d
        assert "period" in d
        assert "summary" in d
        assert "evidence_summary" in d
        assert "controls" in d

    def test_to_dict_framework_is_string(self):
        report = self._make_report()
        d = report.to_dict()
        assert d["framework"] == "soc2"

    def test_to_dict_period_has_start_and_end(self):
        report = self._make_report()
        d = report.to_dict()
        assert "start" in d["period"]
        assert "end" in d["period"]

    def test_to_dict_controls_list_with_control_detail(self):
        report = self._make_report()
        d = report.to_dict()
        assert len(d["controls"]) == 1
        ctrl = d["controls"][0]
        assert ctrl["control_id"] == "CC6.1"
        assert ctrl["status"] == "compliant"
        assert "evidence_count" in ctrl
        assert "last_assessed" in ctrl

    def test_to_dict_control_with_no_last_assessed_is_none(self):
        from core.compliance import (
            ComplianceControl, ComplianceFramework, ComplianceReport, ControlStatus
        )
        now = datetime.now(timezone.utc)
        ctrl = ComplianceControl(
            control_id="CC6.2",
            framework=ComplianceFramework.SOC2,
            title="T",
            description="D",
            category="C",
            evidence_required=[],
        )
        report = ComplianceReport(
            report_id="rpt_test",
            framework=ComplianceFramework.SOC2,
            generated_at=now,
            generated_by="system",
            period_start=now - timedelta(days=7),
            period_end=now,
            controls=[ctrl],
            summary={},
            evidence_summary={}
        )
        d = report.to_dict()
        assert d["controls"][0]["last_assessed"] is None


class TestComplianceEngine:
    def setup_method(self):
        from core.compliance import ComplianceEngine
        self.engine = ComplianceEngine()

    def test_register_and_retrieve_evidence_source(self):
        self.engine.register_evidence_source("test_type", lambda s, e: [{"type": "test"}])
        assert "test_type" in self.engine._evidence_sources

    def test_collect_evidence_calls_registered_source(self):
        now = datetime.now(timezone.utc)
        self.engine.register_evidence_source("auth_logs", lambda s, e: [{"count": 5}])
        results = self.engine.collect_evidence("auth_logs", now - timedelta(hours=1), now)
        assert len(results) == 1
        assert results[0]["count"] == 5

    def test_collect_evidence_unknown_type_returns_empty(self):
        now = datetime.now(timezone.utc)
        results = self.engine.collect_evidence("nonexistent_type", now, now)
        assert results == []

    def test_collect_evidence_failed_collector_returns_empty(self):
        now = datetime.now(timezone.utc)
        def bad_collector(s, e):
            raise RuntimeError("boom")
        self.engine.register_evidence_source("bad", bad_collector)
        results = self.engine.collect_evidence("bad", now, now)
        assert results == []

    def test_assess_control_no_evidence_gives_needs_evidence(self):
        from core.compliance import ComplianceControl, ComplianceFramework, ControlStatus
        now = datetime.now(timezone.utc)
        ctrl = ComplianceControl(
            control_id="CC6.1",
            framework=ComplianceFramework.SOC2,
            title="T",
            description="D",
            category="C",
            evidence_required=["unknown_evidence_type"]
        )
        assessed = self.engine.assess_control(ctrl, now - timedelta(days=1), now)
        assert assessed.status == ControlStatus.NEEDS_EVIDENCE
        assert assessed.last_assessed is not None

    def test_assess_control_with_evidence_gives_compliant(self):
        from core.compliance import ComplianceControl, ComplianceFramework, ControlStatus
        now = datetime.now(timezone.utc)
        self.engine.register_evidence_source("logs", lambda s, e: [{"type": "log"}])
        ctrl = ComplianceControl(
            control_id="CC7.1",
            framework=ComplianceFramework.SOC2,
            title="T",
            description="D",
            category="C",
            evidence_required=["logs"]
        )
        assessed = self.engine.assess_control(ctrl, now - timedelta(days=1), now)
        assert assessed.status == ControlStatus.COMPLIANT

    def test_assess_control_partial_evidence_gives_partial(self):
        from core.compliance import ComplianceControl, ComplianceFramework, ControlStatus
        now = datetime.now(timezone.utc)
        self.engine.register_evidence_source("some_type", lambda s, e: [{"type": "some"}])
        ctrl = ComplianceControl(
            control_id="CC7.2",
            framework=ComplianceFramework.SOC2,
            title="T",
            description="D",
            category="C",
            evidence_required=["some_type", "missing_type"]
        )
        assessed = self.engine.assess_control(ctrl, now - timedelta(days=1), now)
        assert assessed.status == ControlStatus.PARTIAL

    def test_generate_soc2_report_returns_report(self):
        from core.compliance import ComplianceFramework
        now = datetime.now(timezone.utc)
        report = self.engine.generate_report(
            ComplianceFramework.SOC2,
            now - timedelta(days=30),
            now,
            generated_by="test"
        )
        assert report.framework == ComplianceFramework.SOC2
        assert report.generated_by == "test"
        assert len(report.controls) > 0
        assert "total_controls" in report.summary
        assert "compliance_percentage" in report.summary

    def test_generate_report_non_soc2_has_no_controls(self):
        from core.compliance import ComplianceFramework
        now = datetime.now(timezone.utc)
        report = self.engine.generate_report(
            ComplianceFramework.ISO27001,
            now - timedelta(days=30),
            now
        )
        assert len(report.controls) == 0
        assert report.summary["total_controls"] == 0

    def test_get_report_after_generate(self):
        from core.compliance import ComplianceFramework
        now = datetime.now(timezone.utc)
        report = self.engine.generate_report(
            ComplianceFramework.SOC2,
            now - timedelta(days=7),
            now
        )
        fetched = self.engine.get_report(report.report_id)
        assert fetched is not None
        assert fetched.report_id == report.report_id

    def test_get_report_unknown_id_returns_none(self):
        assert self.engine.get_report("nonexistent_id") is None

    def test_list_reports_empty_initially(self):
        engine = type(self.engine)()  # fresh instance
        reports = engine.list_reports()
        assert reports == []

    def test_list_reports_after_generate(self):
        from core.compliance import ComplianceFramework
        now = datetime.now(timezone.utc)
        self.engine.generate_report(ComplianceFramework.SOC2, now - timedelta(days=7), now)
        reports = self.engine.list_reports()
        assert len(reports) == 1
        assert "report_id" in reports[0]
        assert "compliance_percentage" in reports[0]

    def test_list_reports_filters_by_framework(self):
        from core.compliance import ComplianceFramework
        now = datetime.now(timezone.utc)
        self.engine.generate_report(ComplianceFramework.SOC2, now - timedelta(days=7), now)
        self.engine.generate_report(ComplianceFramework.ISO27001, now - timedelta(days=7), now)
        soc2_reports = self.engine.list_reports(framework=ComplianceFramework.SOC2)
        iso_reports = self.engine.list_reports(framework=ComplianceFramework.ISO27001)
        assert len(soc2_reports) == 1
        assert len(iso_reports) == 1

    def test_export_report_json_returns_json_string(self):
        import json
        from core.compliance import ComplianceFramework
        now = datetime.now(timezone.utc)
        report = self.engine.generate_report(ComplianceFramework.SOC2, now - timedelta(days=1), now)
        json_str = self.engine.export_report_json(report.report_id)
        assert json_str is not None
        parsed = json.loads(json_str)
        assert parsed["report_id"] == report.report_id

    def test_export_report_json_unknown_id_returns_none(self):
        assert self.engine.export_report_json("bad_id") is None

    def test_get_evidence_requirements_soc2(self):
        reqs = self.engine.get_evidence_requirements(
            __import__("core.compliance", fromlist=["ComplianceFramework"]).ComplianceFramework.SOC2
        )
        assert len(reqs) > 0
        for req in reqs:
            assert "type" in req
            assert "registered" in req

    def test_get_evidence_requirements_iso_returns_empty(self):
        from core.compliance import ComplianceFramework
        reqs = self.engine.get_evidence_requirements(ComplianceFramework.ISO27001)
        assert reqs == []


# ═══════════════════════════════════════════════════════════════════════════════
# core/semantic_matching.py — SemanticMatcher full logic
# ═══════════════════════════════════════════════════════════════════════════════

class TestMatchStrictnessEnum:
    def test_all_three_values_exist(self):
        from core.semantic_matching import MatchStrictness
        names = {s.name for s in MatchStrictness}
        assert names == {"STRICT", "STANDARD", "RELAXED"}

    def test_values_are_lowercase(self):
        from core.semantic_matching import MatchStrictness
        for s in MatchStrictness:
            assert s.value == s.value.lower()


class TestActionSynonyms:
    def test_read_synonyms_include_view_and_get(self):
        from core.semantic_matching import ACTION_SYNONYMS
        assert "view" in ACTION_SYNONYMS["read"]
        assert "get" in ACTION_SYNONYMS["read"]

    def test_delete_synonyms_include_remove(self):
        from core.semantic_matching import ACTION_SYNONYMS
        assert "remove" in ACTION_SYNONYMS["delete"]

    def test_canonical_lookup_built(self):
        from core.semantic_matching import _SYNONYM_TO_CANONICAL
        assert _SYNONYM_TO_CANONICAL["view"] == "read"
        assert _SYNONYM_TO_CANONICAL["remove"] == "delete"
        assert _SYNONYM_TO_CANONICAL["read"] == "read"


class TestMatchResult:
    def test_instantiation(self):
        from core.semantic_matching import MatchResult
        r = MatchResult(
            matched=True,
            capability="filesystem.read:/data",
            required="file.view:/data/report.txt",
            match_type="hierarchy",
            confidence=0.90
        )
        assert r.matched is True
        assert r.confidence == 0.90
        assert r.canonical_action is None
        assert r.details == {}


class TestSemanticMatcherCanonicalizeAction:
    def setup_method(self):
        from core.semantic_matching import SemanticMatcher
        self.matcher = SemanticMatcher()

    def test_canonical_read(self):
        assert self.matcher.canonicalize_action("view") == "read"

    def test_canonical_delete(self):
        assert self.matcher.canonicalize_action("remove") == "delete"

    def test_unknown_action_returned_as_is(self):
        assert self.matcher.canonicalize_action("analyze") == "analyze"

    def test_case_insensitive(self):
        assert self.matcher.canonicalize_action("VIEW") == "read"


class TestSemanticMatcherResourceAncestors:
    def setup_method(self):
        from core.semantic_matching import SemanticMatcher
        self.matcher = SemanticMatcher()

    def test_file_ancestry_chain(self):
        ancestors = self.matcher.get_resource_ancestors("file")
        assert "file" in ancestors
        assert "filesystem" in ancestors

    def test_document_ancestry_chain(self):
        ancestors = self.matcher.get_resource_ancestors("document")
        assert "document" in ancestors
        assert "file" in ancestors
        assert "filesystem" in ancestors

    def test_unknown_resource_returns_just_itself(self):
        ancestors = self.matcher.get_resource_ancestors("custom_thing")
        assert ancestors == ["custom_thing"]


class TestSemanticMatcherNormalizePath:
    def setup_method(self):
        from core.semantic_matching import SemanticMatcher
        self.matcher = SemanticMatcher()

    def test_empty_path_returns_empty(self):
        assert self.matcher.normalize_path("") == ""

    def test_backslash_normalized(self):
        result = self.matcher.normalize_path("data\\reports\\file.txt")
        assert "\\" not in result

    def test_double_slashes_collapsed(self):
        result = self.matcher.normalize_path("/data//reports//file.txt")
        assert "//" not in result

    def test_trailing_slash_stripped(self):
        result = self.matcher.normalize_path("/data/reports/")
        assert not result.endswith("/")


class TestSemanticMatcherPathMatches:
    def setup_method(self):
        from core.semantic_matching import SemanticMatcher
        self.matcher = SemanticMatcher()

    def test_exact_match(self):
        assert self.matcher.path_matches("/data/file.txt", "/data/file.txt")

    def test_wildcard_star_matches_in_dir(self):
        assert self.matcher.path_matches("/data/*", "/data/file.txt")

    def test_wildcard_star_matches_prefix_path(self):
        # The /* pattern matches anything starting with the prefix (including subdirs)
        assert self.matcher.path_matches("/data/*", "/data/sub/file.txt")

    def test_double_star_matches_subdir(self):
        assert self.matcher.path_matches("/data/**", "/data/sub/file.txt")

    def test_no_match_different_paths(self):
        assert not self.matcher.path_matches("/docs/*", "/data/file.txt")


class TestSemanticMatcherMatchCapability:
    def setup_method(self):
        from core.semantic_matching import SemanticMatcher
        self.matcher = SemanticMatcher()

    def test_exact_match(self):
        result = self.matcher.match_capability("filesystem.read:/data", "filesystem.read:/data")
        assert result.matched is True
        assert result.match_type == "exact"
        assert result.confidence == 1.0

    def test_synonym_action_match(self):
        result = self.matcher.match_capability("filesystem.read:/data", "filesystem.view:/data")
        assert result.matched is True
        assert result.match_type == "synonym"

    def test_hierarchy_resource_match(self):
        result = self.matcher.match_capability("filesystem.read:/data", "file.read:/data")
        assert result.matched is True
        assert result.match_type == "hierarchy"

    def test_action_mismatch_returns_false(self):
        result = self.matcher.match_capability("filesystem.read:/data", "filesystem.write:/data")
        assert result.matched is False
        assert result.match_type == "action_mismatch"

    def test_resource_mismatch_returns_false(self):
        result = self.matcher.match_capability("database.read", "filesystem.read")
        assert result.matched is False
        assert result.match_type == "resource_mismatch"

    def test_path_mismatch_returns_false(self):
        result = self.matcher.match_capability("filesystem.read:/data/a", "filesystem.read:/data/b")
        assert result.matched is False
        assert result.match_type == "path_mismatch"

    def test_wildcard_action_matches_anything(self):
        result = self.matcher.match_capability("filesystem.*", "filesystem.read")
        assert result.matched is True

    def test_strict_mode_rejects_hierarchy_resource_matches(self):
        # STRICT mode prevents hierarchy: holding 'filesystem' doesn't match required 'file'
        from core.semantic_matching import MatchStrictness, SemanticMatcher
        strict = SemanticMatcher(strictness=MatchStrictness.STRICT)
        result = strict.match_capability("external.read", "api.read")
        # 'api' is a child of 'external', but STRICT mode rejects hierarchy
        assert result.matched is False


class TestSemanticMatcherFindBest:
    def setup_method(self):
        from core.semantic_matching import SemanticMatcher
        self.matcher = SemanticMatcher()

    def test_find_matching_capability_returns_best(self):
        held = ["filesystem.read:/data/*", "database.write:/tables/users"]
        result = self.matcher.find_matching_capability(held, "filesystem.read:/data/report.txt")
        assert result is not None
        assert result.matched is True

    def test_find_matching_capability_returns_none_when_no_match(self):
        held = ["filesystem.write:/data"]
        result = self.matcher.find_matching_capability(held, "database.read:/tables")
        assert result is None


class TestSemanticMatcherCustomSynonymsAndHierarchy:
    def setup_method(self):
        from core.semantic_matching import SemanticMatcher
        self.matcher = SemanticMatcher()

    def test_add_custom_synonym(self):
        self.matcher.add_custom_synonym("read", ["examine"])
        from core.semantic_matching import _SYNONYM_TO_CANONICAL
        assert _SYNONYM_TO_CANONICAL.get("examine") == "read"

    def test_add_custom_hierarchy(self):
        self.matcher.add_custom_hierarchy("report", "document")
        ancestors = self.matcher.get_resource_ancestors("report")
        assert "document" in ancestors


class TestSemanticMatcherExplain:
    def setup_method(self):
        from core.semantic_matching import SemanticMatcher
        self.matcher = SemanticMatcher()

    def test_explain_match_contains_match_word(self):
        result = self.matcher.match_capability("filesystem.read:/data", "filesystem.read:/data")
        explanation = self.matcher.explain_match(result)
        assert "MATCH" in explanation

    def test_explain_no_match_contains_no_match(self):
        result = self.matcher.match_capability("filesystem.read", "database.write")
        explanation = self.matcher.explain_match(result)
        assert "NO MATCH" in explanation


class TestCheckCapabilitySemantic:
    def test_matching_capability_returns_true(self):
        from core.semantic_matching import check_capability_semantic
        ok, result = check_capability_semantic(
            ["filesystem.read:/data/*"],
            "filesystem.read:/data/file.txt",
            agent_id="agent_001"
        )
        assert ok is True
        assert result is not None

    def test_no_matching_capability_returns_false(self):
        from core.semantic_matching import check_capability_semantic
        ok, result = check_capability_semantic(
            ["database.write"],
            "filesystem.read:/data",
        )
        assert ok is False


# ═══════════════════════════════════════════════════════════════════════════════
# core/rotation.py — SecretType, RotationRecord, ActiveSecret (pure dataclasses)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSecretTypeEnum:
    def test_all_four_types_exist(self):
        from core.rotation import SecretType
        names = {s.name for s in SecretType}
        assert names == {"JWT_SECRET", "AGENT_SIGNING_KEY", "FEDERATION_SESSION", "API_KEY"}

    def test_values_are_lowercase(self):
        from core.rotation import SecretType
        for s in SecretType:
            assert s.value == s.value.lower()


class TestActiveSecret:
    def test_is_in_grace_period_false_when_no_previous_key(self):
        from core.rotation import ActiveSecret
        now = datetime.now(timezone.utc)
        secret = ActiveSecret(
            current_key=b"current_secret_key",
            current_key_created_at=now
        )
        assert secret.is_in_grace_period() is False

    def test_is_in_grace_period_true_when_previous_key_not_expired(self):
        from core.rotation import ActiveSecret
        now = datetime.now(timezone.utc)
        secret = ActiveSecret(
            current_key=b"new_key",
            current_key_created_at=now,
            previous_key=b"old_key",
            previous_key_expires_at=now + timedelta(hours=24)
        )
        assert secret.is_in_grace_period() is True

    def test_is_in_grace_period_false_when_previous_key_expired(self):
        from core.rotation import ActiveSecret
        now = datetime.now(timezone.utc)
        secret = ActiveSecret(
            current_key=b"new_key",
            current_key_created_at=now,
            previous_key=b"old_key",
            previous_key_expires_at=now - timedelta(hours=1)
        )
        assert secret.is_in_grace_period() is False

    def test_validate_with_either_key_current_key_succeeds(self):
        from core.rotation import ActiveSecret
        now = datetime.now(timezone.utc)
        secret = ActiveSecret(
            current_key=b"correct_key",
            current_key_created_at=now
        )
        result = secret.validate_with_either_key(lambda k: k == b"correct_key")
        assert result is True

    def test_validate_with_either_key_fails_when_wrong_key(self):
        from core.rotation import ActiveSecret
        now = datetime.now(timezone.utc)
        secret = ActiveSecret(
            current_key=b"current_key",
            current_key_created_at=now
        )
        result = secret.validate_with_either_key(lambda k: k == b"wrong_key")
        assert result is False

    def test_validate_with_either_key_accepts_previous_in_grace_period(self):
        from core.rotation import ActiveSecret
        now = datetime.now(timezone.utc)
        secret = ActiveSecret(
            current_key=b"new_key",
            current_key_created_at=now,
            previous_key=b"old_key",
            previous_key_expires_at=now + timedelta(hours=24)
        )
        # Old key should match during grace period
        result = secret.validate_with_either_key(lambda k: k == b"old_key")
        assert result is True


class TestKeyRotationManagerInit:
    def test_manager_initializes_with_default_schedule(self):
        from core.rotation import KeyRotationManager, SecretType
        mgr = KeyRotationManager.__new__(KeyRotationManager)
        mgr._rotation_history = []
        mgr._active_secrets = {}
        mgr._jwt_secret = None
        mgr._rotation_schedule = {
            SecretType.JWT_SECRET: timedelta(days=90),
            SecretType.AGENT_SIGNING_KEY: timedelta(days=180),
            SecretType.FEDERATION_SESSION: timedelta(days=30),
            SecretType.API_KEY: timedelta(days=365),
        }
        assert SecretType.JWT_SECRET in mgr._rotation_schedule
        assert mgr._rotation_schedule[SecretType.JWT_SECRET] == timedelta(days=90)
        assert mgr._rotation_schedule[SecretType.AGENT_SIGNING_KEY] == timedelta(days=180)


# ═══════════════════════════════════════════════════════════════════════════════
# Alias wrapper modules — just importing is sufficient (they are 100% importable)
# ═══════════════════════════════════════════════════════════════════════════════

class TestAliasModuleImports:
    def test_baa_module_importable(self):
        import core.baa
        assert hasattr(core.baa, "baa_manager")
        assert hasattr(core.baa, "BAAManager")

    def test_breach_module_importable(self):
        import core.breach
        assert hasattr(core.breach, "breach_manager")
        assert hasattr(core.breach, "BreachManager")

    def test_hitrust_module_importable(self):
        import core.hitrust
        assert hasattr(core.hitrust, "hitrust_manager")
        assert hasattr(core.hitrust, "HITRUSTManager")

    def test_phi_module_importable(self):
        import core.phi
        assert hasattr(core.phi, "phi_manager")

    def test_retention_module_importable(self):
        import core.retention
        assert hasattr(core.retention, "retention_manager")
        assert hasattr(core.retention, "RetentionManager")

    def test_contingency_module_importable(self):
        import core.contingency
        assert hasattr(core.contingency, "contingency_manager")

    def test_legal_holds_module_importable(self):
        import core.legal_holds
        assert hasattr(core.legal_holds, "legal_hold_manager")
        assert hasattr(core.legal_holds, "HoldManager")


# ═══════════════════════════════════════════════════════════════════════════════
# core/auth_dependencies.py — pure helper functions
# ═══════════════════════════════════════════════════════════════════════════════

class TestExtractSessionId:
    def _make_auth(self, permissions):
        from core.auth import AuthResult
        return AuthResult(authenticated=True, actor="test_actor", method="api_key", permissions=permissions)

    def test_extracts_session_id_from_permissions(self):
        from core.auth_dependencies import _extract_session_id
        auth = self._make_auth(["session:abc123"])
        assert _extract_session_id(auth) == "abc123"

    def test_returns_empty_when_no_session_in_permissions(self):
        from core.auth_dependencies import _extract_session_id
        auth = self._make_auth(["read:data", "write:files"])
        assert _extract_session_id(auth) == ""

    def test_returns_empty_for_empty_permissions(self):
        from core.auth_dependencies import _extract_session_id
        auth = self._make_auth([])
        assert _extract_session_id(auth) == ""

    def test_extracts_first_session_entry(self):
        from core.auth_dependencies import _extract_session_id
        auth = self._make_auth(["read:x", "session:first_session_id"])
        assert _extract_session_id(auth) == "first_session_id"


class TestResolveRbacUser:
    def test_returns_none_when_no_user_found(self):
        from unittest.mock import MagicMock
        from core.auth import AuthResult
        from core.auth_dependencies import _resolve_rbac_user

        auth = AuthResult(authenticated=True, actor="unknown_actor", method="api_key")
        mock_rbac = MagicMock()
        mock_rbac.get_user_by_username.return_value = None
        mock_rbac.get_user.return_value = None

        result = _resolve_rbac_user(auth, mock_rbac)
        assert result is None

    def test_returns_user_by_username(self):
        from unittest.mock import MagicMock
        from core.auth import AuthResult
        from core.auth_dependencies import _resolve_rbac_user

        auth = AuthResult(authenticated=True, actor="alice", method="api_key")
        mock_rbac = MagicMock()
        fake_user = MagicMock()
        mock_rbac.get_user_by_username.return_value = fake_user

        result = _resolve_rbac_user(auth, mock_rbac)
        assert result is fake_user

    def test_returns_user_by_user_id_when_username_fails(self):
        from unittest.mock import MagicMock
        from core.auth import AuthResult
        from core.auth_dependencies import _resolve_rbac_user

        auth = AuthResult(authenticated=True, actor="user_id_123", method="api_key")
        mock_rbac = MagicMock()
        fake_user = MagicMock()
        mock_rbac.get_user_by_username.return_value = None
        mock_rbac.get_user.return_value = fake_user

        result = _resolve_rbac_user(auth, mock_rbac)
        assert result is fake_user

    def test_parses_owner_label_format(self):
        from unittest.mock import MagicMock
        from core.auth import AuthResult
        from core.auth_dependencies import _resolve_rbac_user

        # actor is "owner:label" format — should extract "owner" part
        auth = AuthResult(authenticated=True, actor="alice:my_key", method="api_key")
        mock_rbac = MagicMock()
        fake_user = MagicMock()
        mock_rbac.get_user_by_username.return_value = fake_user

        result = _resolve_rbac_user(auth, mock_rbac)
        mock_rbac.get_user_by_username.assert_called_once_with("alice")
        assert result is fake_user


# ═══════════════════════════════════════════════════════════════════════════════
# core/tenant_rate_limiting.py — _InMemoryBucket pure logic + constants
# ═══════════════════════════════════════════════════════════════════════════════

class TestInMemoryBucket:
    def _make_bucket(self):
        from core.tenant_rate_limiting import _InMemoryBucket
        return _InMemoryBucket()

    def test_initial_count_is_zero(self):
        bucket = self._make_bucket()
        assert bucket.count(1000.0) == 0

    def test_add_and_count_increments(self):
        bucket = self._make_bucket()
        count = bucket.add_and_count(1000.0)
        assert count == 1

    def test_multiple_adds_accumulate(self):
        bucket = self._make_bucket()
        bucket.add_and_count(1000.0)
        bucket.add_and_count(1001.0)
        count = bucket.add_and_count(1002.0)
        assert count == 3

    def test_old_timestamps_excluded_from_window(self):
        bucket = self._make_bucket()
        # Add event 2 minutes ago
        bucket.add_and_count(1000.0, window_seconds=60.0)
        # Add event now (at t=1120)
        count = bucket.add_and_count(1120.0, window_seconds=60.0)
        # Only the second event should be in the window
        assert count == 1

    def test_count_without_add_does_not_grow(self):
        bucket = self._make_bucket()
        bucket.add_and_count(1000.0)
        count1 = bucket.count(1001.0)
        count2 = bucket.count(1002.0)
        assert count1 == count2 == 1

    def test_count_excludes_expired_entries(self):
        bucket = self._make_bucket()
        bucket.add_and_count(1000.0)
        # Count at t=2000, window=60 -> entry at 1000 is expired
        count = bucket.count(2000.0, window_seconds=60.0)
        assert count == 0


class TestTenantRateLimitingConstants:
    def test_default_tenant_requests_per_minute(self):
        from core.tenant_rate_limiting import DEFAULT_TENANT_REQUESTS_PER_MINUTE
        assert DEFAULT_TENANT_REQUESTS_PER_MINUTE > 0
        assert DEFAULT_TENANT_REQUESTS_PER_MINUTE == 600

    def test_default_user_requests_per_minute(self):
        from core.tenant_rate_limiting import DEFAULT_USER_REQUESTS_PER_MINUTE
        assert DEFAULT_USER_REQUESTS_PER_MINUTE > 0
        assert DEFAULT_USER_REQUESTS_PER_MINUTE == 120

    def test_burst_multiplier_is_greater_than_one(self):
        from core.tenant_rate_limiting import BURST_MULTIPLIER
        assert BURST_MULTIPLIER > 1.0

    def test_premium_tenant_multiplier_is_two(self):
        from core.tenant_rate_limiting import PREMIUM_TENANT_MULTIPLIER
        assert PREMIUM_TENANT_MULTIPLIER == 2.0
