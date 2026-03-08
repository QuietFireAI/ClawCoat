# TB-TEST-CAP-012 - TestCapabilitySet · `test_default_deny`

**Sheet ID:** TB-TEST-CAP-012
**Series:** Individual Test Evidence
**Test File:** `tests/test_capabilities.py`
**Class:** `TestCapabilitySet`
**Function:** `test_default_deny`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Default deny

## Verdict

VERIFIED - This test passes as part of the 15-test Capability Enforcement suite. Run the verification command below to confirm independently.

## Source

- `core/capabilities.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_capabilities.py::TestCapabilitySet::test_default_deny -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 15 individual proof sheets for `tests/test_capabilities.py`.
Class-level summary: see the [TB-PROOF-CAP](../../TB-PROOF-CAP.md) proof sheet.

---

*Sheet TB-TEST-CAP-012 | TelsonBase v11.0.1 | March 8, 2026*
