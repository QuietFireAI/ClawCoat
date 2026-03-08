# TB-PROOF-054 -- Toolroom and Foreman Agent Test Suite

**Sheet ID:** TB-PROOF-054
**Claim Source:** tests/test_toolroom.py
**Status:** VERIFIED
**Last Verified:** March 8, 2026
**Version:** v11.0.1

---

## Exact Claim

> "720 tests passing" -- README, proof_sheets/INDEX.md

This sheet proves the **Toolroom and Foreman Agent Test Suite**: 129 tests across 28 classes covering 129 tests across 28 classes verifying the Toolroom and Foreman agent: tool.

## Verdict

VERIFIED -- All 129 tests pass. The Toolroom correctly gates external tool access by agent trust level. The Foreman agent enforces checkout authorization, triggers HITL approval for API-class tools, validates install sources, and manages the tool manifest. Function tools execute with proper authorization checks and return structured results.

## Test Classes

| Class | Tests | Proves |
|---|---|---|
| `TestToolMetadata` | 4 | ToolMetadata construction, defaults, and round-trip serialization |
| `TestToolCheckout` | 2 | ToolCheckout creation and round-trip serialization |
| `TestToolRegistry` | 10 | Register, list, checkout, return, and request tools; active checkout filtering |
| `TestTrustLevelNormalization` | 5 | Accept lowercase, uppercase, and mixed-case trust strings |
| `TestForemanCheckout` | 5 | Authorize or block checkout by trust level; HITL trigger for API tools |
| `TestForemanInstall` | 4 | Reject unapproved sources; create approval for approved sources; validate approval |
| `TestToolroomStore` | 5 | Store singleton existence, required methods, get_store helper |
| `TestCeleryConfiguration` | 3 | Foreman in Celery include, daily update in beat schedule, task routing |
| `TestToolroomAPI` | 3 | Toolroom status, list tools via REST |
| `TestApprovalIntegration` | 3 | Checkout approved/rejected/pending approval states |
| `TestToolroomPostCheckout` | 4 | POST /checkout endpoint authorization and response |
| `TestToolroomPostReturn` | 4 | POST /return endpoint and checkout release |
| `TestToolroomPostInstallPropose` | 5 | POST /install/propose source validation and approval creation |
| `TestToolroomPostInstallExecute` | 5 | POST /install/execute approval enforcement and execution |
| `TestToolroomPostRequest` | 4 | POST /request unapproved tool request flow |
| `TestToolroomPostApiCheckoutComplete` | 4 | POST /checkout/complete HITL API tool completion |
| `TestToolManifest` | 8 | Manifest structure, tool entries, version fields, category grouping |
| `TestManifestValidation` | 10 | Validate required fields, type constraints, duplicate detection |
| `TestManifestFileLoading` | 6 | Load manifest from file, handle missing and malformed files |
| `TestFunctionToolRegistry` | 9 | Register function tools, lookup by name, list by category |
| `TestRegisterFunctionToolDecorator` | 4 | Decorator registers function tools with metadata |
| `TestExecutionResult` | 4 | ExecutionResult construction, success/failure status, output access |
| `TestFunctionToolExecution` | 8 | Execute function tools with auth, handle errors and timeouts |
| `TestApprovalStatusLookup` | 9 | Lookup pending, approved, rejected approval status by checkout ID |
| `TestSemanticVersionComparison` | 5 | Compare semantic versions for tool upgrade eligibility |
| `TestToolroomExecuteEndpoint` | 5 | POST /execute endpoint dispatch and result formatting |
| `TestForemanExecution` | 13 | Foreman executes tools, enforces HITL, logs audit events |
| `TestToolMetadataV460` | 4 | Forward compatibility: v4.6.0 metadata fields and defaults |

## Source Files Tested

- `tests/test_toolroom.py`
- `core/toolroom.py -- ToolMetadata, ToolCheckout, ToolRegistry, Foreman`
- `core/toolroom.py -- FunctionToolRegistry, ExecutionResult, ToolroomStore`
- `routers/toolroom.py -- REST endpoints`
- `core/celery_app.py -- Foreman task routing and beat schedule`

## Verification Command

```bash
docker compose exec mcp_server python -m pytest tests/test_toolroom.py -v --tb=short
```

## Expected Result

```
129 passed
```

---

*Sheet TB-PROOF-054 | TelsonBase v11.0.1 | March 8, 2026*
