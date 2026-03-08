# TB-TEST-SEC-067 - TestDataProtection · `test_minimum_necessary_viewer_limited_scope`

**Sheet ID:** TB-TEST-SEC-067
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestDataProtection`
**Function:** `test_minimum_necessary_viewer_limited_scope`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Viewers receive only fields within their minimum necessary scope

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
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestDataProtection::test_minimum_necessary_viewer_limited_scope -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-048](../../TB-PROOF-048_security_data_protection.md) proof sheet.

---

*Sheet TB-TEST-SEC-067 | TelsonBase v11.0.1 | March 8, 2026*
