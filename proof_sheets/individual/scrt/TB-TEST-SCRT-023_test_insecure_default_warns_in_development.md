# TB-TEST-SCRT-023 - TestSecretsProvider · `test_insecure_default_warns_in_development`

**Sheet ID:** TB-TEST-SCRT-023
**Series:** Individual Test Evidence
**Test File:** `tests/test_secrets.py`
**Class:** `TestSecretsProvider`
**Function:** `test_insecure_default_warns_in_development`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Insecure default warns in development

## Verdict

VERIFIED - This test passes as part of the 48-test Secrets Management suite. Run the verification command below to confirm independently.

## Source

- `core/secrets.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_secrets.py::TestSecretsProvider::test_insecure_default_warns_in_development -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 48 individual proof sheets for `tests/test_secrets.py`.
Class-level summary: see the [TB-PROOF-SCRT](../../TB-PROOF-SCRT.md) proof sheet.

---

*Sheet TB-TEST-SCRT-023 | TelsonBase v11.0.1 | March 8, 2026*
