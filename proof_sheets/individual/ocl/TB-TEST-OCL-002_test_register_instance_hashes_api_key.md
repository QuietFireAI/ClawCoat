# TB-TEST-OCL-002 - TestRegistration · `test_register_instance_hashes_api_key`

**Sheet ID:** TB-TEST-OCL-002
**Series:** Individual Test Evidence
**Test File:** `tests/test_openclaw.py`
**Class:** `TestRegistration`
**Function:** `test_register_instance_hashes_api_key`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Register instance hashes api key

## Verdict

VERIFIED - This test passes as part of the 55-test OpenClaw Governance suite. Run the verification command below to confirm independently.

## Source

- `core/openclaw.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_openclaw.py::TestRegistration::test_register_instance_hashes_api_key -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 55 individual proof sheets for `tests/test_openclaw.py`.
Class-level summary: see the [TB-PROOF-041](../../TB-PROOF-041_agent_registration.md) proof sheet.

---

*Sheet TB-TEST-OCL-002 | TelsonBase v11.0.1 | March 8, 2026*
