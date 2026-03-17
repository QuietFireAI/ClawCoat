# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_core_metrics_depth.py
# REM: Depth tests for core/metrics.py — path normalisation + helper smoke tests

import sys
from unittest.mock import MagicMock, patch

# REM: Stub prometheus_client and starlette if not installed
# (CI Docker has them; local dev Python 3.14 may not)
for _mod in [
    "prometheus_client",
    "starlette",
    "starlette.middleware",
    "starlette.middleware.base",
    "fastapi",
]:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

import pytest

# REM: Import the module under test after stubs are in place
from core.metrics import (
    MetricsMiddleware,
    record_auth,
    record_qms_message,
    record_agent_action,
    record_anomaly,
    record_rate_limit,
    record_approval,
    set_pending_approvals,
    record_federation_message,
    set_federation_relationships,
    set_sovereign_score,
    set_system_info,
)


# ═══════════════════════════════════════════════════════════════════════════════
# MetricsMiddleware._normalize_path — pure static method
# ═══════════════════════════════════════════════════════════════════════════════

class TestNormalizePath:
    """REM: _normalize_path collapses variable-looking segments to {id}."""

    def test_short_segment_unchanged(self):
        assert MetricsMiddleware._normalize_path("/v1/agents") == "/v1/agents"

    def test_root_path(self):
        assert MetricsMiddleware._normalize_path("/") == "/"

    def test_plain_multi_segment(self):
        assert MetricsMiddleware._normalize_path("/v1/agents/list") == "/v1/agents/list"

    def test_long_hex_segment_normalized(self):
        # More than 8 chars + at least one digit → {id}
        result = MetricsMiddleware._normalize_path("/v1/agents/signing/keys/abc1234567")
        assert result.endswith("/{id}")

    def test_uuid_segment_normalized(self):
        uuid = "550e8400-e29b-41d4-a716-446655440000"
        result = MetricsMiddleware._normalize_path(f"/v1/entities/{uuid}")
        assert "{id}" in result

    def test_short_segment_not_normalized(self):
        # 8 chars or fewer → keep as-is, even if digits present
        result = MetricsMiddleware._normalize_path("/v1/route/abc12345")
        # "abc12345" is exactly 8 chars → NOT normalized (len > 8 required)
        assert "{id}" not in result

    def test_nine_char_with_digit_normalized(self):
        # 9 chars with a digit → normalized
        result = MetricsMiddleware._normalize_path("/v1/path/abc123456")
        assert "{id}" in result

    def test_long_alpha_only_not_normalized(self):
        # No digit in segment → not normalized even if long
        result = MetricsMiddleware._normalize_path("/v1/endpoints/longalphaonly")
        assert "{id}" not in result

    def test_known_soc_control_id_not_normalized(self):
        # "CC6.1" is short → not normalized
        result = MetricsMiddleware._normalize_path("/v1/compliance/CC6.1")
        assert "CC6.1" in result

    def test_multiple_variable_segments(self):
        # Two long+digit segments
        result = MetricsMiddleware._normalize_path(
            "/v1/fed/abc123456789/messages/xyz987654321"
        )
        assert result.count("{id}") == 2

    def test_metrics_path_preserved(self):
        assert MetricsMiddleware._normalize_path("/metrics") == "/metrics"

    def test_health_path_preserved(self):
        assert MetricsMiddleware._normalize_path("/health") == "/health"

    def test_preserves_leading_slash(self):
        result = MetricsMiddleware._normalize_path("/v1/status")
        assert result.startswith("/")

    def test_trailing_slash_handled(self):
        # strip('/').split('/') → leading/trailing empty strings handled
        result = MetricsMiddleware._normalize_path("/v1/agents/")
        assert isinstance(result, str)


# ═══════════════════════════════════════════════════════════════════════════════
# EXCLUDED_PATHS constant
# ═══════════════════════════════════════════════════════════════════════════════

class TestExcludedPaths:
    def test_metrics_excluded(self):
        assert "/metrics" in MetricsMiddleware.EXCLUDED_PATHS

    def test_health_excluded(self):
        assert "/health" in MetricsMiddleware.EXCLUDED_PATHS

    def test_favicon_excluded(self):
        assert "/favicon.ico" in MetricsMiddleware.EXCLUDED_PATHS

    def test_api_not_excluded(self):
        assert "/v1/agents" not in MetricsMiddleware.EXCLUDED_PATHS


# ═══════════════════════════════════════════════════════════════════════════════
# Helper functions — smoke tests (mocked metrics objects)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRecordHelpers:
    """REM: Verify helpers call metric labels/inc without raising."""

    def test_record_auth_success(self):
        record_auth("api_key", success=True)  # should not raise

    def test_record_auth_failure(self):
        record_auth("jwt", success=False)

    def test_record_qms_message(self):
        record_qms_message("Thank_You")

    def test_record_qms_message_no(self):
        record_qms_message("Thank_You_But_No")

    def test_record_agent_action(self):
        record_agent_action("agent-1", "read_file")

    def test_record_anomaly(self):
        record_anomaly("high")

    def test_record_rate_limit(self):
        record_rate_limit("/v1/mcp/call")

    def test_record_approval_approved(self):
        record_approval("approved")

    def test_record_approval_denied(self):
        record_approval("denied")

    def test_set_pending_approvals(self):
        set_pending_approvals(5)

    def test_set_pending_approvals_zero(self):
        set_pending_approvals(0)

    def test_record_federation_message_inbound(self):
        record_federation_message("inbound")

    def test_record_federation_message_outbound(self):
        record_federation_message("outbound")

    def test_set_federation_relationships(self):
        set_federation_relationships(3)

    def test_set_sovereign_score_no_factors(self):
        set_sovereign_score(75.0)

    def test_set_sovereign_score_with_factors(self):
        set_sovereign_score(80.0, factors={"llm_locality": 90.0, "data_residency": 85.0})

    def test_set_system_info(self):
        set_system_info("11.0.1", instance_id="test-01")

    def test_set_system_info_no_instance(self):
        set_system_info("11.0.1")
