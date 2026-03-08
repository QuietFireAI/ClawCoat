# TB-TEST-TOOL-011 - TestToolRegistry · `test_checkout_nonexistent_tool_returns_none`

**Sheet ID:** TB-TEST-TOOL-011
**Series:** Individual Test Evidence
**Test File:** `tests/test_toolroom.py`
**Class:** `TestToolRegistry`
**Function:** `test_checkout_nonexistent_tool_returns_none`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Checkout nonexistent tool returns none

## Verdict

VERIFIED - This test passes as part of the 129-test Toolroom Supply-Chain Security suite. Run the verification command below to confirm independently.

## Source

- `toolroom/registry.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_toolroom.py::TestToolRegistry::test_checkout_nonexistent_tool_returns_none -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 129 individual proof sheets for `tests/test_toolroom.py`.
Class-level summary: see the [TB-PROOF-TOOL](../../TB-PROOF-TOOL.md) proof sheet.

---

*Sheet TB-TEST-TOOL-011 | TelsonBase v11.0.1 | March 8, 2026*
