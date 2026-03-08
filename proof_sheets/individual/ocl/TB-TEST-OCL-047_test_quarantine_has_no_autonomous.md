# TB-TEST-OCL-047 - TestPermissionMatrix · `test_quarantine_has_no_autonomous`

**Sheet ID:** TB-TEST-OCL-047
**Series:** Individual Test Evidence
**Test File:** `tests/test_openclaw.py`
**Class:** `TestPermissionMatrix`
**Function:** `test_quarantine_has_no_autonomous`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Quarantine has no autonomous

## Verdict

VERIFIED - This test passes as part of the 55-test OpenClaw Governance suite. Run the verification command below to confirm independently.

## Source

- `core/trust_levels.py`
- `core/capabilities.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_openclaw.py::TestPermissionMatrix::test_quarantine_has_no_autonomous -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 55 individual proof sheets for `tests/test_openclaw.py`.
Class-level summary: see the [TB-PROOF-036](../../TB-PROOF-036_trust_level_matrix.md) proof sheet.

---

*Sheet TB-TEST-OCL-047 | TelsonBase v11.0.1 | March 8, 2026*
