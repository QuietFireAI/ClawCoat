# TB-TEST-INT-004 - TestEgressGatewayBlocking · `test_blocked_domain_rejected`

**Sheet ID:** TB-TEST-INT-004
**Series:** Individual Test Evidence
**Test File:** `tests/test_integration.py`
**Class:** `TestEgressGatewayBlocking`
**Function:** `test_blocked_domain_rejected`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Blocked domain rejected

## Verdict

VERIFIED - This test passes as part of the 26-test Integration Layer suite. Run the verification command below to confirm independently.

## Source

- `core/capabilities.py`
- `core/middleware.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_integration.py::TestEgressGatewayBlocking::test_blocked_domain_rejected -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 26 individual proof sheets for `tests/test_integration.py`.
Class-level summary: see the [TB-PROOF-INT](../../TB-PROOF-INT.md) proof sheet.

---

*Sheet TB-TEST-INT-004 | TelsonBase v11.0.1 | March 8, 2026*
