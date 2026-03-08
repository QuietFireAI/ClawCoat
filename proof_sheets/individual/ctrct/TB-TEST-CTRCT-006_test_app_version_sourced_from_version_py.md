# TB-TEST-CTRCT-006 - TestVersionContract · `test_app_version_sourced_from_version_py`

**Sheet ID:** TB-TEST-CTRCT-006
**Series:** Individual Test Evidence
**Test File:** `tests/test_contracts.py`
**Class:** `TestVersionContract`
**Function:** `test_app_version_sourced_from_version_py`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> App version sourced from version py

## Verdict

VERIFIED - This test passes as part of the 7-test Enum Contract Tripwires suite. Run the verification command below to confirm independently.

## Source

- `version.py`
- `core/config.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_contracts.py::TestVersionContract::test_app_version_sourced_from_version_py -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 7 individual proof sheets for `tests/test_contracts.py`.
Class-level summary: see the [TB-PROOF-CTRCT](../../TB-PROOF-CTRCT.md) proof sheet.

---

*Sheet TB-TEST-CTRCT-006 | TelsonBase v11.0.1 | March 8, 2026*
