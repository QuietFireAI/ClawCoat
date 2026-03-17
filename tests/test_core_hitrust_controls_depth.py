# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_hitrust_controls_depth.py
# REM: Depth coverage for core/hitrust_controls.py
# REM: HITRUSTDomain, ControlStatus, HITRUSTControl, RiskAssessment,
# REM: HITRUSTManager — in-memory.

import pytest
from datetime import datetime, timezone

from core.hitrust_controls import (
    ControlStatus,
    HITRUSTControl,
    HITRUSTDomain,
    HITRUSTManager,
    RiskAssessment,
)


# ─── Patch Redis so audit.log() uses in-memory path ────────────────────────────
@pytest.fixture(autouse=True)
def _no_redis(monkeypatch):
    monkeypatch.setattr("core.persistence.get_redis", lambda: None)


@pytest.fixture
def hitrust():
    """Bypass __init__ to avoid _load_from_redis() and _save_all_controls() hitting Redis."""
    m = object.__new__(HITRUSTManager)
    m._controls = {}
    m._risk_assessments = []
    m._register_baseline_controls()
    return m


def _do_assessment(hitrust, title="Annual Risk Assessment", risk_level="medium"):
    return hitrust.record_risk_assessment(
        title=title,
        scope="full_platform",
        conducted_by="security_officer",
        findings=[{"finding": "test finding"}],
        risk_level=risk_level,
        mitigation="Apply patches within 30 days",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# HITRUSTDomain enum
# ═══════════════════════════════════════════════════════════════════════════════

class TestHITRUSTDomain:
    def test_access_control_value(self):
        assert HITRUSTDomain.ACCESS_CONTROL == "access_control"

    def test_audit_logging_value(self):
        assert HITRUSTDomain.AUDIT_LOGGING == "audit_logging"

    def test_risk_management_value(self):
        assert HITRUSTDomain.RISK_MANAGEMENT == "risk_management"

    def test_encryption_value(self):
        assert HITRUSTDomain.ENCRYPTION == "encryption"

    def test_incident_management_value(self):
        assert HITRUSTDomain.INCIDENT_MANAGEMENT == "incident_management"

    def test_twelve_members(self):
        assert len(HITRUSTDomain) == 12

    def test_is_str_subclass(self):
        assert isinstance(HITRUSTDomain.ACCESS_CONTROL, str)


# ═══════════════════════════════════════════════════════════════════════════════
# ControlStatus enum
# ═══════════════════════════════════════════════════════════════════════════════

class TestControlStatus:
    def test_not_implemented_value(self):
        assert ControlStatus.NOT_IMPLEMENTED == "not_implemented"

    def test_partial_value(self):
        assert ControlStatus.PARTIAL == "partial"

    def test_implemented_value(self):
        assert ControlStatus.IMPLEMENTED == "implemented"

    def test_validated_value(self):
        assert ControlStatus.VALIDATED == "validated"

    def test_not_applicable_value(self):
        assert ControlStatus.NOT_APPLICABLE == "not_applicable"

    def test_five_members(self):
        assert len(ControlStatus) == 5

    def test_is_str_subclass(self):
        assert isinstance(ControlStatus.IMPLEMENTED, str)


# ═══════════════════════════════════════════════════════════════════════════════
# HITRUSTControl.to_dict()
# ═══════════════════════════════════════════════════════════════════════════════

class TestHITRUSTControlToDict:
    def _make_control(self, **kwargs):
        defaults = dict(
            control_id="01.a",
            domain=HITRUSTDomain.ACCESS_CONTROL,
            title="Access Control",
            description="RBAC policy",
        )
        defaults.update(kwargs)
        return HITRUSTControl(**defaults)

    def test_returns_dict(self):
        assert isinstance(self._make_control().to_dict(), dict)

    def test_control_id_present(self):
        c = self._make_control(control_id="09.ab")
        assert c.to_dict()["control_id"] == "09.ab"

    def test_domain_is_value_string(self):
        c = self._make_control(domain=HITRUSTDomain.ENCRYPTION)
        assert c.to_dict()["domain"] == "encryption"

    def test_title_present(self):
        c = self._make_control(title="Key Management")
        assert c.to_dict()["title"] == "Key Management"

    def test_description_present(self):
        c = self._make_control(description="AES-256 encryption")
        assert c.to_dict()["description"] == "AES-256 encryption"

    def test_status_is_value_string(self):
        c = self._make_control(status=ControlStatus.IMPLEMENTED)
        assert c.to_dict()["status"] == "implemented"

    def test_evidence_references_is_list(self):
        c = self._make_control()
        assert isinstance(c.to_dict()["evidence_references"], list)

    def test_last_assessed_none_when_unset(self):
        c = self._make_control()
        assert c.to_dict()["last_assessed"] is None

    def test_last_assessed_isoformat_when_set(self):
        ts = datetime(2026, 3, 1, tzinfo=timezone.utc)
        c = self._make_control(last_assessed=ts)
        assert c.to_dict()["last_assessed"] == ts.isoformat()

    def test_assessed_by_present(self):
        c = self._make_control(assessed_by="security_officer")
        assert c.to_dict()["assessed_by"] == "security_officer"

    def test_notes_present(self):
        c = self._make_control(notes="reviewed Q1 2026")
        assert c.to_dict()["notes"] == "reviewed Q1 2026"

    def test_nine_keys_present(self):
        c = self._make_control()
        expected = {
            "control_id", "domain", "title", "description",
            "status", "evidence_references", "last_assessed",
            "assessed_by", "notes"
        }
        assert set(c.to_dict().keys()) == expected


# ═══════════════════════════════════════════════════════════════════════════════
# RiskAssessment.to_dict()
# ═══════════════════════════════════════════════════════════════════════════════

class TestRiskAssessmentToDict:
    def test_returns_dict(self):
        assert isinstance(RiskAssessment().to_dict(), dict)

    def test_assessment_id_present(self):
        ra = RiskAssessment(assessment_id="ra-001")
        assert ra.to_dict()["assessment_id"] == "ra-001"

    def test_title_present(self):
        ra = RiskAssessment(title="Q1 Assessment")
        assert ra.to_dict()["title"] == "Q1 Assessment"

    def test_scope_present(self):
        ra = RiskAssessment(scope="full_platform")
        assert ra.to_dict()["scope"] == "full_platform"

    def test_conducted_by_present(self):
        ra = RiskAssessment(conducted_by="auditor")
        assert ra.to_dict()["conducted_by"] == "auditor"

    def test_conducted_at_is_isoformat(self):
        ts = datetime(2026, 3, 1, tzinfo=timezone.utc)
        ra = RiskAssessment(conducted_at=ts)
        assert ra.to_dict()["conducted_at"] == ts.isoformat()

    def test_findings_is_list(self):
        ra = RiskAssessment(findings=[{"test": "finding"}])
        assert ra.to_dict()["findings"] == [{"test": "finding"}]

    def test_risk_level_present(self):
        ra = RiskAssessment(risk_level="critical")
        assert ra.to_dict()["risk_level"] == "critical"

    def test_mitigation_plan_present(self):
        ra = RiskAssessment(mitigation_plan="Apply patches")
        assert ra.to_dict()["mitigation_plan"] == "Apply patches"

    def test_next_review_is_isoformat(self):
        ts = datetime(2026, 6, 1, tzinfo=timezone.utc)
        ra = RiskAssessment(next_review=ts)
        assert ra.to_dict()["next_review"] == ts.isoformat()

    def test_nine_keys_present(self):
        expected = {
            "assessment_id", "title", "scope", "conducted_by",
            "conducted_at", "findings", "risk_level",
            "mitigation_plan", "next_review"
        }
        assert set(RiskAssessment().to_dict().keys()) == expected


# ═══════════════════════════════════════════════════════════════════════════════
# HITRUSTManager baseline controls
# ═══════════════════════════════════════════════════════════════════════════════

class TestBaselineControls:
    def test_seventeen_controls_registered(self, hitrust):
        assert len(hitrust._controls) == 17

    def test_all_baseline_controls_partial(self, hitrust):
        assert all(c.status == ControlStatus.PARTIAL for c in hitrust._controls.values())

    def test_access_control_01a_present(self, hitrust):
        assert "01.a" in hitrust._controls

    def test_audit_logging_09aa_present(self, hitrust):
        assert "09.aa" in hitrust._controls

    def test_encryption_06a_present(self, hitrust):
        assert "06.a" in hitrust._controls

    def test_risk_management_03a_present(self, hitrust):
        assert "03.a" in hitrust._controls

    def test_controls_have_correct_domain(self, hitrust):
        assert hitrust._controls["01.a"].domain == HITRUSTDomain.ACCESS_CONTROL
        assert hitrust._controls["09.aa"].domain == HITRUSTDomain.AUDIT_LOGGING
        assert hitrust._controls["06.a"].domain == HITRUSTDomain.ENCRYPTION


# ═══════════════════════════════════════════════════════════════════════════════
# HITRUSTManager.register_control()
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegisterControl:
    def test_returns_hitrust_control(self, hitrust):
        result = hitrust.register_control("99.x", HITRUSTDomain.ENCRYPTION, "Test", "Test desc")
        assert isinstance(result, HITRUSTControl)

    def test_control_stored(self, hitrust):
        hitrust.register_control("99.x", HITRUSTDomain.ENCRYPTION, "Test", "Test desc")
        assert "99.x" in hitrust._controls

    def test_control_id_correct(self, hitrust):
        c = hitrust.register_control("99.x", HITRUSTDomain.ENCRYPTION, "Test", "Test desc")
        assert c.control_id == "99.x"

    def test_status_is_not_implemented_by_default(self, hitrust):
        c = hitrust.register_control("99.x", HITRUSTDomain.ENCRYPTION, "Test", "Test desc")
        assert c.status == ControlStatus.NOT_IMPLEMENTED

    def test_title_stored(self, hitrust):
        c = hitrust.register_control("99.x", HITRUSTDomain.ENCRYPTION, "Key Mgmt", "Desc")
        assert c.title == "Key Mgmt"

    def test_domain_stored(self, hitrust):
        c = hitrust.register_control("99.x", HITRUSTDomain.NETWORK_SECURITY, "Net", "Desc")
        assert c.domain == HITRUSTDomain.NETWORK_SECURITY

    def test_overrides_existing_control(self, hitrust):
        hitrust.register_control("01.a", HITRUSTDomain.ENCRYPTION, "Overridden", "New desc")
        assert hitrust._controls["01.a"].title == "Overridden"


# ═══════════════════════════════════════════════════════════════════════════════
# HITRUSTManager.update_control_status()
# ═══════════════════════════════════════════════════════════════════════════════

class TestUpdateControlStatus:
    def test_returns_true_for_known_control(self, hitrust):
        assert hitrust.update_control_status("01.a", ControlStatus.IMPLEMENTED) is True

    def test_returns_false_for_unknown_control(self, hitrust):
        assert hitrust.update_control_status("99.z", ControlStatus.IMPLEMENTED) is False

    def test_status_updated(self, hitrust):
        hitrust.update_control_status("01.a", ControlStatus.VALIDATED)
        assert hitrust._controls["01.a"].status == ControlStatus.VALIDATED

    def test_last_assessed_set(self, hitrust):
        hitrust.update_control_status("01.a", ControlStatus.IMPLEMENTED)
        assert hitrust._controls["01.a"].last_assessed is not None

    def test_assessed_by_stored(self, hitrust):
        hitrust.update_control_status("01.a", ControlStatus.IMPLEMENTED, assessed_by="auditor")
        assert hitrust._controls["01.a"].assessed_by == "auditor"

    def test_evidence_appended(self, hitrust):
        hitrust.update_control_status("01.a", ControlStatus.IMPLEMENTED, evidence=["doc-001"])
        assert "doc-001" in hitrust._controls["01.a"].evidence_references

    def test_multiple_evidence_items_appended(self, hitrust):
        hitrust.update_control_status("01.a", ControlStatus.IMPLEMENTED, evidence=["doc-001", "doc-002"])
        refs = hitrust._controls["01.a"].evidence_references
        assert "doc-001" in refs and "doc-002" in refs

    def test_no_evidence_leaves_references_unchanged(self, hitrust):
        initial = list(hitrust._controls["01.a"].evidence_references)
        hitrust.update_control_status("01.a", ControlStatus.IMPLEMENTED)
        assert hitrust._controls["01.a"].evidence_references == initial


# ═══════════════════════════════════════════════════════════════════════════════
# HITRUSTManager.record_risk_assessment()
# ═══════════════════════════════════════════════════════════════════════════════

class TestRecordRiskAssessment:
    def test_returns_risk_assessment(self, hitrust):
        assert isinstance(_do_assessment(hitrust), RiskAssessment)

    def test_assessment_appended(self, hitrust):
        _do_assessment(hitrust)
        assert len(hitrust._risk_assessments) == 1

    def test_title_stored(self, hitrust):
        ra = _do_assessment(hitrust, title="Q2 Assessment")
        assert ra.title == "Q2 Assessment"

    def test_risk_level_stored(self, hitrust):
        ra = _do_assessment(hitrust, risk_level="critical")
        assert ra.risk_level == "critical"

    def test_assessment_id_generated(self, hitrust):
        ra = _do_assessment(hitrust)
        assert ra.assessment_id  # Non-empty

    def test_unique_assessment_ids(self, hitrust):
        ra1 = _do_assessment(hitrust)
        ra2 = _do_assessment(hitrust)
        assert ra1.assessment_id != ra2.assessment_id

    def test_findings_stored(self, hitrust):
        ra = _do_assessment(hitrust)
        assert len(ra.findings) == 1

    def test_next_review_defaults_to_90_days(self, hitrust):
        from datetime import timedelta
        before = datetime.now(timezone.utc)
        ra = _do_assessment(hitrust)
        after = datetime.now(timezone.utc)
        expected_min = before + timedelta(days=89)
        expected_max = after + timedelta(days=91)
        assert expected_min <= ra.next_review <= expected_max

    def test_custom_next_review(self, hitrust):
        from datetime import timedelta
        future = datetime.now(timezone.utc) + timedelta(days=180)
        ra = hitrust.record_risk_assessment(
            title="Custom",
            scope="scope",
            conducted_by="auditor",
            findings=[],
            risk_level="low",
            mitigation="none",
            next_review=future,
        )
        assert abs((ra.next_review - future).total_seconds()) < 1


# ═══════════════════════════════════════════════════════════════════════════════
# HITRUSTManager.get_compliance_posture()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetCompliancePosture:
    def test_returns_dict(self, hitrust):
        assert isinstance(hitrust.get_compliance_posture(), dict)

    def test_overall_key_present(self, hitrust):
        assert "overall" in hitrust.get_compliance_posture()

    def test_overall_has_total_controls(self, hitrust):
        assert "total_controls" in hitrust.get_compliance_posture()["overall"]

    def test_overall_has_compliant_controls(self, hitrust):
        assert "compliant_controls" in hitrust.get_compliance_posture()["overall"]

    def test_overall_has_percentage(self, hitrust):
        assert "percentage" in hitrust.get_compliance_posture()["overall"]

    def test_baseline_all_partial_gives_zero_percent(self, hitrust):
        posture = hitrust.get_compliance_posture()
        assert posture["overall"]["percentage"] == 0.0

    def test_implemented_status_counts_as_compliant(self, hitrust):
        hitrust.update_control_status("01.a", ControlStatus.IMPLEMENTED)
        posture = hitrust.get_compliance_posture()
        assert posture["overall"]["compliant_controls"] >= 1

    def test_validated_counts_as_compliant(self, hitrust):
        hitrust.update_control_status("01.a", ControlStatus.VALIDATED)
        posture = hitrust.get_compliance_posture()
        assert posture["overall"]["compliant_controls"] >= 1

    def test_not_applicable_counts_as_compliant(self, hitrust):
        hitrust.update_control_status("01.a", ControlStatus.NOT_APPLICABLE)
        posture = hitrust.get_compliance_posture()
        assert posture["overall"]["compliant_controls"] >= 1

    def test_partial_does_not_count_as_compliant(self, hitrust):
        # All baseline are PARTIAL → 0 compliant
        posture = hitrust.get_compliance_posture()
        assert posture["overall"]["compliant_controls"] == 0

    def test_domain_key_present_for_access_control(self, hitrust):
        assert "access_control" in hitrust.get_compliance_posture()

    def test_total_controls_matches_registered(self, hitrust):
        posture = hitrust.get_compliance_posture()
        assert posture["overall"]["total_controls"] == len(hitrust._controls)


# ═══════════════════════════════════════════════════════════════════════════════
# HITRUSTManager.get_control()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetControl:
    def test_returns_control_by_id(self, hitrust):
        result = hitrust.get_control("01.a")
        assert result is hitrust._controls["01.a"]

    def test_returns_none_for_unknown(self, hitrust):
        assert hitrust.get_control("99.z") is None

    def test_returns_hitrust_control(self, hitrust):
        assert isinstance(hitrust.get_control("01.a"), HITRUSTControl)


# ═══════════════════════════════════════════════════════════════════════════════
# HITRUSTManager.get_controls_by_domain()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetControlsByDomain:
    def test_returns_list(self, hitrust):
        assert isinstance(hitrust.get_controls_by_domain(HITRUSTDomain.ACCESS_CONTROL), list)

    def test_returns_correct_domain_controls(self, hitrust):
        result = hitrust.get_controls_by_domain(HITRUSTDomain.ACCESS_CONTROL)
        assert all(c.domain == HITRUSTDomain.ACCESS_CONTROL for c in result)

    def test_access_control_has_multiple(self, hitrust):
        result = hitrust.get_controls_by_domain(HITRUSTDomain.ACCESS_CONTROL)
        assert len(result) >= 2  # 01.a, 01.b, 01.c are all access_control

    def test_empty_for_domain_with_no_controls(self, hitrust):
        # Clear controls and check empty domain
        hitrust._controls = {}
        result = hitrust.get_controls_by_domain(HITRUSTDomain.PHYSICAL_SECURITY)
        assert result == []


# ═══════════════════════════════════════════════════════════════════════════════
# HITRUSTManager.get_controls_by_status()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetControlsByStatus:
    def test_returns_list(self, hitrust):
        assert isinstance(hitrust.get_controls_by_status(ControlStatus.PARTIAL), list)

    def test_all_baseline_returned_for_partial(self, hitrust):
        result = hitrust.get_controls_by_status(ControlStatus.PARTIAL)
        assert len(result) == 17

    def test_empty_for_not_implemented(self, hitrust):
        result = hitrust.get_controls_by_status(ControlStatus.NOT_IMPLEMENTED)
        assert result == []

    def test_filter_works_after_update(self, hitrust):
        hitrust.update_control_status("01.a", ControlStatus.IMPLEMENTED)
        result = hitrust.get_controls_by_status(ControlStatus.IMPLEMENTED)
        assert len(result) == 1
        assert result[0].control_id == "01.a"


# ═══════════════════════════════════════════════════════════════════════════════
# HITRUSTManager.get_risk_assessments()
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetRiskAssessments:
    def test_returns_list(self, hitrust):
        assert isinstance(hitrust.get_risk_assessments(), list)

    def test_empty_initially(self, hitrust):
        assert hitrust.get_risk_assessments() == []

    def test_returns_all_assessments(self, hitrust):
        _do_assessment(hitrust)
        _do_assessment(hitrust)
        assert len(hitrust.get_risk_assessments()) == 2

    def test_sorted_newest_first(self, hitrust):
        ra1 = _do_assessment(hitrust)
        ra2 = _do_assessment(hitrust)
        results = hitrust.get_risk_assessments()
        # Most recent first
        assert results[0].conducted_at >= results[1].conducted_at
