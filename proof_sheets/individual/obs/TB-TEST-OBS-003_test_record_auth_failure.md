# TB-TEST-OBS-003 - TestPrometheusMetrics · `test_record_auth_failure`

**Sheet ID:** TB-TEST-OBS-003
**Series:** Individual Test Evidence
**Test File:** `tests/test_observability.py`
**Class:** `TestPrometheusMetrics`
**Function:** `test_record_auth_failure`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Record auth failure

## Verdict

VERIFIED - This test passes as part of the 40-test Observability & Monitoring suite. Run the verification command below to confirm independently.

## Source

- `core/metrics.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_observability.py::TestPrometheusMetrics::test_record_auth_failure -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 40 individual proof sheets for `tests/test_observability.py`.
Class-level summary: see the [TB-PROOF-OBS](../../TB-PROOF-OBS.md) proof sheet.

---

*Sheet TB-TEST-OBS-003 | TelsonBase v11.0.1 | March 8, 2026*
