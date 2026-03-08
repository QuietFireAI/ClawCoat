# TB-TEST-QMS-035 - TestBuildChain · `test_chain_with_explicit_correlation_id`

**Sheet ID:** TB-TEST-QMS-035
**Series:** Individual Test Evidence
**Test File:** `tests/test_qms.py`
**Class:** `TestBuildChain`
**Function:** `test_chain_with_explicit_correlation_id`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Chain with explicit correlation id

## Verdict

VERIFIED - This test passes as part of the 115-test QMS Protocol suite. Run the verification command below to confirm independently.

## Source

- `core/qms.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_qms.py::TestBuildChain::test_chain_with_explicit_correlation_id -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 115 individual proof sheets for `tests/test_qms.py`.
Class-level summary: see the [TB-PROOF-QMS](../../TB-PROOF-QMS.md) proof sheet.

---

*Sheet TB-TEST-QMS-035 | TelsonBase v11.0.1 | March 8, 2026*
