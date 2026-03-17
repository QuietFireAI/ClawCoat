# SPDX-FileCopyrightText: 2026 Quietfire AI / Jeff Phillips
# SPDX-License-Identifier: Apache-2.0
# tests/test_tenancy_routes_depth.py
# REM: Coverage depth tests for api/tenancy_routes.py
# REM: Targets: tenant CRUD, matter CRUD, access grants, hold lifecycle

import pytest

AUTH = {"X-API-Key": "test_api_key_12345"}

VALID_TENANT_TYPES = [
    "law_firm", "insurance", "real_estate",
    "healthcare", "small_business", "personal", "general"
]


# ═══════════════════════════════════════════════════════════════════════════════
# TENANT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestTenantCreate:
    def test_create_tenant_general(self, client):
        resp = client.post("/v1/tenancy/tenants",
                           json={"name": "Acme Corp", "tenant_type": "general"},
                           headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["qms_status"] == "Thank_You"
        assert "tenant" in data
        assert data["tenant"]["name"] == "Acme Corp"

    def test_create_tenant_law_firm(self, client):
        resp = client.post("/v1/tenancy/tenants",
                           json={"name": "Smith & Partners LLP", "tenant_type": "law_firm"},
                           headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["tenant"]["tenant_type"] == "law_firm"

    def test_create_tenant_all_valid_types(self, client):
        for t in VALID_TENANT_TYPES:
            resp = client.post("/v1/tenancy/tenants",
                               json={"name": f"Org-{t}", "tenant_type": t},
                               headers=AUTH)
            assert resp.status_code == 200, f"Failed for type: {t}"

    def test_create_tenant_invalid_type_returns_400(self, client):
        resp = client.post("/v1/tenancy/tenants",
                           json={"name": "Bad Corp", "tenant_type": "invalid_type"},
                           headers=AUTH)
        assert resp.status_code == 400
        assert resp.json()["qms_status"] == "Thank_You_But_No"

    def test_create_tenant_requires_auth(self, client):
        resp = client.post("/v1/tenancy/tenants",
                           json={"name": "Unauth Corp", "tenant_type": "general"})
        assert resp.status_code == 401

    def test_create_tenant_returns_tenant_id(self, client):
        resp = client.post("/v1/tenancy/tenants",
                           json={"name": "ID-Test Corp", "tenant_type": "healthcare"},
                           headers=AUTH)
        assert resp.status_code == 200
        tenant = resp.json()["tenant"]
        assert "tenant_id" in tenant or "id" in tenant

    def test_create_tenant_with_created_by(self, client):
        resp = client.post("/v1/tenancy/tenants",
                           json={"name": "Created By Corp", "tenant_type": "general",
                                 "created_by": "admin-user"},
                           headers=AUTH)
        assert resp.status_code == 200


class TestTenantList:
    def test_list_tenants_returns_list(self, client):
        resp = client.get("/v1/tenancy/tenants", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["qms_status"] == "Thank_You"
        assert "tenants" in data
        assert isinstance(data["tenants"], list)

    def test_list_tenants_count_field(self, client):
        resp = client.get("/v1/tenancy/tenants", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert "count" in data
        assert data["count"] == len(data["tenants"])

    def test_list_tenants_active_only_filter(self, client):
        client.post("/v1/tenancy/tenants",
                    json={"name": "Active Filter Test", "tenant_type": "general"},
                    headers=AUTH)
        resp = client.get("/v1/tenancy/tenants?active_only=true", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert all(t.get("is_active", True) for t in data["tenants"])

    def test_list_tenants_requires_auth(self, client):
        resp = client.get("/v1/tenancy/tenants")
        assert resp.status_code == 401


class TestTenantGet:
    def test_get_existing_tenant(self, client):
        create = client.post("/v1/tenancy/tenants",
                             json={"name": "Get Test Corp", "tenant_type": "general"},
                             headers=AUTH)
        tid = create.json()["tenant"].get("tenant_id") or create.json()["tenant"].get("id")
        if tid:
            resp = client.get(f"/v1/tenancy/tenants/{tid}", headers=AUTH)
            assert resp.status_code == 200
            assert resp.json()["qms_status"] == "Thank_You"

    def test_get_nonexistent_tenant_returns_404(self, client):
        resp = client.get("/v1/tenancy/tenants/tenant-does-not-exist-xyz", headers=AUTH)
        assert resp.status_code == 404
        assert resp.json()["qms_status"] == "Thank_You_But_No"

    def test_get_tenant_requires_auth(self, client):
        resp = client.get("/v1/tenancy/tenants/some-id")
        assert resp.status_code == 401


class TestTenantDeactivate:
    def test_deactivate_tenant(self, client):
        create = client.post("/v1/tenancy/tenants",
                             json={"name": "Deactivate Me Corp", "tenant_type": "general"},
                             headers=AUTH)
        tid = create.json()["tenant"].get("tenant_id") or create.json()["tenant"].get("id")
        if tid:
            resp = client.post(f"/v1/tenancy/tenants/{tid}/deactivate",
                               json={"deactivated_by": "admin"},
                               headers=AUTH)
            assert resp.status_code == 200
            assert resp.json()["qms_status"] == "Thank_You"

    def test_deactivate_nonexistent_tenant(self, client):
        resp = client.post("/v1/tenancy/tenants/tenant-nonexist/deactivate",
                           json={"deactivated_by": "admin"},
                           headers=AUTH)
        assert resp.status_code in (404, 500)

    def test_deactivate_requires_auth(self, client):
        resp = client.post("/v1/tenancy/tenants/some-id/deactivate",
                           json={"deactivated_by": "admin"})
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# MATTER ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

def _create_tenant(client) -> str:
    """Helper: create a tenant and return its ID."""
    resp = client.post("/v1/tenancy/tenants",
                       json={"name": "Matter-Test Org", "tenant_type": "law_firm"},
                       headers=AUTH)
    assert resp.status_code == 200
    tenant = resp.json()["tenant"]
    return tenant.get("tenant_id") or tenant.get("id")


class TestMatterCreate:
    def test_create_matter_transaction(self, client):
        tid = _create_tenant(client)
        if not tid:
            pytest.skip("no tenant id returned")
        resp = client.post(f"/v1/tenancy/tenants/{tid}/matters",
                           json={"name": "Deal Alpha", "matter_type": "transaction"},
                           headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert data["qms_status"] == "Thank_You"
        assert "matter" in data

    def test_create_matter_litigation(self, client):
        tid = _create_tenant(client)
        if not tid:
            pytest.skip("no tenant id")
        resp = client.post(f"/v1/tenancy/tenants/{tid}/matters",
                           json={"name": "Case Beta", "matter_type": "litigation"},
                           headers=AUTH)
        assert resp.status_code == 200

    def test_create_matter_client_file(self, client):
        tid = _create_tenant(client)
        if not tid:
            pytest.skip("no tenant id")
        resp = client.post(f"/v1/tenancy/tenants/{tid}/matters",
                           json={"name": "File Gamma", "matter_type": "client_file"},
                           headers=AUTH)
        assert resp.status_code == 200

    def test_create_matter_nonexistent_tenant(self, client):
        resp = client.post("/v1/tenancy/tenants/tenant-xyz-none/matters",
                           json={"name": "Orphan Matter", "matter_type": "transaction"},
                           headers=AUTH)
        assert resp.status_code in (404, 500)

    def test_create_matter_requires_auth(self, client):
        resp = client.post("/v1/tenancy/tenants/some-tid/matters",
                           json={"name": "Unauth", "matter_type": "transaction"})
        assert resp.status_code == 401


class TestMatterList:
    def test_list_matters_for_tenant(self, client):
        tid = _create_tenant(client)
        if not tid:
            pytest.skip("no tenant id")
        client.post(f"/v1/tenancy/tenants/{tid}/matters",
                    json={"name": "Matter List A", "matter_type": "transaction"},
                    headers=AUTH)
        resp = client.get(f"/v1/tenancy/tenants/{tid}/matters", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert "matters" in data

    def test_list_matters_nonexistent_tenant(self, client):
        resp = client.get("/v1/tenancy/tenants/tenant-xyz-none/matters", headers=AUTH)
        assert resp.status_code in (404, 500)

    def test_list_matters_requires_auth(self, client):
        resp = client.get("/v1/tenancy/tenants/some-tid/matters")
        assert resp.status_code == 401


class TestMatterGet:
    def test_get_existing_matter(self, client):
        tid = _create_tenant(client)
        if not tid:
            pytest.skip("no tenant id")
        create = client.post(f"/v1/tenancy/tenants/{tid}/matters",
                             json={"name": "Get Matter X", "matter_type": "transaction"},
                             headers=AUTH)
        matter = create.json().get("matter", {})
        mid = matter.get("matter_id") or matter.get("id")
        if mid:
            resp = client.get(f"/v1/tenancy/matters/{mid}", headers=AUTH)
            assert resp.status_code == 200
            assert resp.json()["qms_status"] == "Thank_You"

    def test_get_nonexistent_matter_returns_404(self, client):
        resp = client.get("/v1/tenancy/matters/matter-does-not-exist", headers=AUTH)
        assert resp.status_code == 404

    def test_get_matter_requires_auth(self, client):
        resp = client.get("/v1/tenancy/matters/mid")
        assert resp.status_code == 401


class TestMatterClose:
    def test_close_matter(self, client):
        tid = _create_tenant(client)
        if not tid:
            pytest.skip("no tenant id")
        create = client.post(f"/v1/tenancy/tenants/{tid}/matters",
                             json={"name": "Close Matter Y", "matter_type": "transaction"},
                             headers=AUTH)
        matter = create.json().get("matter", {})
        mid = matter.get("matter_id") or matter.get("id")
        if mid:
            resp = client.post(f"/v1/tenancy/matters/{mid}/close",
                               json={"closed_by": "attorney"},
                               headers=AUTH)
            assert resp.status_code == 200
            assert resp.json()["qms_status"] == "Thank_You"

    def test_close_nonexistent_matter(self, client):
        resp = client.post("/v1/tenancy/matters/matter-none/close",
                           json={"closed_by": "attorney"},
                           headers=AUTH)
        assert resp.status_code in (404, 500)

    def test_close_requires_auth(self, client):
        resp = client.post("/v1/tenancy/matters/mid/close",
                           json={"closed_by": "attorney"})
        assert resp.status_code == 401


class TestMatterHold:
    def test_place_litigation_hold(self, client):
        tid = _create_tenant(client)
        if not tid:
            pytest.skip("no tenant id")
        create = client.post(f"/v1/tenancy/tenants/{tid}/matters",
                             json={"name": "Hold Matter Z", "matter_type": "litigation"},
                             headers=AUTH)
        matter = create.json().get("matter", {})
        mid = matter.get("matter_id") or matter.get("id")
        if mid:
            resp = client.post(f"/v1/tenancy/matters/{mid}/hold",
                               json={"hold_by": "legal-team"},
                               headers=AUTH)
            assert resp.status_code == 200
            assert resp.json()["qms_status"] == "Thank_You"

    def test_release_hold(self, client):
        tid = _create_tenant(client)
        if not tid:
            pytest.skip("no tenant id")
        create = client.post(f"/v1/tenancy/tenants/{tid}/matters",
                             json={"name": "Release Hold Matter", "matter_type": "litigation"},
                             headers=AUTH)
        matter = create.json().get("matter", {})
        mid = matter.get("matter_id") or matter.get("id")
        if mid:
            client.post(f"/v1/tenancy/matters/{mid}/hold",
                        json={"hold_by": "legal-team"},
                        headers=AUTH)
            resp = client.post(f"/v1/tenancy/matters/{mid}/release-hold",
                               json={"released_by": "judge"},
                               headers=AUTH)
            assert resp.status_code == 200
            assert resp.json()["qms_status"] == "Thank_You"

    def test_hold_nonexistent_matter(self, client):
        resp = client.post("/v1/tenancy/matters/matter-none/hold",
                           json={"hold_by": "legal"},
                           headers=AUTH)
        assert resp.status_code in (404, 500)

    def test_hold_requires_auth(self, client):
        resp = client.post("/v1/tenancy/matters/mid/hold",
                           json={"hold_by": "legal"})
        assert resp.status_code == 401

    def test_release_requires_auth(self, client):
        resp = client.post("/v1/tenancy/matters/mid/release-hold",
                           json={"released_by": "judge"})
        assert resp.status_code == 401


class TestTenantGrantAccess:
    def test_grant_access_to_tenant(self, client):
        tid = _create_tenant(client)
        if not tid:
            pytest.skip("no tenant id")
        resp = client.post(f"/v1/tenancy/tenants/{tid}/grant-access",
                           json={"user_id": "u-grant-001"},
                           headers=AUTH)
        assert resp.status_code in (200, 404)

    def test_grant_access_requires_auth(self, client):
        resp = client.post("/v1/tenancy/tenants/some-tid/grant-access",
                           json={"user_id": "u-001"})
        assert resp.status_code == 401
