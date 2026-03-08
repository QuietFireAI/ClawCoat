# TB-TEST-E2E-005 - TestUserLifecycle · `test_profile_with_jwt`

**Sheet ID:** TB-TEST-E2E-005
**Series:** Individual Test Evidence
**Test File:** `tests/test_e2e_integration.py`
**Class:** `TestUserLifecycle`
**Function:** `test_profile_with_jwt`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Profile with jwt

## Verdict

VERIFIED - This test passes as part of the 29-test End-to-End Integration suite. Run the verification command below to confirm independently.

## Source

- `api/routes.py`
- `core/auth.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_e2e_integration.py::TestUserLifecycle::test_profile_with_jwt -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 29 individual proof sheets for `tests/test_e2e_integration.py`.
Class-level summary: see the [TB-PROOF-E2E](../../TB-PROOF-E2E.md) proof sheet.

---

*Sheet TB-TEST-E2E-005 | TelsonBase v11.0.1 | March 8, 2026*
