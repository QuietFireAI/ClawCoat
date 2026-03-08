# TB-TEST-INT-020 - TestAuditChain · `test_audit_export_for_compliance`

**Sheet ID:** TB-TEST-INT-020
**Series:** Individual Test Evidence
**Test File:** `tests/test_integration.py`
**Class:** `TestAuditChain`
**Function:** `test_audit_export_for_compliance`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Audit export for compliance

## Verdict

VERIFIED - This test passes as part of the 26-test Integration Layer suite. Run the verification command below to confirm independently.

## Source

- `core/audit.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_integration.py::TestAuditChain::test_audit_export_for_compliance -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 26 individual proof sheets for `tests/test_integration.py`.
Class-level summary: see the [TB-PROOF-009](../../TB-PROOF-009_audit_chain_sha256.md) proof sheet.

---

*Sheet TB-TEST-INT-020 | TelsonBase v11.0.1 | March 8, 2026*
