# TB-TEST-OCL-027 - TestTrustLevels · `test_cannot_demote_below_quarantine`

**Sheet ID:** TB-TEST-OCL-027
**Series:** Individual Test Evidence
**Test File:** `tests/test_openclaw.py`
**Class:** `TestTrustLevels`
**Function:** `test_cannot_demote_below_quarantine`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Cannot demote below quarantine

## Verdict

VERIFIED - This test passes as part of the 55-test OpenClaw Governance suite. Run the verification command below to confirm independently.

## Source

- `core/openclaw.py`
- `core/trust_levels.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_openclaw.py::TestTrustLevels::test_cannot_demote_below_quarantine -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 55 individual proof sheets for `tests/test_openclaw.py`.
Class-level summary: see the [TB-PROOF-036](../../TB-PROOF-036_trust_level_matrix.md) proof sheet.

---

*Sheet TB-TEST-OCL-027 | TelsonBase v11.0.1 | March 8, 2026*
