# TB-TEST-OCL-025 - TestTrustLevels · `test_demotion_citizen_to_probation`

**Sheet ID:** TB-TEST-OCL-025
**Series:** Individual Test Evidence
**Test File:** `tests/test_openclaw.py`
**Class:** `TestTrustLevels`
**Function:** `test_demotion_citizen_to_probation`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Demotion citizen to probation

## Verdict

VERIFIED - This test passes as part of the 55-test OpenClaw Governance suite. Run the verification command below to confirm independently.

## Source

- `core/openclaw.py`
- `core/trust_levels.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_openclaw.py::TestTrustLevels::test_demotion_citizen_to_probation -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 55 individual proof sheets for `tests/test_openclaw.py`.
Class-level summary: see the [TB-PROOF-036](../../TB-PROOF-036_trust_level_matrix.md) proof sheet.

---

*Sheet TB-TEST-OCL-025 | TelsonBase v11.0.1 | March 8, 2026*
