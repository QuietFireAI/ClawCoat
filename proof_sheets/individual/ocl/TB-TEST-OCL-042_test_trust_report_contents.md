# TB-TEST-OCL-042 - TestTrustReport · `test_trust_report_contents`

**Sheet ID:** TB-TEST-OCL-042
**Series:** Individual Test Evidence
**Test File:** `tests/test_openclaw.py`
**Class:** `TestTrustReport`
**Function:** `test_trust_report_contents`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Trust report contents

## Verdict

VERIFIED - This test passes as part of the 55-test OpenClaw Governance suite. Run the verification command below to confirm independently.

## Source

- `core/openclaw.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_openclaw.py::TestTrustReport::test_trust_report_contents -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 55 individual proof sheets for `tests/test_openclaw.py`.
Class-level summary: see the [TB-PROOF-035](../../TB-PROOF-035_openclaw_governance.md) proof sheet.

---

*Sheet TB-TEST-OCL-042 | TelsonBase v11.0.1 | March 8, 2026*
