# TB-TEST-SEC-038 - TestAccessControl · `test_custom_denial_overrides_role_grant`

**Sheet ID:** TB-TEST-SEC-038
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestAccessControl`
**Function:** `test_custom_denial_overrides_role_grant`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> A custom denial on a user overrides what the role would allow - deny wins

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/rbac.py`
- `core/auth.py`
- `core/session_management.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestAccessControl::test_custom_denial_overrides_role_grant -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-045](../../TB-PROOF-045_security_access_control.md) proof sheet.

---

*Sheet TB-TEST-SEC-038 | TelsonBase v11.0.1 | March 8, 2026*
