# TB-TEST-OBS-029 - TestMQTTBusSingleton · `test_get_mqtt_bus_returns_same_instance`

**Sheet ID:** TB-TEST-OBS-029
**Series:** Individual Test Evidence
**Test File:** `tests/test_observability.py`
**Class:** `TestMQTTBusSingleton`
**Function:** `test_get_mqtt_bus_returns_same_instance`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Get mqtt bus returns same instance

## Verdict

VERIFIED - This test passes as part of the 40-test Observability & Monitoring suite. Run the verification command below to confirm independently.

## Source

- `core/mqtt.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_observability.py::TestMQTTBusSingleton::test_get_mqtt_bus_returns_same_instance -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 40 individual proof sheets for `tests/test_observability.py`.
Class-level summary: see the [TB-PROOF-OBS](../../TB-PROOF-OBS.md) proof sheet.

---

*Sheet TB-TEST-OBS-029 | TelsonBase v11.0.1 | March 8, 2026*
