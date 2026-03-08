# TB-TEST-TOOL-081 - TestManifestValidation · `test_dangerous_entry_point_dollar_paren`

**Sheet ID:** TB-TEST-TOOL-081
**Series:** Individual Test Evidence
**Test File:** `tests/test_toolroom.py`
**Class:** `TestManifestValidation`
**Function:** `test_dangerous_entry_point_dollar_paren`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Dangerous entry point dollar paren

## Verdict

VERIFIED - This test passes as part of the 129-test Toolroom Supply-Chain Security suite. Run the verification command below to confirm independently.

## Source

- `toolroom/manifest.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_toolroom.py::TestManifestValidation::test_dangerous_entry_point_dollar_paren -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 129 individual proof sheets for `tests/test_toolroom.py`.
Class-level summary: see the [TB-PROOF-TOOL](../../TB-PROOF-TOOL.md) proof sheet.

---

*Sheet TB-TEST-TOOL-081 | TelsonBase v11.0.1 | March 8, 2026*
