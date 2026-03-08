# TB-TEST-TOOL-073 - TestToolManifest · `test_manifest_from_dict_ignores_unknown_fields`

**Sheet ID:** TB-TEST-TOOL-073
**Series:** Individual Test Evidence
**Test File:** `tests/test_toolroom.py`
**Class:** `TestToolManifest`
**Function:** `test_manifest_from_dict_ignores_unknown_fields`
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Claim

> Manifest from dict ignores unknown fields

## Verdict

VERIFIED - This test passes as part of the 129-test Toolroom Supply-Chain Security suite. Run the verification command below to confirm independently.

## Source

- `toolroom/manifest.py`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_toolroom.py::TestToolManifest::test_manifest_from_dict_ignores_unknown_fields -v --tb=short
```

## Expected Result

```
1 passed
```

## Suite Context

This sheet is one of 129 individual proof sheets for `tests/test_toolroom.py`.
Class-level summary: see the [TB-PROOF-TOOL](../../TB-PROOF-TOOL.md) proof sheet.

---

*Sheet TB-TEST-TOOL-073 | TelsonBase v11.0.1 | March 8, 2026*
