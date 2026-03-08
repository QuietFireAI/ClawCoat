# TB-TEST-OLL-036 - TestOllamaAgentExecute · `test_chat_validates_messages_required`

**Sheet ID:** TB-TEST-OLL-036
**Series:** Individual Test Evidence
**Test File:** `tests/test_ollama.py`
**Class:** `TestOllamaAgentExecute`
**Function:** `test_chat_validates_messages_required`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Chat validates messages required

## Verdict

VERIFIED - This test passes as part of the 49-test Local LLM Inference suite. Run the verification command below to confirm independently.

## Source

- `agents/ollama_agent.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_ollama.py::TestOllamaAgentExecute::test_chat_validates_messages_required -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 49 individual proof sheets for `tests/test_ollama.py`.
Class-level summary: see the [TB-PROOF-029](../../TB-PROOF-029_local_llm_ollama.md) proof sheet.

---

*Sheet TB-TEST-OLL-036 | TelsonBase v11.0.1 | March 8, 2026*
