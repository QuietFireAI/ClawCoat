# TB-TEST-BEH-020 - TestBehavior_SystemResilience · `test_GIVEN_system_running_WHEN_system_status_requested_THEN_returns_status`

**Sheet ID:** TB-TEST-BEH-020
**Series:** Individual Test Evidence
**Test File:** `tests/test_behavioral.py`
**Class:** `TestBehavior_SystemResilience`
**Function:** `test_GIVEN_system_running_WHEN_system_status_requested_THEN_returns_status`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Given system running: when system status requested, the system returns status

## Verdict

VERIFIED - This test passes as part of the 30-test Behavioral Specification suite. Run the verification command below to confirm independently.

## Source

- `api/routes.py`
- `core/config.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_behavioral.py::TestBehavior_SystemResilience::test_GIVEN_system_running_WHEN_system_status_requested_THEN_returns_status -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 30 individual proof sheets for `tests/test_behavioral.py`.
Class-level summary: see the [TB-PROOF-BEH](../../TB-PROOF-BEH.md) proof sheet.

---

*Sheet TB-TEST-BEH-020 | TelsonBase v11.0.1 | March 8, 2026*
