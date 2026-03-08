# TB-TEST-QMS-114 - TestSpecExamples · `test_spec_example_graceful_failure`

**Sheet ID:** TB-TEST-QMS-114
**Series:** Individual Test Evidence
**Test File:** `tests/test_qms.py`
**Class:** `TestSpecExamples`
**Function:** `test_spec_example_graceful_failure`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Spec example graceful failure

## Verdict

VERIFIED - This test passes as part of the 115-test QMS Protocol suite. Run the verification command below to confirm independently.

## Source

- `core/qms.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_qms.py::TestSpecExamples::test_spec_example_graceful_failure -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 115 individual proof sheets for `tests/test_qms.py`.
Class-level summary: see the [TB-PROOF-QMS](../../TB-PROOF-QMS.md) proof sheet.

---

*Sheet TB-TEST-QMS-114 | TelsonBase v11.0.1 | March 8, 2026*
