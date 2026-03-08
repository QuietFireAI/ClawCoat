# TB-TEST-SEC-071 - TestDataProtection · `test_legal_hold_blocks_deletion`

**Sheet ID:** TB-TEST-SEC-071
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestDataProtection`
**Function:** `test_legal_hold_blocks_deletion`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Records under legal hold cannot be deleted - deletion returns an error

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/phi_deidentification.py`
- `core/minimum_necessary.py`
- `core/legal_hold.py`
- `core/data_retention.py`
- `core/tenancy.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestDataProtection::test_legal_hold_blocks_deletion -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-048](../../TB-PROOF-048_security_data_protection.md) proof sheet.

---

*Sheet TB-TEST-SEC-071 | TelsonBase v11.0.1 | March 8, 2026*
