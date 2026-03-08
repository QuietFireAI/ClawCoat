# TB-TEST-OBS-032 - TestMonitoringConfigs · `test_grafana_datasource_provisioning_exists`

**Sheet ID:** TB-TEST-OBS-032
**Series:** Individual Test Evidence
**Test File:** `tests/test_observability.py`
**Class:** `TestMonitoringConfigs`
**Function:** `test_grafana_datasource_provisioning_exists`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Grafana datasource provisioning exists

## Verdict

VERIFIED - This test passes as part of the 40-test Observability & Monitoring suite. Run the verification command below to confirm independently.

## Source

- `monitoring/prometheus/prometheus.yml`
- `monitoring/grafana/`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_observability.py::TestMonitoringConfigs::test_grafana_datasource_provisioning_exists -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 40 individual proof sheets for `tests/test_observability.py`.
Class-level summary: see the [TB-PROOF-OBS](../../TB-PROOF-OBS.md) proof sheet.

---

*Sheet TB-TEST-OBS-032 | TelsonBase v11.0.1 | March 8, 2026*
