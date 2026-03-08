# TB-TEST-OBS-026 - TestMQTTBus · `test_on_disconnect_callback`

**Sheet ID:** TB-TEST-OBS-026
**Series:** Individual Test Evidence
**Test File:** `tests/test_observability.py`
**Class:** `TestMQTTBus`
**Function:** `test_on_disconnect_callback`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> On disconnect callback

## Verdict

VERIFIED - This test passes as part of the 40-test Observability & Monitoring suite. Run the verification command below to confirm independently.

## Source

- `core/mqtt.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_observability.py::TestMQTTBus::test_on_disconnect_callback -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 40 individual proof sheets for `tests/test_observability.py`.
Class-level summary: see the [TB-PROOF-OBS](../../TB-PROOF-OBS.md) proof sheet.

---

*Sheet TB-TEST-OBS-026 | TelsonBase v11.0.1 | March 8, 2026*
