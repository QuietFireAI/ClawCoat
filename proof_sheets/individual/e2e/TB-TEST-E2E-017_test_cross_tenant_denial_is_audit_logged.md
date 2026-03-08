# TB-TEST-E2E-017 - TestTenantIsolation · `test_cross_tenant_denial_is_audit_logged`

**Sheet ID:** TB-TEST-E2E-017
**Series:** Individual Test Evidence
**Test File:** `tests/test_e2e_integration.py`
**Class:** `TestTenantIsolation`
**Function:** `test_cross_tenant_denial_is_audit_logged`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Cross tenant denial is audit logged

## Verdict

VERIFIED - This test passes as part of the 29-test End-to-End Integration suite. Run the verification command below to confirm independently.

## Source

- `core/tenancy.py`
- `core/rbac.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_e2e_integration.py::TestTenantIsolation::test_cross_tenant_denial_is_audit_logged -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 29 individual proof sheets for `tests/test_e2e_integration.py`.
Class-level summary: see the [TB-PROOF-042](../../TB-PROOF-042_tenant_access_control.md) proof sheet.

---

*Sheet TB-TEST-E2E-017 | TelsonBase v11.0.1 | March 8, 2026*
