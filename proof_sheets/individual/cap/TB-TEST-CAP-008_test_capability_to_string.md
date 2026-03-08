# TB-TEST-CAP-008 - TestCapability · `test_capability_to_string`

**Sheet ID:** TB-TEST-CAP-008
**Series:** Individual Test Evidence
**Test File:** `tests/test_capabilities.py`
**Class:** `TestCapability`
**Function:** `test_capability_to_string`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Capability to string

## Verdict

VERIFIED - This test passes as part of the 15-test Capability Enforcement suite. Run the verification command below to confirm independently.

## Source

- `core/capabilities.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_capabilities.py::TestCapability::test_capability_to_string -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 15 individual proof sheets for `tests/test_capabilities.py`.
Class-level summary: see the [TB-PROOF-CAP](../../TB-PROOF-CAP.md) proof sheet.

---

*Sheet TB-TEST-CAP-008 | TelsonBase v11.0.1 | March 8, 2026*
