# TB-TEST-SCRT-034 - TestProductionStartupGuard · `test_multiple_errors_all_reported`

**Sheet ID:** TB-TEST-SCRT-034
**Series:** Individual Test Evidence
**Test File:** `tests/test_secrets.py`
**Class:** `TestProductionStartupGuard`
**Function:** `test_multiple_errors_all_reported`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Multiple errors all reported

## Verdict

VERIFIED - This test passes as part of the 48-test Secrets Management suite. Run the verification command below to confirm independently.

## Source

- `core/secrets.py`
- `core/config.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_secrets.py::TestProductionStartupGuard::test_multiple_errors_all_reported -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 48 individual proof sheets for `tests/test_secrets.py`.
Class-level summary: see the [TB-PROOF-SCRT](../../TB-PROOF-SCRT.md) proof sheet.

---

*Sheet TB-TEST-SCRT-034 | TelsonBase v11.0.1 | March 8, 2026*
