# TB-TEST-INT-001 - TestFederationHandshake · `test_full_federation_handshake`

**Sheet ID:** TB-TEST-INT-001
**Series:** Individual Test Evidence
**Test File:** `tests/test_integration.py`
**Class:** `TestFederationHandshake`
**Function:** `test_full_federation_handshake`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Full federation handshake

## Verdict

VERIFIED - This test passes as part of the 26-test Integration Layer suite. Run the verification command below to confirm independently.

## Source

- `core/federation.py`
- `core/signing.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_integration.py::TestFederationHandshake::test_full_federation_handshake -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 26 individual proof sheets for `tests/test_integration.py`.
Class-level summary: see the [TB-PROOF-INT](../../TB-PROOF-INT.md) proof sheet.

---

*Sheet TB-TEST-INT-001 | TelsonBase v11.0.1 | March 8, 2026*
