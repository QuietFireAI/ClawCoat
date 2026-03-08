# TB-TEST-SEC-063 - TestNetworkSecurity · `test_external_domain_whitelist_restrictive`

**Sheet ID:** TB-TEST-SEC-063
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestNetworkSecurity`
**Function:** `test_external_domain_whitelist_restrictive`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> ALLOWED_EXTERNAL_DOMAINS is set and does not permit unrestricted external calls

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/config.py`
- `core/middleware.py`
- `core/session_management.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestNetworkSecurity::test_external_domain_whitelist_restrictive -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-047](../../TB-PROOF-047_security_network.md) proof sheet.

---

*Sheet TB-TEST-SEC-063 | TelsonBase v11.0.1 | March 8, 2026*
