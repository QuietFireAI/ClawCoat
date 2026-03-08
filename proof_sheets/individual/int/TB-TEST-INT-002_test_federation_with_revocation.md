# TB-TEST-INT-002 - TestFederationHandshake · `test_federation_with_revocation`

**Sheet ID:** TB-TEST-INT-002
**Series:** Individual Test Evidence
**Test File:** `tests/test_integration.py`
**Class:** `TestFederationHandshake`
**Function:** `test_federation_with_revocation`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Federation with revocation

## Verdict

VERIFIED - This test passes as part of the 26-test Integration Layer suite. Run the verification command below to confirm independently.

## Source

- `core/federation.py`
- `core/signing.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_integration.py::TestFederationHandshake::test_federation_with_revocation -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 26 individual proof sheets for `tests/test_integration.py`.
Class-level summary: see the [TB-PROOF-INT](../../TB-PROOF-INT.md) proof sheet.

---

*Sheet TB-TEST-INT-002 | TelsonBase v11.0.1 | March 8, 2026*
