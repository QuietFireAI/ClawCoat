# TB-TEST-SIGN-009 - TestAgentKeyRegistry · `test_verify_invalid_signature`

**Sheet ID:** TB-TEST-SIGN-009
**Series:** Individual Test Evidence
**Test File:** `tests/test_signing.py`
**Class:** `TestAgentKeyRegistry`
**Function:** `test_verify_invalid_signature`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Verify invalid signature

## Verdict

VERIFIED - This test passes as part of the 13-test Cryptographic Message Signing suite. Run the verification command below to confirm independently.

## Source

- `core/signing.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_signing.py::TestAgentKeyRegistry::test_verify_invalid_signature -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 13 individual proof sheets for `tests/test_signing.py`.
Class-level summary: see the [TB-PROOF-013](../../TB-PROOF-013_message_signing.md) proof sheet.

---

*Sheet TB-TEST-SIGN-009 | TelsonBase v11.0.1 | March 8, 2026*
