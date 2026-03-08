# TB-TEST-BEH-030 - TestBehavior_DataSovereignty · `test_GIVEN_agent_capabilities_THEN_no_agent_declares_external_wildcard`

**Sheet ID:** TB-TEST-BEH-030
**Series:** Individual Test Evidence
**Test File:** `tests/test_behavioral.py`
**Class:** `TestBehavior_DataSovereignty`
**Function:** `test_GIVEN_agent_capabilities_THEN_no_agent_declares_external_wildcard`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Given : when , the system 

## Verdict

VERIFIED - This test passes as part of the 30-test Behavioral Specification suite. Run the verification command below to confirm independently.

## Source

- `agents/ollama_agent.py`
- `core/capabilities.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_behavioral.py::TestBehavior_DataSovereignty::test_GIVEN_agent_capabilities_THEN_no_agent_declares_external_wildcard -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 30 individual proof sheets for `tests/test_behavioral.py`.
Class-level summary: see the [TB-PROOF-BEH](../../TB-PROOF-BEH.md) proof sheet.

---

*Sheet TB-TEST-BEH-030 | TelsonBase v11.0.1 | March 8, 2026*
