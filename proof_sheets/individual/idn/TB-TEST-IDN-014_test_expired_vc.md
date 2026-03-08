# TB-TEST-IDN-014 - TestVCValidation · `test_expired_vc`

**Sheet ID:** TB-TEST-IDN-014
**Series:** Individual Test Evidence
**Test File:** `tests/test_identiclaw.py`
**Class:** `TestVCValidation`
**Function:** `test_expired_vc`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Expired vc

## Verdict

VERIFIED - This test passes as part of the 50-test W3C DID Agent Identity suite. Run the verification command below to confirm independently.

## Source

- `core/identiclaw.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_identiclaw.py::TestVCValidation::test_expired_vc -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 50 individual proof sheets for `tests/test_identiclaw.py`.
Class-level summary: see the [TB-PROOF-IDN](../../TB-PROOF-IDN.md) proof sheet.

---

*Sheet TB-TEST-IDN-014 | TelsonBase v11.0.1 | March 8, 2026*
