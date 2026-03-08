# TB-TEST-OCL-048 - TestPermissionMatrix · `test_citizen_has_all_autonomous`

**Sheet ID:** TB-TEST-OCL-048
**Series:** Individual Test Evidence
**Test File:** `tests/test_openclaw.py`
**Class:** `TestPermissionMatrix`
**Function:** `test_citizen_has_all_autonomous`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Citizen has all autonomous

## Verdict

VERIFIED - This test passes as part of the 55-test OpenClaw Governance suite. Run the verification command below to confirm independently.

## Source

- `core/trust_levels.py`
- `core/capabilities.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_openclaw.py::TestPermissionMatrix::test_citizen_has_all_autonomous -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 55 individual proof sheets for `tests/test_openclaw.py`.
Class-level summary: see the [TB-PROOF-036](../../TB-PROOF-036_trust_level_matrix.md) proof sheet.

---

*Sheet TB-TEST-OCL-048 | TelsonBase v11.0.1 | March 8, 2026*
