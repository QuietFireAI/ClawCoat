# TB-TEST-SIGN-002 - TestSignedAgentMessage · `test_signing_payload_deterministic`

**Sheet ID:** TB-TEST-SIGN-002
**Series:** Individual Test Evidence
**Test File:** `tests/test_signing.py`
**Class:** `TestSignedAgentMessage`
**Function:** `test_signing_payload_deterministic`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Signing payload deterministic

## Verdict

VERIFIED - This test passes as part of the 13-test Cryptographic Message Signing suite. Run the verification command below to confirm independently.

## Source

- `core/signing.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_signing.py::TestSignedAgentMessage::test_signing_payload_deterministic -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 13 individual proof sheets for `tests/test_signing.py`.
Class-level summary: see the [TB-PROOF-013](../../TB-PROOF-013_message_signing.md) proof sheet.

---

*Sheet TB-TEST-SIGN-002 | TelsonBase v11.0.1 | March 8, 2026*
