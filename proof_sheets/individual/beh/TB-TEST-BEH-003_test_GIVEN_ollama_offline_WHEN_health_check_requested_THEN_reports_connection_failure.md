# TB-TEST-BEH-003 - TestBehavior_OllamaAgent_ModelManagement · `test_GIVEN_ollama_offline_WHEN_health_check_requested_THEN_reports_connection_failure`

**Sheet ID:** TB-TEST-BEH-003
**Series:** Individual Test Evidence
**Test File:** `tests/test_behavioral.py`
**Class:** `TestBehavior_OllamaAgent_ModelManagement`
**Function:** `test_GIVEN_ollama_offline_WHEN_health_check_requested_THEN_reports_connection_failure`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Given ollama offline: when health check requested, the system reports connection failure

## Verdict

VERIFIED - This test passes as part of the 30-test Behavioral Specification suite. Run the verification command below to confirm independently.

## Source

- `agents/ollama_agent.py`
- `core/ollama.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_behavioral.py::TestBehavior_OllamaAgent_ModelManagement::test_GIVEN_ollama_offline_WHEN_health_check_requested_THEN_reports_connection_failure -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 30 individual proof sheets for `tests/test_behavioral.py`.
Class-level summary: see the [TB-PROOF-BEH](../../TB-PROOF-BEH.md) proof sheet.

---

*Sheet TB-TEST-BEH-003 | TelsonBase v11.0.1 | March 8, 2026*
