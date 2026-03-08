# TB-TEST-QMS-014 - TestBlockDetection · `test_detect_command_thank_you_but_no`

**Sheet ID:** TB-TEST-QMS-014
**Series:** Individual Test Evidence
**Test File:** `tests/test_qms.py`
**Class:** `TestBlockDetection`
**Function:** `test_detect_command_thank_you_but_no`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Detect command thank you but no

## Verdict

VERIFIED - This test passes as part of the 115-test QMS Protocol suite. Run the verification command below to confirm independently.

## Source

- `core/qms.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_qms.py::TestBlockDetection::test_detect_command_thank_you_but_no -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 115 individual proof sheets for `tests/test_qms.py`.
Class-level summary: see the [TB-PROOF-QMS](../../TB-PROOF-QMS.md) proof sheet.

---

*Sheet TB-TEST-QMS-014 | TelsonBase v11.0.1 | March 8, 2026*
