# TB-TEST-SEC-095 - TestRuntimeBoundaries · `test_captcha_expired_challenge_rejected`

**Sheet ID:** TB-TEST-SEC-095
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestRuntimeBoundaries`
**Function:** `test_captcha_expired_challenge_rejected`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> An expired CAPTCHA challenge is rejected even with the correct answer - time enforcement is real

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/middleware.py`
- `core/captcha.py`
- `core/email_verification.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestRuntimeBoundaries::test_captcha_expired_challenge_rejected -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-051](../../TB-PROOF-051_security_runtime_boundaries.md) proof sheet.

---

*Sheet TB-TEST-SEC-095 | TelsonBase v11.0.1 | March 8, 2026*
