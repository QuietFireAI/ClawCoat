# TB-TEST-SEC-004 - TestAuthSecurity · `test_jwt_token_decode_roundtrip`

**Sheet ID:** TB-TEST-SEC-004
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestAuthSecurity`
**Function:** `test_jwt_token_decode_roundtrip`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> JWT round-trips correctly - subject and permissions claims survive encode/decode

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/auth.py`
- `core/mfa.py`
- `core/session_management.py`
- `core/emergency_access.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestAuthSecurity::test_jwt_token_decode_roundtrip -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-043](../../TB-PROOF-043_security_auth.md) proof sheet.

---

*Sheet TB-TEST-SEC-004 | TelsonBase v11.0.1 | March 8, 2026*
