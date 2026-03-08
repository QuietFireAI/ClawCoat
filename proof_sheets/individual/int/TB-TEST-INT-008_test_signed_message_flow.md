# TB-TEST-INT-008 - TestCrossAgentMessaging · `test_signed_message_flow`

**Sheet ID:** TB-TEST-INT-008
**Series:** Individual Test Evidence
**Test File:** `tests/test_integration.py`
**Class:** `TestCrossAgentMessaging`
**Function:** `test_signed_message_flow`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Signed message flow

## Verdict

VERIFIED - This test passes as part of the 26-test Integration Layer suite. Run the verification command below to confirm independently.

## Source

- `core/signing.py`
- `core/federation.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_integration.py::TestCrossAgentMessaging::test_signed_message_flow -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 26 individual proof sheets for `tests/test_integration.py`.
Class-level summary: see the [TB-PROOF-013](../../TB-PROOF-013_message_signing.md) proof sheet.

---

*Sheet TB-TEST-INT-008 | TelsonBase v11.0.1 | March 8, 2026*
