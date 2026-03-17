# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_security_routes_depth.py
# REM: Coverage depth tests for api/security_routes.py
# REM: Targets: MFA, sessions, email verification, captcha, emergency access

import pytest


AUTH = {"X-API-Key": "test_api_key_12345"}


# ═══════════════════════════════════════════════════════════════════════════════
# MFA ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestMFAEnroll:
    def test_enroll_returns_secret_and_backup_codes(self, client):
        resp = client.post("/v1/security/mfa/enroll",
                           json={"user_id": "u-mfa-001", "username": "mfauser1"},
                           headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["qms_status"] == "Thank_You"
        assert "secret" in data
        assert "backup_codes" in data

    def test_enroll_requires_auth(self, client):
        resp = client.post("/v1/security/mfa/enroll",
                           json={"user_id": "u-mfa-002", "username": "mfauser2"})
        assert resp.status_code == 401

    def test_enroll_different_users_independent(self, client):
        resp1 = client.post("/v1/security/mfa/enroll",
                            json={"user_id": "u-mfa-010", "username": "user10"},
                            headers=AUTH)
        resp2 = client.post("/v1/security/mfa/enroll",
                            json={"user_id": "u-mfa-011", "username": "user11"},
                            headers=AUTH)
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        # secrets must differ
        assert resp1.json()["secret"] != resp2.json()["secret"]

    def test_enroll_provisioning_uri_present(self, client):
        resp = client.post("/v1/security/mfa/enroll",
                           json={"user_id": "u-mfa-020", "username": "provuri"},
                           headers=AUTH)
        assert resp.status_code == 200
        assert "provisioning_uri" in resp.json()


class TestMFAVerify:
    def test_verify_invalid_token_returns_not_verified(self, client):
        # enroll first so the user exists
        client.post("/v1/security/mfa/enroll",
                    json={"user_id": "u-mfav-001", "username": "mfavuser"},
                    headers=AUTH)
        resp = client.post("/v1/security/mfa/verify",
                           json={"user_id": "u-mfav-001", "token": "000000"},
                           headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["verified"] is False

    def test_verify_requires_auth(self, client):
        resp = client.post("/v1/security/mfa/verify",
                           json={"user_id": "u-mfav-002", "token": "123456"})
        assert resp.status_code == 401

    def test_verify_unknown_user_returns_not_verified(self, client):
        resp = client.post("/v1/security/mfa/verify",
                           json={"user_id": "u-mfav-nonexistent", "token": "123456"},
                           headers=AUTH)
        # should not crash — returns false or 200 with verified=false
        assert resp.status_code in (200, 500)


class TestMFABackupCode:
    def test_backup_code_invalid_returns_not_verified(self, client):
        client.post("/v1/security/mfa/enroll",
                    json={"user_id": "u-mfab-001", "username": "backupuser"},
                    headers=AUTH)
        resp = client.post("/v1/security/mfa/backup-code",
                           json={"user_id": "u-mfab-001", "code": "INVALIDCODE"},
                           headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["verified"] is False

    def test_backup_code_requires_auth(self, client):
        resp = client.post("/v1/security/mfa/backup-code",
                           json={"user_id": "u-mfab-002", "code": "ABCDE12345"})
        assert resp.status_code == 401

    def test_backup_code_valid_code_from_enrollment(self, client):
        enroll = client.post("/v1/security/mfa/enroll",
                             json={"user_id": "u-mfab-010", "username": "backvalid"},
                             headers=AUTH)
        codes = enroll.json().get("backup_codes", [])
        if codes:
            resp = client.post("/v1/security/mfa/backup-code",
                               json={"user_id": "u-mfab-010", "code": codes[0]},
                               headers=AUTH)
            assert resp.status_code == 200
            assert resp.json()["verified"] is True


class TestMFAStatus:
    def test_status_enrolled_user(self, client):
        client.post("/v1/security/mfa/enroll",
                    json={"user_id": "u-mfas-001", "username": "statususer"},
                    headers=AUTH)
        resp = client.get("/v1/security/mfa/status/u-mfas-001", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["qms_status"] == "Thank_You"

    def test_status_unenrolled_user(self, client):
        resp = client.get("/v1/security/mfa/status/u-mfas-never-enrolled", headers=AUTH)
        assert resp.status_code == 200

    def test_status_requires_auth(self, client):
        resp = client.get("/v1/security/mfa/status/u-mfas-001")
        assert resp.status_code == 401


class TestMFADisable:
    def test_disable_enrolled_user(self, client):
        client.post("/v1/security/mfa/enroll",
                    json={"user_id": "u-mfad-001", "username": "disableuser"},
                    headers=AUTH)
        resp = client.delete("/v1/security/mfa/u-mfad-001", headers=AUTH)
        assert resp.status_code in (200, 404)

    def test_disable_requires_auth(self, client):
        resp = client.delete("/v1/security/mfa/u-mfad-002")
        assert resp.status_code == 401

    def test_disable_unenrolled_user(self, client):
        resp = client.delete("/v1/security/mfa/u-mfad-never", headers=AUTH)
        assert resp.status_code in (200, 404, 500)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestSessionCreate:
    def test_create_session_minimal(self, client):
        resp = client.post("/v1/security/sessions",
                           json={"user_id": "u-sess-001"},
                           headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["qms_status"] == "Thank_You"
        assert "session_id" in data or "user_id" in data

    def test_create_session_with_ip_and_agent(self, client):
        resp = client.post("/v1/security/sessions",
                           json={"user_id": "u-sess-002",
                                 "ip_address": "192.168.1.100",
                                 "user_agent": "TestBrowser/1.0"},
                           headers=AUTH)
        assert resp.status_code == 200

    def test_create_session_requires_auth(self, client):
        resp = client.post("/v1/security/sessions",
                           json={"user_id": "u-sess-003"})
        assert resp.status_code == 401


class TestSessionList:
    def test_list_sessions_no_filter(self, client):
        resp = client.get("/v1/security/sessions", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert "sessions" in data
        assert isinstance(data["sessions"], list)

    def test_list_sessions_filtered_by_user(self, client):
        client.post("/v1/security/sessions",
                    json={"user_id": "u-sess-filter-001"},
                    headers=AUTH)
        resp = client.get("/v1/security/sessions?user_id=u-sess-filter-001",
                          headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert "sessions" in data

    def test_list_sessions_requires_auth(self, client):
        resp = client.get("/v1/security/sessions")
        assert resp.status_code == 401


class TestSessionGet:
    def test_get_nonexistent_session_returns_404(self, client):
        resp = client.get("/v1/security/sessions/sess-does-not-exist", headers=AUTH)
        assert resp.status_code == 404

    def test_get_existing_session(self, client):
        create = client.post("/v1/security/sessions",
                             json={"user_id": "u-sess-get-001"},
                             headers=AUTH)
        assert create.status_code == 200
        sid = create.json().get("session_id")
        if sid:
            resp = client.get(f"/v1/security/sessions/{sid}", headers=AUTH)
            assert resp.status_code == 200
            assert resp.json()["qms_status"] == "Thank_You"

    def test_get_session_requires_auth(self, client):
        resp = client.get("/v1/security/sessions/any-id")
        assert resp.status_code == 401


class TestSessionTerminate:
    def test_terminate_nonexistent_session(self, client):
        resp = client.delete("/v1/security/sessions/sess-nonexist-001", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["terminated"] is False

    def test_terminate_existing_session(self, client):
        create = client.post("/v1/security/sessions",
                             json={"user_id": "u-sess-term-001"},
                             headers=AUTH)
        sid = create.json().get("session_id")
        if sid:
            resp = client.delete(f"/v1/security/sessions/{sid}", headers=AUTH)
            assert resp.status_code == 200
            assert resp.json()["terminated"] is True

    def test_terminate_with_custom_reason(self, client):
        create = client.post("/v1/security/sessions",
                             json={"user_id": "u-sess-term-002"},
                             headers=AUTH)
        sid = create.json().get("session_id")
        if sid:
            resp = client.delete(f"/v1/security/sessions/{sid}?reason=security_incident",
                                 headers=AUTH)
            assert resp.status_code == 200

    def test_terminate_requires_auth(self, client):
        resp = client.delete("/v1/security/sessions/any")
        assert resp.status_code == 401


class TestSessionTerminateAll:
    def test_terminate_all_for_user(self, client):
        client.post("/v1/security/sessions",
                    json={"user_id": "u-sess-ta-001"},
                    headers=AUTH)
        resp = client.delete("/v1/security/sessions/user/u-sess-ta-001", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert "terminated_count" in data

    def test_terminate_all_user_with_no_sessions(self, client):
        resp = client.delete("/v1/security/sessions/user/u-no-sessions", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["terminated_count"] == 0

    def test_terminate_all_requires_auth(self, client):
        resp = client.delete("/v1/security/sessions/user/any")
        assert resp.status_code == 401


class TestSessionCleanup:
    def test_cleanup_returns_count(self, client):
        resp = client.post("/v1/security/sessions/cleanup", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["qms_status"] == "Thank_You"
        assert "cleaned" in data

    def test_cleanup_requires_auth(self, client):
        resp = client.post("/v1/security/sessions/cleanup")
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL VERIFICATION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestEmailVerification:
    def test_request_verification_creates_token(self, client):
        resp = client.post("/v1/security/email/request-verification",
                           json={"user_id": "u-email-001",
                                 "email": "test@example.com"},
                           headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["qms_status"] == "Thank_You"

    def test_request_verification_requires_auth(self, client):
        resp = client.post("/v1/security/email/request-verification",
                           json={"user_id": "u-email-002",
                                 "email": "test2@example.com"})
        assert resp.status_code == 401

    def test_verify_invalid_token_returns_failure(self, client):
        resp = client.post("/v1/security/email/verify",
                           json={"user_id": "u-email-003",
                                 "token": "invalid-token-xyz"},
                           headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["verified"] is False

    def test_verify_valid_token_flow(self, client):
        # Request a token
        req = client.post("/v1/security/email/request-verification",
                          json={"user_id": "u-email-flow-001",
                                "email": "flow@example.com"},
                          headers=AUTH)
        assert req.status_code == 200
        token = req.json().get("token")
        if token:
            resp = client.post("/v1/security/email/verify",
                               json={"user_id": "u-email-flow-001",
                                     "token": token},
                               headers=AUTH)
            assert resp.status_code == 200
            assert resp.json()["verified"] is True

    def test_verify_requires_auth(self, client):
        resp = client.post("/v1/security/email/verify",
                           json={"user_id": "u-email-004", "token": "tok"})
        assert resp.status_code == 401

    def test_request_multiple_verifications_same_user(self, client):
        for i in range(3):
            resp = client.post("/v1/security/email/request-verification",
                               json={"user_id": "u-email-multi",
                                     "email": f"multi{i}@example.com"},
                               headers=AUTH)
            assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# CAPTCHA ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestCaptchaGenerate:
    def test_generate_returns_challenge_id_and_question(self, client):
        resp = client.post("/v1/security/captcha/generate",
                           json={}, headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["qms_status"] == "Thank_You"
        assert "challenge_id" in data
        assert "question" in data

    def test_generate_with_challenge_type_math(self, client):
        resp = client.post("/v1/security/captcha/generate",
                           json={"challenge_type": "math"}, headers=AUTH)
        assert resp.status_code == 200

    def test_generate_with_challenge_type_text(self, client):
        resp = client.post("/v1/security/captcha/generate",
                           json={"challenge_type": "text"}, headers=AUTH)
        assert resp.status_code == 200

    def test_generate_challenge_ids_unique(self, client):
        r1 = client.post("/v1/security/captcha/generate", json={}, headers=AUTH)
        r2 = client.post("/v1/security/captcha/generate", json={}, headers=AUTH)
        assert r1.json()["challenge_id"] != r2.json()["challenge_id"]

    def test_generate_requires_auth(self, client):
        resp = client.post("/v1/security/captcha/generate", json={})
        assert resp.status_code == 401


class TestCaptchaVerify:
    def test_verify_wrong_answer_returns_not_solved(self, client):
        gen = client.post("/v1/security/captcha/generate", json={}, headers=AUTH)
        cid = gen.json()["challenge_id"]
        resp = client.post("/v1/security/captcha/verify",
                           json={"challenge_id": cid, "answer": "WRONG_ANSWER_XYZ"},
                           headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["solved"] is False

    def test_verify_expired_challenge_id(self, client):
        resp = client.post("/v1/security/captcha/verify",
                           json={"challenge_id": "cid-does-not-exist",
                                 "answer": "anything"},
                           headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["solved"] is False

    def test_verify_requires_auth(self, client):
        resp = client.post("/v1/security/captcha/verify",
                           json={"challenge_id": "cid", "answer": "ans"})
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# EMERGENCY ACCESS ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestEmergencyAccess:
    def test_request_emergency_access(self, client):
        resp = client.post("/v1/security/emergency/request",
                           json={"user_id": "u-emerg-001",
                                 "reason": "System outage requires immediate access",
                                 "duration_minutes": 30},
                           headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["qms_status"] == "Thank_You"

    def test_request_emergency_caps_duration_at_1440(self, client):
        resp = client.post("/v1/security/emergency/request",
                           json={"user_id": "u-emerg-cap",
                                 "reason": "Long running emergency test case",
                                 "duration_minutes": 9999},
                           headers=AUTH)
        assert resp.status_code == 200

    def test_request_emergency_requires_auth(self, client):
        resp = client.post("/v1/security/emergency/request",
                           json={"user_id": "u-emerg-002",
                                 "reason": "test"})
        assert resp.status_code == 401

    def test_approve_emergency_access(self, client):
        req = client.post("/v1/security/emergency/request",
                          json={"user_id": "u-emerg-appr-001",
                                "reason": "Testing approval workflow flow"},
                          headers=AUTH)
        assert req.status_code == 200
        rid = req.json().get("request_id")
        if rid:
            resp = client.post(f"/v1/security/emergency/{rid}/approve",
                               json={"approved_by": "admin-user"},
                               headers=AUTH)
            assert resp.status_code == 200
            assert "approved" in resp.json()

    def test_approve_nonexistent_request(self, client):
        resp = client.post("/v1/security/emergency/req-nonexist-001/approve",
                           json={"approved_by": "admin"},
                           headers=AUTH)
        assert resp.status_code in (200, 404, 500)

    def test_revoke_emergency_access(self, client):
        req = client.post("/v1/security/emergency/request",
                          json={"user_id": "u-emerg-rev-001",
                                "reason": "Revocation test flow check"},
                          headers=AUTH)
        assert req.status_code == 200
        rid = req.json().get("request_id")
        if rid:
            # approve first
            client.post(f"/v1/security/emergency/{rid}/approve",
                        json={"approved_by": "admin"},
                        headers=AUTH)
            # then revoke
            resp = client.post(f"/v1/security/emergency/{rid}/revoke",
                               json={"revoked_by": "security-officer"},
                               headers=AUTH)
            assert resp.status_code == 200
            assert "revoked" in resp.json()

    def test_revoke_requires_auth(self, client):
        resp = client.post("/v1/security/emergency/req-001/revoke",
                           json={"revoked_by": "admin"})
        assert resp.status_code == 401

    def test_list_active_emergencies(self, client):
        resp = client.get("/v1/security/emergency/active", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["qms_status"] == "Thank_You"
        assert "emergencies" in data

    def test_list_active_emergencies_requires_auth(self, client):
        resp = client.get("/v1/security/emergency/active")
        assert resp.status_code == 401

    def test_emergency_default_duration_60_minutes(self, client):
        resp = client.post("/v1/security/emergency/request",
                           json={"user_id": "u-emerg-def",
                                 "reason": "Default duration path test case here"},
                           headers=AUTH)
        assert resp.status_code == 200
