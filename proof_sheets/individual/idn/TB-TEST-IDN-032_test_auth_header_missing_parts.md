# TB-TEST-IDN-032 - TestAuthFlow · `test_auth_header_missing_parts`

**Sheet ID:** TB-TEST-IDN-032
**Series:** Individual Test Evidence
**Test File:** `tests/test_identiclaw.py`
**Class:** `TestAuthFlow`
**Function:** `test_auth_header_missing_parts`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Auth header missing parts

## Verdict

VERIFIED - This test passes as part of the 50-test W3C DID Agent Identity suite. Run the verification command below to confirm independently.

## Source

- `core/identiclaw.py`
- `core/auth.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_identiclaw.py::TestAuthFlow::test_auth_header_missing_parts -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 50 individual proof sheets for `tests/test_identiclaw.py`.
Class-level summary: see the [TB-PROOF-IDN](../../TB-PROOF-IDN.md) proof sheet.

---

*Sheet TB-TEST-IDN-032 | TelsonBase v11.0.1 | March 8, 2026*
