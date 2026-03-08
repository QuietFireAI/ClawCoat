# TB-TEST-SEC-092 - TestCryptographicStandards · `test_gcm_nonce_size_is_96_bits`

**Sheet ID:** TB-TEST-SEC-092
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestCryptographicStandards`
**Function:** `test_gcm_nonce_size_is_96_bits`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> GCM nonce size is 96 bits - NIST-recommended for AES-GCM

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/signing.py`
- `core/audit.py`
- `core/mfa.py`
- `core/secure_storage.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestCryptographicStandards::test_gcm_nonce_size_is_96_bits -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-050](../../TB-PROOF-050_security_cryptography.md) proof sheet.

---

*Sheet TB-TEST-SEC-092 | TelsonBase v11.0.1 | March 8, 2026*
