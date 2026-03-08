# TB-TEST-QMS-058 - TestFindChains · `test_find_chains_ignores_surrounding_text`

**Sheet ID:** TB-TEST-QMS-058
**Series:** Individual Test Evidence
**Test File:** `tests/test_qms.py`
**Class:** `TestFindChains`
**Function:** `test_find_chains_ignores_surrounding_text`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Find chains ignores surrounding text

## Verdict

VERIFIED - This test passes as part of the 115-test QMS Protocol suite. Run the verification command below to confirm independently.

## Source

- `core/qms.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_qms.py::TestFindChains::test_find_chains_ignores_surrounding_text -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 115 individual proof sheets for `tests/test_qms.py`.
Class-level summary: see the [TB-PROOF-QMS](../../TB-PROOF-QMS.md) proof sheet.

---

*Sheet TB-TEST-QMS-058 | TelsonBase v11.0.1 | March 8, 2026*
