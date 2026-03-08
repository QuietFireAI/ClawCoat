# TB-TEST-SEC-035 - TestAccessControl · `test_permission_check_denies_unlisted`

**Sheet ID:** TB-TEST-SEC-035
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestAccessControl`
**Function:** `test_permission_check_denies_unlisted`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Any permission not explicitly granted is denied by default

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/rbac.py`
- `core/auth.py`
- `core/session_management.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestAccessControl::test_permission_check_denies_unlisted -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-045](../../TB-PROOF-045_security_access_control.md) proof sheet.

---

*Sheet TB-TEST-SEC-035 | TelsonBase v11.0.1 | March 8, 2026*
