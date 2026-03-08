# TB-TEST-BEH-014 - TestBehavior_QMS_ProtocolDiscipline · `test_GIVEN_chain_with_halt_postscript_WHEN_validated_THEN_is_parseable`

**Sheet ID:** TB-TEST-BEH-014
**Series:** Individual Test Evidence
**Test File:** `tests/test_behavioral.py`
**Class:** `TestBehavior_QMS_ProtocolDiscipline`
**Function:** `test_GIVEN_chain_with_halt_postscript_WHEN_validated_THEN_is_parseable`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Given chain with halt postscript: when validated, the system is parseable

## Verdict

VERIFIED - This test passes as part of the 30-test Behavioral Specification suite. Run the verification command below to confirm independently.

## Source

- `core/qms.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_behavioral.py::TestBehavior_QMS_ProtocolDiscipline::test_GIVEN_chain_with_halt_postscript_WHEN_validated_THEN_is_parseable -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 30 individual proof sheets for `tests/test_behavioral.py`.
Class-level summary: see the [TB-PROOF-BEH](../../TB-PROOF-BEH.md) proof sheet.

---

*Sheet TB-TEST-BEH-014 | TelsonBase v11.0.1 | March 8, 2026*
