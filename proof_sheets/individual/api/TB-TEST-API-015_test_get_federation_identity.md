# TB-TEST-API-015 - TestFederationEndpoints · `test_get_federation_identity`

**Sheet ID:** TB-TEST-API-015
**Series:** Individual Test Evidence
**Test File:** `tests/test_api.py`
**Class:** `TestFederationEndpoints`
**Function:** `test_get_federation_identity`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Get federation identity

## Verdict

VERIFIED - This test passes as part of the 19-test API Endpoint Smoke Tests suite. Run the verification command below to confirm independently.

## Source

- `api/routes.py`
- `core/federation.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_api.py::TestFederationEndpoints::test_get_federation_identity -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 19 individual proof sheets for `tests/test_api.py`.
Class-level summary: see the [TB-PROOF-API](../../TB-PROOF-API.md) proof sheet.

---

*Sheet TB-TEST-API-015 | TelsonBase v11.0.1 | March 8, 2026*
