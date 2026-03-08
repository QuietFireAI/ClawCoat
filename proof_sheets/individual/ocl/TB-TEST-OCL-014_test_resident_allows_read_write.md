# TB-TEST-OCL-014 - TestGovernancePipeline · `test_resident_allows_read_write`

**Sheet ID:** TB-TEST-OCL-014
**Series:** Individual Test Evidence
**Test File:** `tests/test_openclaw.py`
**Class:** `TestGovernancePipeline`
**Function:** `test_resident_allows_read_write`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Resident allows read write

## Verdict

VERIFIED - This test passes as part of the 55-test OpenClaw Governance suite. Run the verification command below to confirm independently.

## Source

- `core/openclaw.py`
- `core/capabilities.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_openclaw.py::TestGovernancePipeline::test_resident_allows_read_write -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 55 individual proof sheets for `tests/test_openclaw.py`.
Class-level summary: see the [TB-PROOF-035](../../TB-PROOF-035_openclaw_governance.md) proof sheet.

---

*Sheet TB-TEST-OCL-014 | TelsonBase v11.0.1 | March 8, 2026*
