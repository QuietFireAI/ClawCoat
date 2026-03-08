# TB-TEST-OBS-037 - TestMonitoringConfigs · `test_grafana_dashboard_has_security_panels`

**Sheet ID:** TB-TEST-OBS-037
**Series:** Individual Test Evidence
**Test File:** `tests/test_observability.py`
**Class:** `TestMonitoringConfigs`
**Function:** `test_grafana_dashboard_has_security_panels`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Grafana dashboard has security panels

## Verdict

VERIFIED - This test passes as part of the 40-test Observability & Monitoring suite. Run the verification command below to confirm independently.

## Source

- `monitoring/prometheus/prometheus.yml`
- `monitoring/grafana/`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_observability.py::TestMonitoringConfigs::test_grafana_dashboard_has_security_panels -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 40 individual proof sheets for `tests/test_observability.py`.
Class-level summary: see the [TB-PROOF-OBS](../../TB-PROOF-OBS.md) proof sheet.

---

*Sheet TB-TEST-OBS-037 | TelsonBase v11.0.1 | March 8, 2026*
