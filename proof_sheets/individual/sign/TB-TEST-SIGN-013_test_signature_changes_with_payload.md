# TB-TEST-SIGN-013 - TestMessageSigner · `test_signature_changes_with_payload`

**Sheet ID:** TB-TEST-SIGN-013
**Series:** Individual Test Evidence
**Test File:** `tests/test_signing.py`
**Class:** `TestMessageSigner`
**Function:** `test_signature_changes_with_payload`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Signature changes with payload

## Verdict

VERIFIED - This test passes as part of the 13-test Cryptographic Message Signing suite. Run the verification command below to confirm independently.

## Source

- `core/signing.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_signing.py::TestMessageSigner::test_signature_changes_with_payload -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 13 individual proof sheets for `tests/test_signing.py`.
Class-level summary: see the [TB-PROOF-013](../../TB-PROOF-013_message_signing.md) proof sheet.

---

*Sheet TB-TEST-SIGN-013 | TelsonBase v11.0.1 | March 8, 2026*
