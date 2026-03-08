# TB-TEST-SEC-037 - TestAccessControl · `test_custom_permission_grants_work`

**Sheet ID:** TB-TEST-SEC-037
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestAccessControl`
**Function:** `test_custom_permission_grants_work`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Custom per-user grants extend beyond the base role

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/rbac.py`
- `core/auth.py`
- `core/session_management.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestAccessControl::test_custom_permission_grants_work -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-045](../../TB-PROOF-045_security_access_control.md) proof sheet.

---

*Sheet TB-TEST-SEC-037 | TelsonBase v11.0.1 | March 8, 2026*
