# TB-TEST-SEC-051 - TestAuditTrailIntegrity · `test_chain_hash_is_sha256`

**Sheet ID:** TB-TEST-SEC-051
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestAuditTrailIntegrity`
**Function:** `test_chain_hash_is_sha256`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> The audit chain hash algorithm is SHA-256 - not MD5, not SHA-1

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/audit.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestAuditTrailIntegrity::test_chain_hash_is_sha256 -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-046](../../TB-PROOF-046_security_audit_trail.md) proof sheet.

---

*Sheet TB-TEST-SEC-051 | TelsonBase v11.0.1 | March 8, 2026*
