# TB-TEST-SEC-076 - TestComplianceInfrastructure · `test_training_requirements_enforce_role_compliance`

**Sheet ID:** TB-TEST-SEC-076
**Series:** Individual Test Evidence
**Test File:** `tests/test_security_battery.py`
**Class:** `TestComplianceInfrastructure`
**Function:** `test_training_requirements_enforce_role_compliance`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Training requirements are enforced per role - non-compliant users are flagged

## Verdict

VERIFIED - This test passes as part of the 96-test Security Battery suite. Run the verification command below to confirm independently.

## Source

- `core/sanctions.py`
- `core/training.py`
- `core/baa.py`
- `core/breach.py`
- `core/hitrust.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_security_battery.py::TestComplianceInfrastructure::test_training_requirements_enforce_role_compliance -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 96 individual proof sheets for `tests/test_security_battery.py`.
Class-level summary: see the [TB-PROOF-049](../../TB-PROOF-049_security_compliance.md) proof sheet.

---

*Sheet TB-TEST-SEC-076 | TelsonBase v11.0.1 | March 8, 2026*
