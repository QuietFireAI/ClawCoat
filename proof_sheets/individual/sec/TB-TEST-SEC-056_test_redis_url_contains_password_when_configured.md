# TB-TEST-SEC-056 - TestNetworkSecurity · `test_redis_url_contains_password_when_configured`

**Sheet ID:** TB-TEST-SEC-056
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestNetworkSecurity`
**Function:** `test_redis_url_contains_password_when_configured`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Redis connection URL includes authentication when a password is set

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/config.py`
- `core/middleware.py`
- `core/session_management.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestNetworkSecurity::test_redis_url_contains_password_when_configured -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-047](../../TB-PROOF-047_security_network.md) proof sheet.

---

*Sheet TB-TEST-SEC-056 | TelsonBase v11.0.1 | March 8, 2026*
