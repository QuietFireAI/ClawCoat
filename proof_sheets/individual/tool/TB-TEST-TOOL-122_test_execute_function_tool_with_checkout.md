# TB-TEST-TOOL-122 - TestForemanExecution · `test_execute_function_tool_with_checkout`

**Sheet ID:** TB-TEST-TOOL-122
**Series:** Individual Test Evidence
**Test File:** `tests/test_toolroom.py`
**Class:** `TestForemanExecution`
**Function:** `test_execute_function_tool_with_checkout`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Execute function tool with checkout

## Verdict

VERIFIED - This test passes as part of the 129-test Toolroom Supply-Chain Security suite. Run the verification command below to confirm independently.

## Source

- `toolroom/foreman.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_toolroom.py::TestForemanExecution::test_execute_function_tool_with_checkout -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 129 individual proof sheets for `tests/test_toolroom.py`.
Class-level summary: see the [TB-PROOF-TOOL](../../TB-PROOF-TOOL.md) proof sheet.

---

*Sheet TB-TEST-TOOL-122 | TelsonBase v11.0.1 | March 8, 2026*
