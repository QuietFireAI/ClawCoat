# TB-TEST-INT-011 - TestCrossAgentMessaging · `test_replay_attack_prevented`

**Sheet ID:** TB-TEST-INT-011
**Series:** Individual Test Evidence
**Test File:** `tests/test_integration.py`
**Class:** `TestCrossAgentMessaging`
**Function:** `test_replay_attack_prevented`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Replay attack prevented

## Verdict

VERIFIED - This test passes as part of the 26-test Integration Layer suite. Run the verification command below to confirm independently.

## Source

- `core/signing.py`
- `core/federation.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_integration.py::TestCrossAgentMessaging::test_replay_attack_prevented -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 26 individual proof sheets for `tests/test_integration.py`.
Class-level summary: see the [TB-PROOF-013](../../TB-PROOF-013_message_signing.md) proof sheet.

---

*Sheet TB-TEST-INT-011 | TelsonBase v11.0.1 | March 8, 2026*
