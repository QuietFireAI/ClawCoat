# TB-TEST-QMS-102 - TestLegacyCompatibility · `test_is_qms_formatted_rejects_plain`

**Sheet ID:** TB-TEST-QMS-102
**Series:** Individual Test Evidence
**Test File:** `tests/test_qms.py`
**Class:** `TestLegacyCompatibility`
**Function:** `test_is_qms_formatted_rejects_plain`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Is qms formatted rejects plain

## Verdict

VERIFIED - This test passes as part of the 115-test QMS Protocol suite. Run the verification command below to confirm independently.

## Source

- `core/qms.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_qms.py::TestLegacyCompatibility::test_is_qms_formatted_rejects_plain -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 115 individual proof sheets for `tests/test_qms.py`.
Class-level summary: see the [TB-PROOF-QMS](../../TB-PROOF-QMS.md) proof sheet.

---

*Sheet TB-TEST-QMS-102 | TelsonBase v11.0.1 | March 8, 2026*
