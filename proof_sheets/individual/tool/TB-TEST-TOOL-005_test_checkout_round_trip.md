# TB-TEST-TOOL-005 - TestToolCheckout · `test_checkout_round_trip`

**Sheet ID:** TB-TEST-TOOL-005
**Series:** Individual Test Evidence
**Test File:** `tests/test_toolroom.py`
**Class:** `TestToolCheckout`
**Function:** `test_checkout_round_trip`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Checkout round trip

## Verdict

VERIFIED - This test passes as part of the 129-test Toolroom Supply-Chain Security suite. Run the verification command below to confirm independently.

## Source

- `toolroom/models.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_toolroom.py::TestToolCheckout::test_checkout_round_trip -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 129 individual proof sheets for `tests/test_toolroom.py`.
Class-level summary: see the [TB-PROOF-TOOL](../../TB-PROOF-TOOL.md) proof sheet.

---

*Sheet TB-TEST-TOOL-005 | TelsonBase v11.0.1 | March 8, 2026*
