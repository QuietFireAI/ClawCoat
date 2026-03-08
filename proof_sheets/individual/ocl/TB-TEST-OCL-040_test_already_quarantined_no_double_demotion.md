# TB-TEST-OCL-040 - TestMannersAutoDemotion · `test_already_quarantined_no_double_demotion`

**Sheet ID:** TB-TEST-OCL-040
**Series:** Individual Test Evidence
**Test File:** `tests/test_openclaw.py`
**Class:** `TestMannersAutoDemotion`
**Function:** `test_already_quarantined_no_double_demotion`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Already quarantined no double demotion

## Verdict

VERIFIED - This test passes as part of the 55-test OpenClaw Governance suite. Run the verification command below to confirm independently.

## Source

- `core/openclaw.py`
- `core/manners.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_openclaw.py::TestMannersAutoDemotion::test_already_quarantined_no_double_demotion -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 55 individual proof sheets for `tests/test_openclaw.py`.
Class-level summary: see the [TB-PROOF-038](../../TB-PROOF-038_manners_auto_demotion.md) proof sheet.

---

*Sheet TB-TEST-OCL-040 | TelsonBase v11.0.1 | March 8, 2026*
