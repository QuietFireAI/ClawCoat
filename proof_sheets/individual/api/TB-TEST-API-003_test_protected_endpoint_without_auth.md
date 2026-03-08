# TB-TEST-API-003 - TestAuthentication · `test_protected_endpoint_without_auth`

**Sheet ID:** TB-TEST-API-003
**Series:** Individual Test Evidence
**Test File:** `tests/test_api.py`
**Class:** `TestAuthentication`
**Function:** `test_protected_endpoint_without_auth`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Protected endpoint without auth

## Verdict

VERIFIED - This test passes as part of the 19-test API Endpoint Smoke Tests suite. Run the verification command below to confirm independently.

## Source

- `core/openclaw.py`
- `core/auth.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_api.py::TestAuthentication::test_protected_endpoint_without_auth -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 19 individual proof sheets for `tests/test_api.py`.
Class-level summary: see the [TB-PROOF-API](../../TB-PROOF-API.md) proof sheet.

---

*Sheet TB-TEST-API-003 | TelsonBase v11.0.1 | March 8, 2026*
