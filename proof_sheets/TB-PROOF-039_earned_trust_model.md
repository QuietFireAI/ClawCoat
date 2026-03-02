# TB-PROOF-039: Earned Trust Model

**Sheet ID:** TB-PROOF-039
**Claim Source:** telsonbase.com — Control Your Claw
**Status:** VERIFIED
**Last Verified:** February 23, 2026
**Version:** 7.4.0CC

---

## Exact Claim

> "Trust is earned, not granted. Every autonomous agent starts at Quarantine with zero autonomous permissions. Promotion is sequential and earned. Demotion is instant and can skip levels."

## Verdict

VERIFIED — `OpenClawManager.register_instance()` starts every claw at QUARANTINE (configurable via `OPENCLAW_DEFAULT_TRUST`, defaults to "quarantine"). `promote_trust()` enforces sequential promotion only via `VALID_PROMOTIONS` dictionary. `demote_trust()` allows skip-level demotion via `VALID_DEMOTIONS` dictionary. An agent cannot promote itself — promotion requires admin authentication.

## Evidence

### Source Files
| File | Lines | What It Proves |
|---|---|---|
| `core/openclaw.py` | `register_instance()` | Default trust level = QUARANTINE |
| `core/openclaw.py` | `VALID_PROMOTIONS` | Sequential-only: Q→P, P→R, R→C |
| `core/openclaw.py` | `VALID_DEMOTIONS` | Skip-capable: C→{R,P,Q}, R→{P,Q}, P→{Q} |
| `core/openclaw.py` | `promote_trust()` | Validates against VALID_PROMOTIONS |
| `core/openclaw.py` | `demote_trust()` | Validates against VALID_DEMOTIONS |
| `core/openclaw.py` | `TRUST_PERMISSION_MATRIX` | Per-level autonomous/gated/blocked actions |
| `api/openclaw_routes.py` | `POST /{id}/promote` | Admin-only endpoint for promotion |
| `api/openclaw_routes.py` | `POST /{id}/demote` | Admin-only endpoint for demotion |
| `tests/test_openclaw.py` | `TestTrustLevels` | 6+ tests covering promotion/demotion rules |

### Valid Trust Transitions
```
VALID_PROMOTIONS (sequential only):
  QUARANTINE → PROBATION
  PROBATION  → RESIDENT
  RESIDENT   → CITIZEN
  CITIZEN    → AGENT

VALID_DEMOTIONS (skip-capable):
  CITIZEN    → RESIDENT, PROBATION, QUARANTINE
  RESIDENT   → PROBATION, QUARANTINE
  PROBATION  → QUARANTINE
```

### Trust Level Permission Matrix
| Trust Level | Autonomous | Gated (Approval Required) | Blocked |
|---|---|---|---|
| **QUARANTINE** | None | ALL actions | Destructive, external |
| **PROBATION** | Read-only, internal | External calls, writes | Destructive |
| **RESIDENT** | Read/write, internal | Financial, delete, new domains | None (gated) |
| **CITIZEN** | All allowed tools | Anomaly-flagged only | None |
| **AGENT** | Full autonomy (300 actions/min), all tools | None | None |

### Why This Is the "Secret Sauce"
1. **Default-deny**: No agent has autonomous permissions by default
2. **Earn-up**: Trust must be explicitly granted by a human administrator
3. **Instant-down**: Bad behavior triggers immediate demotion (no intermediate steps)
4. **Self-promotion impossible**: The agent cannot call its own promote endpoint
5. **Manners-enforced**: Behavioral compliance is continuously scored, not just checked at promotion time

### Test Coverage
- `test_registration_default_quarantine` — New instances start at QUARANTINE
- `test_promotion_sequential_only` — Cannot skip from QUARANTINE to RESIDENT
- `test_demotion_skip_levels` — Can skip from CITIZEN to QUARANTINE
- `test_invalid_promotion_rejected` — Invalid promotion transitions are rejected
- `test_invalid_demotion_rejected` — Cannot "demote" upward
- `test_promotion_requires_valid_transition` — Each step validated against VALID_PROMOTIONS

## Verification Command

```bash
grep -n "VALID_PROMOTIONS\|VALID_DEMOTIONS\|default_trust\|register_instance" core/openclaw.py | head -10
```

## Expected Result

References to VALID_PROMOTIONS dictionary (sequential), VALID_DEMOTIONS dictionary (skip-capable), and register_instance defaulting to quarantine.

---

*Sheet TB-PROOF-039 | TelsonBase v7.4.0CC | February 23, 2026*
