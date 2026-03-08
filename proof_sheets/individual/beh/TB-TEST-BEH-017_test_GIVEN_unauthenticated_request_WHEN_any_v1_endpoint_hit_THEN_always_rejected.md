# TB-TEST-BEH-017 - TestBehavior_SecurityBoundaries · `test_GIVEN_unauthenticated_request_WHEN_any_v1_endpoint_hit_THEN_always_rejected`

**Sheet ID:** TB-TEST-BEH-017
**Series:** Individual Test Evidence
**Test File:** `tests/test_behavioral.py`
**Class:** `TestBehavior_SecurityBoundaries`
**Function:** `test_GIVEN_unauthenticated_request_WHEN_any_v1_endpoint_hit_THEN_always_rejected`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Given unauthenticated request: when any v1 endpoint hit, the system always rejected

## Verdict

VERIFIED - This test passes as part of the 30-test Behavioral Specification suite. Run the verification command below to confirm independently.

## Source

- `core/auth.py`
- `api/routes.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_behavioral.py::TestBehavior_SecurityBoundaries::test_GIVEN_unauthenticated_request_WHEN_any_v1_endpoint_hit_THEN_always_rejected -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 30 individual proof sheets for `tests/test_behavioral.py`.
Class-level summary: see the [TB-PROOF-BEH](../../TB-PROOF-BEH.md) proof sheet.

---

*Sheet TB-TEST-BEH-017 | TelsonBase v11.0.1 | March 8, 2026*
