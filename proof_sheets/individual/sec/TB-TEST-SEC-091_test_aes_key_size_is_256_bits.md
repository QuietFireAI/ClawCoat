# TB-TEST-SEC-091 - TestCryptographicStandards · `test_aes_key_size_is_256_bits`

**Sheet ID:** TB-TEST-SEC-091
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestCryptographicStandards`
**Function:** `test_aes_key_size_is_256_bits`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> AES key size is exactly 256 bits - not 128, not 192

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/signing.py`
- `core/audit.py`
- `core/mfa.py`
- `core/secure_storage.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestCryptographicStandards::test_aes_key_size_is_256_bits -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-050](../../TB-PROOF-050_security_cryptography.md) proof sheet.

---

*Sheet TB-TEST-SEC-091 | TelsonBase v11.0.1 | March 8, 2026*
