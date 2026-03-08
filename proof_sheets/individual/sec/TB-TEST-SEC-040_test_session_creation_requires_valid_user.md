# TB-TEST-SEC-040 - TestAccessControl · `test_session_creation_requires_valid_user`

**Sheet ID:** TB-TEST-SEC-040
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestAccessControl`
**Function:** `test_session_creation_requires_valid_user`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Sessions can only be created for active, valid users

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/rbac.py`
- `core/auth.py`
- `core/session_management.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestAccessControl::test_session_creation_requires_valid_user -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-045](../../TB-PROOF-045_security_access_control.md) proof sheet.

---

*Sheet TB-TEST-SEC-040 | TelsonBase v11.0.1 | March 8, 2026*
