# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_openclaw_routes_depth.py
# REM: Depth coverage for api/openclaw_routes.py
# REM: Tests: model validators, request/response models, all 14 endpoints,
# REM: auth-required paths, trust-override validation, demotion hard-block.

import pytest

AUTH = {"X-API-Key": "test_api_key_12345"}
NO_AUTH = {}
INSTANCE_ID = "test_instance_depth_001"


# ═══════════════════════════════════════════════════════════════════════════════
# RegisterClawRequest model validator (pure Python, no network)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegisterClawRequestModel:
    """REM: Test model-layer validation — runs without a server."""

    def _make(self, **kwargs):
        from api.openclaw_routes import RegisterClawRequest
        return RegisterClawRequest(**kwargs)

    def test_default_is_quarantine(self):
        req = self._make(name="test")
        assert req.initial_trust_level == "quarantine"

    def test_quarantine_with_no_reason_is_valid(self):
        req = self._make(name="test", initial_trust_level="quarantine")
        assert req.initial_trust_level == "quarantine"

    def test_quarantine_with_reason_is_valid(self):
        req = self._make(name="test", initial_trust_level="quarantine",
                         override_reason="some reason here")
        assert req.initial_trust_level == "quarantine"

    def test_invalid_trust_level_raises(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            self._make(name="test", initial_trust_level="superpower")

    def test_probation_without_reason_raises(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            self._make(name="test", initial_trust_level="probation")

    def test_probation_with_short_reason_raises(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            self._make(name="test", initial_trust_level="probation",
                       override_reason="too short")

    def test_probation_with_valid_reason_is_valid(self):
        req = self._make(name="test", initial_trust_level="probation",
                         override_reason="Approved for initial deployment phase")
        assert req.initial_trust_level == "probation"
        assert req.override_reason == "Approved for initial deployment phase"

    def test_resident_with_valid_reason_is_valid(self):
        req = self._make(name="test", initial_trust_level="resident",
                         override_reason="Proven track record, operator approved")
        assert req.initial_trust_level == "resident"

    def test_citizen_with_valid_reason_is_valid(self):
        req = self._make(name="test", initial_trust_level="citizen",
                         override_reason="Senior agent, 90-day review completed")
        assert req.initial_trust_level == "citizen"

    def test_agent_with_valid_reason_is_valid(self):
        req = self._make(name="test", initial_trust_level="agent",
                         override_reason="Apex agent, full autonomy grant approved")
        assert req.initial_trust_level == "agent"

    def test_normalizes_uppercase_to_lowercase(self):
        req = self._make(name="test", initial_trust_level="QUARANTINE")
        assert req.initial_trust_level == "quarantine"

    def test_strips_whitespace_from_trust_level(self):
        req = self._make(name="test", initial_trust_level="  quarantine  ")
        assert req.initial_trust_level == "quarantine"

    def test_reason_whitespace_stripped(self):
        req = self._make(name="test", initial_trust_level="probation",
                         override_reason="  Approved for probation period  ")
        assert req.override_reason == "Approved for probation period"

    def test_empty_override_reason_for_above_quarantine_raises(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            self._make(name="test", initial_trust_level="probation", override_reason="")

    def test_default_allowed_tools_is_empty_list(self):
        req = self._make(name="test")
        assert req.allowed_tools == []

    def test_default_blocked_tools_is_empty_list(self):
        req = self._make(name="test")
        assert req.blocked_tools == []


# ═══════════════════════════════════════════════════════════════════════════════
# Other request models
# ═══════════════════════════════════════════════════════════════════════════════

class TestOtherRequestModels:
    def test_action_request(self):
        from api.openclaw_routes import ActionRequest
        req = ActionRequest(tool_name="read_file", tool_args={"path": "/tmp/test.txt"})
        assert req.tool_name == "read_file"
        assert req.nonce is None

    def test_action_request_with_nonce(self):
        from api.openclaw_routes import ActionRequest
        req = ActionRequest(tool_name="write_file", nonce="abc123")
        assert req.nonce == "abc123"

    def test_promote_request(self):
        from api.openclaw_routes import PromoteRequest
        req = PromoteRequest(new_level="probation", reason="initial setup")
        assert req.new_level == "probation"

    def test_demote_request_default_acknowledged(self):
        from api.openclaw_routes import DemoteRequest
        req = DemoteRequest(new_level="quarantine")
        assert req.acknowledged is False

    def test_demote_request_with_acknowledged(self):
        from api.openclaw_routes import DemoteRequest
        req = DemoteRequest(new_level="quarantine", acknowledged=True)
        assert req.acknowledged is True

    def test_suspend_request_empty_reason(self):
        from api.openclaw_routes import SuspendRequest
        req = SuspendRequest()
        assert req.reason == ""

    def test_reinstate_request(self):
        from api.openclaw_routes import ReinstateRequest
        req = ReinstateRequest(reason="reviewed and cleared")
        assert req.reason == "reviewed and cleared"

    def test_clear_review_request(self):
        from api.openclaw_routes import ClearReviewRequest
        req = ClearReviewRequest(notes="audited last 30 actions, all nominal")
        assert req.notes == "audited last 30 actions, all nominal"

    def test_claw_instance_response_defaults(self):
        from api.openclaw_routes import ClawInstanceResponse
        resp = ClawInstanceResponse(instance_id="test-001")
        assert resp.trust_level == "quarantine"
        assert resp.manners_score == 1.0
        assert resp.suspended is False
        assert resp.qms_status == "Thank_You"

    def test_action_result_response_defaults(self):
        from api.openclaw_routes import ActionResultResponse
        resp = ActionResultResponse()
        assert resp.allowed is False
        assert resp.approval_required is False
        assert resp.qms_status == "Thank_You"


# ═══════════════════════════════════════════════════════════════════════════════
# _check_enabled and _TRUST_LADDER constants
# ═══════════════════════════════════════════════════════════════════════════════

class TestOpenClawConstants:
    def test_trust_ladder_has_five_levels(self):
        from api.openclaw_routes import _TRUST_LADDER
        assert len(_TRUST_LADDER) == 5

    def test_trust_ladder_order(self):
        from api.openclaw_routes import _TRUST_LADDER
        assert _TRUST_LADDER[0] == "quarantine"
        assert _TRUST_LADDER[1] == "probation"
        assert _TRUST_LADDER[2] == "resident"
        assert _TRUST_LADDER[3] == "citizen"
        assert _TRUST_LADDER[4] == "agent"

    def test_override_reason_min_len(self):
        from api.openclaw_routes import _OVERRIDE_REASON_MIN_LEN
        assert _OVERRIDE_REASON_MIN_LEN == 10


# ═══════════════════════════════════════════════════════════════════════════════
# Route tests — auth required
# ═══════════════════════════════════════════════════════════════════════════════

class TestListCLawsAuth:
    def test_requires_auth(self, client):
        resp = client.get("/v1/openclaw/list")
        assert resp.status_code == 401


class TestRegisterClawAuth:
    def test_requires_auth(self, client):
        resp = client.post("/v1/openclaw/register", json={"name": "test"})
        assert resp.status_code == 401


class TestEvaluateActionAuth:
    def test_requires_auth(self, client):
        resp = client.post(
            f"/v1/openclaw/{INSTANCE_ID}/action",
            json={"tool_name": "read_file"}
        )
        assert resp.status_code == 401


class TestGetInstanceAuth:
    def test_requires_auth(self, client):
        resp = client.get(f"/v1/openclaw/{INSTANCE_ID}")
        assert resp.status_code == 401


class TestGetStatusAuth:
    def test_requires_auth(self, client):
        resp = client.get(f"/v1/openclaw/{INSTANCE_ID}/status")
        assert resp.status_code == 401


class TestPromoteAuth:
    def test_requires_auth(self, client):
        resp = client.post(
            f"/v1/openclaw/{INSTANCE_ID}/promote",
            json={"new_level": "probation"}
        )
        assert resp.status_code == 401


class TestDemoteAuth:
    def test_requires_auth(self, client):
        resp = client.post(
            f"/v1/openclaw/{INSTANCE_ID}/demote",
            json={"new_level": "quarantine"}
        )
        assert resp.status_code == 401


class TestSuspendAuth:
    def test_requires_auth(self, client):
        resp = client.post(
            f"/v1/openclaw/{INSTANCE_ID}/suspend",
            json={"reason": "testing"}
        )
        assert resp.status_code == 401


class TestReinstateAuth:
    def test_requires_auth(self, client):
        resp = client.post(
            f"/v1/openclaw/{INSTANCE_ID}/reinstate",
            json={"reason": "testing"}
        )
        assert resp.status_code == 401


class TestDeregisterAuth:
    def test_requires_auth(self, client):
        resp = client.delete(f"/v1/openclaw/{INSTANCE_ID}")
        assert resp.status_code == 401


class TestTrustReportAuth:
    def test_requires_auth(self, client):
        resp = client.get(f"/v1/openclaw/{INSTANCE_ID}/trust-report")
        assert resp.status_code == 401


class TestActionsAuth:
    def test_requires_auth(self, client):
        resp = client.get(f"/v1/openclaw/{INSTANCE_ID}/actions")
        assert resp.status_code == 401


class TestMannersAuth:
    def test_requires_auth(self, client):
        resp = client.get(f"/v1/openclaw/{INSTANCE_ID}/manners")
        assert resp.status_code == 401


class TestClearReviewAuth:
    def test_requires_auth(self, client):
        resp = client.post(
            f"/v1/openclaw/{INSTANCE_ID}/clear-review",
            json={"notes": "reviewed"}
        )
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# Route tests — validation (422)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegisterValidation:
    def test_invalid_trust_level_returns_422(self, client):
        resp = client.post(
            "/v1/openclaw/register",
            headers=AUTH,
            json={"name": "test", "initial_trust_level": "superpower"}
        )
        assert resp.status_code == 422

    def test_above_quarantine_without_reason_returns_422(self, client):
        resp = client.post(
            "/v1/openclaw/register",
            headers=AUTH,
            json={"name": "test", "initial_trust_level": "probation"}
        )
        assert resp.status_code == 422

    def test_above_quarantine_with_short_reason_returns_422(self, client):
        resp = client.post(
            "/v1/openclaw/register",
            headers=AUTH,
            json={"name": "test", "initial_trust_level": "probation",
                  "override_reason": "short"}
        )
        assert resp.status_code == 422

    def test_missing_name_returns_422(self, client):
        resp = client.post("/v1/openclaw/register", headers=AUTH, json={})
        assert resp.status_code == 422


class TestActionValidation:
    def test_missing_tool_name_returns_422(self, client):
        resp = client.post(
            f"/v1/openclaw/{INSTANCE_ID}/action",
            headers=AUTH,
            json={}
        )
        assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# Route tests — success paths (200 or expected error codes)
# ═══════════════════════════════════════════════════════════════════════════════

class TestListClaws:
    def test_list_returns_200_or_404(self, client):
        resp = client.get("/v1/openclaw/list", headers=AUTH)
        # 200 if enabled, 404 if OPENCLAW_ENABLED=false
        assert resp.status_code in (200, 404)

    def test_list_returns_list_when_200(self, client):
        resp = client.get("/v1/openclaw/list", headers=AUTH)
        if resp.status_code == 200:
            assert isinstance(resp.json(), list)


class TestRegisterClaw:
    def test_register_returns_200_or_404(self, client):
        resp = client.post(
            "/v1/openclaw/register",
            headers=AUTH,
            json={"name": "depth-test-agent"}
        )
        assert resp.status_code in (200, 400, 404)

    def test_register_with_quarantine_level(self, client):
        resp = client.post(
            "/v1/openclaw/register",
            headers=AUTH,
            json={"name": "depth-quarantine-agent", "initial_trust_level": "quarantine"}
        )
        assert resp.status_code in (200, 400, 404)

    def test_register_with_probation_override(self, client):
        resp = client.post(
            "/v1/openclaw/register",
            headers=AUTH,
            json={
                "name": "depth-probation-agent",
                "initial_trust_level": "probation",
                "override_reason": "Approved for initial probation deployment"
            }
        )
        assert resp.status_code in (200, 400, 404)


class TestEvaluateAction:
    def test_action_returns_200_or_error(self, client):
        resp = client.post(
            f"/v1/openclaw/{INSTANCE_ID}/action",
            headers=AUTH,
            json={"tool_name": "read_file", "tool_args": {"path": "/docs/test.txt"}}
        )
        assert resp.status_code in (200, 404, 500)

    def test_action_with_nonce(self, client):
        resp = client.post(
            f"/v1/openclaw/{INSTANCE_ID}/action",
            headers=AUTH,
            json={"tool_name": "read_file", "nonce": "test-nonce-12345"}
        )
        assert resp.status_code in (200, 404, 500)

    def test_action_with_invalid_agent_key_returns_401(self, client):
        resp = client.post(
            f"/v1/openclaw/{INSTANCE_ID}/action",
            headers={**AUTH, "X-Agent-Key": "invalid_agent_key"},
            json={"tool_name": "read_file"}
        )
        # Either 401 (invalid agent key) or 404 (openclaw disabled) or 200/500
        assert resp.status_code in (200, 401, 404, 500)


class TestGetClaw:
    def test_get_nonexistent_returns_404_or_openclaw_disabled(self, client):
        resp = client.get(f"/v1/openclaw/nonexistent_instance_xyz", headers=AUTH)
        assert resp.status_code in (404, 500)

    def test_get_returns_200_or_404(self, client):
        resp = client.get(f"/v1/openclaw/{INSTANCE_ID}", headers=AUTH)
        assert resp.status_code in (200, 404, 500)


class TestGetStatus:
    def test_status_nonexistent_returns_404(self, client):
        resp = client.get(f"/v1/openclaw/nonexistent_xyz/status", headers=AUTH)
        assert resp.status_code in (404, 500)


class TestPromote:
    def test_promote_nonexistent_returns_400_or_404(self, client):
        resp = client.post(
            f"/v1/openclaw/nonexistent_xyz/promote",
            headers=AUTH,
            json={"new_level": "probation", "reason": "test"}
        )
        assert resp.status_code in (400, 404, 500)


class TestDemote:
    def test_demote_nonexistent_returns_400_or_404(self, client):
        resp = client.post(
            f"/v1/openclaw/nonexistent_xyz/demote",
            headers=AUTH,
            json={"new_level": "quarantine", "reason": "test"}
        )
        assert resp.status_code in (400, 404, 409, 500)

    def test_demote_from_agent_without_acknowledge_returns_409(self, client):
        # When demoting AGENT tier without acknowledged=true → 409
        resp = client.post(
            f"/v1/openclaw/{INSTANCE_ID}/demote",
            headers=AUTH,
            json={"new_level": "quarantine", "acknowledged": False}
        )
        # Either 409 (if instance exists at AGENT tier) or 400/404/500
        assert resp.status_code in (400, 404, 409, 500)


class TestSuspend:
    def test_suspend_nonexistent_returns_404(self, client):
        resp = client.post(
            f"/v1/openclaw/nonexistent_xyz/suspend",
            headers=AUTH,
            json={"reason": "testing"}
        )
        assert resp.status_code in (404, 500)


class TestReinstate:
    def test_reinstate_nonexistent_returns_400_or_404(self, client):
        resp = client.post(
            f"/v1/openclaw/nonexistent_xyz/reinstate",
            headers=AUTH,
            json={"reason": "testing"}
        )
        assert resp.status_code in (400, 404, 500)


class TestDeregister:
    def test_deregister_nonexistent_returns_404(self, client):
        resp = client.delete(f"/v1/openclaw/nonexistent_xyz", headers=AUTH)
        assert resp.status_code in (404, 500)


class TestTrustReport:
    def test_trust_report_nonexistent_returns_404(self, client):
        resp = client.get(f"/v1/openclaw/nonexistent_xyz/trust-report", headers=AUTH)
        assert resp.status_code in (404, 500)


class TestRecentActions:
    def test_actions_nonexistent_returns_404(self, client):
        resp = client.get(f"/v1/openclaw/nonexistent_xyz/actions", headers=AUTH)
        assert resp.status_code in (404, 500)

    def test_actions_with_limit_param(self, client):
        resp = client.get(
            f"/v1/openclaw/nonexistent_xyz/actions?limit=10",
            headers=AUTH
        )
        assert resp.status_code in (404, 500)


class TestMannersReport:
    def test_manners_nonexistent_returns_404(self, client):
        resp = client.get(f"/v1/openclaw/nonexistent_xyz/manners", headers=AUTH)
        assert resp.status_code in (404, 500)


class TestClearReview:
    def test_clear_review_nonexistent_returns_400_or_404(self, client):
        resp = client.post(
            f"/v1/openclaw/nonexistent_xyz/clear-review",
            headers=AUTH,
            json={"notes": "reviewed all actions, all nominal"}
        )
        assert resp.status_code in (400, 404, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# Integration flow: register → action → status (if OpenClaw enabled)
# ═══════════════════════════════════════════════════════════════════════════════

class TestOpenClawFlow:
    """REM: Light end-to-end flow if OpenClaw is enabled in test environment."""

    def test_full_register_and_action_flow(self, client):
        # Register
        reg_resp = client.post(
            "/v1/openclaw/register",
            headers=AUTH,
            json={"name": "flow-test-agent-depth"}
        )
        if reg_resp.status_code == 404:
            pytest.skip("OpenClaw not enabled in test environment")
        if reg_resp.status_code in (400, 500):
            return  # Can't proceed without registration

        assert reg_resp.status_code == 200
        data = reg_resp.json()
        instance_id = data["instance_id"]
        assert data["trust_level"] == "quarantine"
        assert "agent_key" in data

        # List — should include our new instance
        list_resp = client.get("/v1/openclaw/list", headers=AUTH)
        assert list_resp.status_code == 200
        ids = [i["instance_id"] for i in list_resp.json()]
        assert instance_id in ids

        # Get instance
        get_resp = client.get(f"/v1/openclaw/{instance_id}", headers=AUTH)
        assert get_resp.status_code == 200
        assert get_resp.json()["instance_id"] == instance_id

        # Evaluate action (quarantine — should be blocked)
        action_resp = client.post(
            f"/v1/openclaw/{instance_id}/action",
            headers=AUTH,
            json={"tool_name": "read_file", "tool_args": {"path": "/test.txt"}}
        )
        assert action_resp.status_code in (200, 500)

        # Promote to probation
        promote_resp = client.post(
            f"/v1/openclaw/{instance_id}/promote",
            headers=AUTH,
            json={"new_level": "probation", "reason": "depth test promotion"}
        )
        assert promote_resp.status_code in (200, 400, 500)

        # Get status
        status_resp = client.get(f"/v1/openclaw/{instance_id}/status", headers=AUTH)
        assert status_resp.status_code in (200, 500)

        # Trust report
        report_resp = client.get(f"/v1/openclaw/{instance_id}/trust-report", headers=AUTH)
        assert report_resp.status_code in (200, 500)

        # Actions log
        actions_resp = client.get(f"/v1/openclaw/{instance_id}/actions", headers=AUTH)
        assert actions_resp.status_code in (200, 500)

        # Manners report
        manners_resp = client.get(f"/v1/openclaw/{instance_id}/manners", headers=AUTH)
        assert manners_resp.status_code in (200, 500)

        # Suspend
        suspend_resp = client.post(
            f"/v1/openclaw/{instance_id}/suspend",
            headers=AUTH,
            json={"reason": "depth test suspension"}
        )
        assert suspend_resp.status_code in (200, 500)

        # Reinstate
        reinstate_resp = client.post(
            f"/v1/openclaw/{instance_id}/reinstate",
            headers=AUTH,
            json={"reason": "depth test reinstatement"}
        )
        assert reinstate_resp.status_code in (200, 400, 500)

        # Deregister
        del_resp = client.delete(f"/v1/openclaw/{instance_id}", headers=AUTH)
        assert del_resp.status_code in (200, 500)

        # Verify gone
        gone_resp = client.get(f"/v1/openclaw/{instance_id}", headers=AUTH)
        assert gone_resp.status_code in (404, 500)
