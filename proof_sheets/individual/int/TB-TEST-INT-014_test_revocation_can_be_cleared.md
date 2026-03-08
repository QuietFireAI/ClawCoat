# TB-TEST-INT-014 - TestKeyRevocation · `test_revocation_can_be_cleared`

**Sheet ID:** TB-TEST-INT-014
**Series:** Individual Test Evidence
**Test File:** `tests/test_integration.py`
**Class:** `TestKeyRevocation`
**Function:** `test_revocation_can_be_cleared`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Revocation can be cleared

## Verdict

VERIFIED - This test passes as part of the 26-test Integration Layer suite. Run the verification command below to confirm independently.

## Source

- `core/signing.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_integration.py::TestKeyRevocation::test_revocation_can_be_cleared -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 26 individual proof sheets for `tests/test_integration.py`.
Class-level summary: see the [TB-PROOF-013](../../TB-PROOF-013_message_signing.md) proof sheet.

---

*Sheet TB-TEST-INT-014 | TelsonBase v11.0.1 | March 8, 2026*
