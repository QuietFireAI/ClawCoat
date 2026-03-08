# TB-TEST-IDN-023 - TestKillSwitch · `test_revoke_agent`

**Sheet ID:** TB-TEST-IDN-023
**Series:** Individual Test Evidence
**Test File:** `tests/test_identiclaw.py`
**Class:** `TestKillSwitch`
**Function:** `test_revoke_agent`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Revoke agent

## Verdict

VERIFIED - This test passes as part of the 50-test W3C DID Agent Identity suite. Run the verification command below to confirm independently.

## Source

- `core/openclaw.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_identiclaw.py::TestKillSwitch::test_revoke_agent -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 50 individual proof sheets for `tests/test_identiclaw.py`.
Class-level summary: see the [TB-PROOF-IDN](../../TB-PROOF-IDN.md) proof sheet.

---

*Sheet TB-TEST-IDN-023 | TelsonBase v11.0.1 | March 8, 2026*
