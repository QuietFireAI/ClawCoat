# TB-TEST-INT-012 - TestAnomalyDetection · `test_capability_probe_detection`

**Sheet ID:** TB-TEST-INT-012
**Series:** Individual Test Evidence
**Test File:** `tests/test_integration.py`
**Class:** `TestAnomalyDetection`
**Function:** `test_capability_probe_detection`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Capability probe detection

## Verdict

VERIFIED - This test passes as part of the 26-test Integration Layer suite. Run the verification command below to confirm independently.

## Source

- `core/anomaly.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_integration.py::TestAnomalyDetection::test_capability_probe_detection -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 26 individual proof sheets for `tests/test_integration.py`.
Class-level summary: see the [TB-PROOF-020](../../TB-PROOF-020_anomaly_detection.md) proof sheet.

---

*Sheet TB-TEST-INT-012 | TelsonBase v11.0.1 | March 8, 2026*
