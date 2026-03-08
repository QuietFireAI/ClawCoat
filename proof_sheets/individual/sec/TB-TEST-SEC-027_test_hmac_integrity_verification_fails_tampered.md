# TB-TEST-SEC-027 - TestEncryptionIntegrity · `test_hmac_integrity_verification_fails_tampered`

**Sheet ID:** TB-TEST-SEC-027
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestEncryptionIntegrity`
**Function:** `test_hmac_integrity_verification_fails_tampered`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> HMAC verification rejects a tampered payload

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/secure_storage.py`
- `core/signing.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestEncryptionIntegrity::test_hmac_integrity_verification_fails_tampered -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-044](../../TB-PROOF-044_security_encryption.md) proof sheet.

---

*Sheet TB-TEST-SEC-027 | TelsonBase v11.0.1 | March 8, 2026*
