# TB-TEST-OCL-054 - TestQueryMethods · `test_get_instance_by_id`

**Sheet ID:** TB-TEST-OCL-054
**Series:** Individual Test Evidence
**Test File:** `tests/test_openclaw.py`
**Class:** `TestQueryMethods`
**Function:** `test_get_instance_by_id`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Get instance by id

## Verdict

VERIFIED - This test passes as part of the 55-test OpenClaw Governance suite. Run the verification command below to confirm independently.

## Source

- `core/openclaw.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_openclaw.py::TestQueryMethods::test_get_instance_by_id -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 55 individual proof sheets for `tests/test_openclaw.py`.
Class-level summary: see the [TB-PROOF-035](../../TB-PROOF-035_openclaw_governance.md) proof sheet.

---

*Sheet TB-TEST-OCL-054 | TelsonBase v11.0.1 | March 8, 2026*
