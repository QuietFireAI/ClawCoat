# TB-TEST-OCL-030 - TestKillSwitch · `test_suspend_blocks_all_actions`

**Sheet ID:** TB-TEST-OCL-030
**Series:** Individual Test Evidence
**Test File:** `tests/test_openclaw.py`
**Class:** `TestKillSwitch`
**Function:** `test_suspend_blocks_all_actions`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Suspend blocks all actions

## Verdict

VERIFIED - This test passes as part of the 55-test OpenClaw Governance suite. Run the verification command below to confirm independently.

## Source

- `core/openclaw.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_openclaw.py::TestKillSwitch::test_suspend_blocks_all_actions -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 55 individual proof sheets for `tests/test_openclaw.py`.
Class-level summary: see the [TB-PROOF-037](../../TB-PROOF-037_openclaw_kill_switch.md) proof sheet.

---

*Sheet TB-TEST-OCL-030 | TelsonBase v11.0.1 | March 8, 2026*
