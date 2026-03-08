# TB-TEST-BEH-019 - TestBehavior_SecurityBoundaries · `test_GIVEN_valid_api_key_WHEN_token_requested_THEN_jwt_issued`

**Sheet ID:** TB-TEST-BEH-019
**Series:** Individual Test Evidence
**Test File:** `tests/test_behavioral.py`
**Class:** `TestBehavior_SecurityBoundaries`
**Function:** `test_GIVEN_valid_api_key_WHEN_token_requested_THEN_jwt_issued`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Given valid api key: when token requested, the system jwt issued

## Verdict

VERIFIED - This test passes as part of the 30-test Behavioral Specification suite. Run the verification command below to confirm independently.

## Source

- `core/auth.py`
- `api/routes.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_behavioral.py::TestBehavior_SecurityBoundaries::test_GIVEN_valid_api_key_WHEN_token_requested_THEN_jwt_issued -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 30 individual proof sheets for `tests/test_behavioral.py`.
Class-level summary: see the [TB-PROOF-BEH](../../TB-PROOF-BEH.md) proof sheet.

---

*Sheet TB-TEST-BEH-019 | TelsonBase v11.0.1 | March 8, 2026*
