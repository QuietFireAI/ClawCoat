# TB-TEST-INT-013 - TestKeyRevocation · `test_revoked_agent_cannot_reregister`

**Sheet ID:** TB-TEST-INT-013
**Series:** Individual Test Evidence
**Test File:** `tests/test_integration.py`
**Class:** `TestKeyRevocation`
**Function:** `test_revoked_agent_cannot_reregister`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Revoked agent cannot reregister

## Verdict

VERIFIED - This test passes as part of the 26-test Integration Layer suite. Run the verification command below to confirm independently.

## Source

- `core/signing.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_integration.py::TestKeyRevocation::test_revoked_agent_cannot_reregister -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 26 individual proof sheets for `tests/test_integration.py`.
Class-level summary: see the [TB-PROOF-013](../../TB-PROOF-013_message_signing.md) proof sheet.

---

*Sheet TB-TEST-INT-013 | TelsonBase v11.0.1 | March 8, 2026*
