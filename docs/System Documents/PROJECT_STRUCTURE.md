# ClawCoat Project Structure

**Version:** v11.0.2 | **Updated:** March 19, 2026

```
telsonbase/
├── main.py                     # FastAPI application entry point
├── version.py                  # Single source of truth for version string
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container build instructions
├── docker-compose.yml          # Full stack orchestration
├── docker-compose.prod.yml     # Production overrides (no MailHog)
├── docker-compose.federation-test.yml  # Multi-instance federation test setup
├── alembic.ini                 # Database migration configuration
├── pytest.ini                  # Test configuration
├── goose.yaml                  # Goose MCP client config (copy to ~/.config/goose/)
├── .env.example                # Environment template (copy to .env)
│
├── core/                       # Security & governance engine (~60 modules)
│   │
│   ├── - Governance - 
│   ├── openclaw.py             # OpenClaw governance engine + OpenClawManager singleton
│   ├── trust_levels.py         # AgentTrustLevel enum (QUARANTINE → AGENT), permission matrix
│   ├── manners.py              # Manners compliance scoring engine
│   ├── identiclaw.py           # Agent identity (DID, Ed25519, verifiable credentials)
│   │
│   ├── - Auth & Access - 
│   ├── config.py               # Centralized settings (pydantic)
│   ├── auth.py                 # JWT authentication
│   ├── auth_dependencies.py    # FastAPI auth dependency helpers
│   ├── rbac.py                 # Role-based access control (5 roles, Redis-persisted)
│   ├── mfa.py                  # TOTP multi-factor authentication (RFC 6238)
│   ├── captcha.py              # CAPTCHA challenge/response
│   ├── sessions.py             # Session store
│   ├── session_management.py   # HIPAA-compliant idle timeout
│   ├── delegation.py           # Permission delegation
│   ├── emergency_access.py     # Break-glass emergency access
│   │
│   ├── - Security - 
│   ├── signing.py              # HMAC-SHA256 / Ed25519 message signing
│   ├── capabilities.py         # Capability enforcement (filesystem, external, MQTT)
│   ├── anomaly.py              # Behavioral anomaly detection
│   ├── approval.py             # Human-in-the-loop approval gates
│   ├── audit.py                # SHA-256 hash-chained audit trail
│   ├── middleware.py           # Rate limiting, circuit breaker
│   ├── rate_limiting.py        # Per-tenant rate limit enforcement
│   ├── tenant_rate_limiting.py # Tenant-scoped rate limits
│   ├── secrets.py              # Secrets management
│   ├── secure_storage.py       # AES-256-GCM encrypted storage
│   ├── rotation.py             # Key rotation
│   ├── threat_response.py      # Automated threat response
│   ├── system_analysis.py      # System health analysis
│   │
│   ├── - Compliance - 
│   ├── compliance.py           # Framework orchestration
│   ├── baa.py                  # BAA management (HIPAA)
│   ├── breach.py               # Breach detection
│   ├── breach_notification.py  # HITECH 60-day breach notification
│   ├── data_classification.py  # PHI / PII / sensitive data classification
│   ├── data_retention.py       # Retention policy enforcement
│   ├── hitrust.py              # HITRUST CSF controls
│   ├── legal_hold.py           # Legal hold enforcement
│   ├── minimum_necessary.py    # HIPAA minimum necessary rule
│   ├── phi.py                  # PHI access tracking
│   ├── phi_deidentification.py # 18 safe harbor identifier removal
│   ├── phi_disclosure.py       # PHI disclosure logging
│   ├── retention.py            # Retention lifecycle
│   ├── sanctions.py            # OFAC/sanctions screening
│   ├── training.py             # Compliance training tracking
│   ├── contingency.py          # HIPAA contingency planning
│   ├── contingency_testing.py  # Contingency plan test runner
│   │
│   ├── - Infrastructure - 
│   ├── database.py             # SQLAlchemy async engine + session factory
│   ├── models.py               # ORM models (shared across modules)
│   ├── persistence.py          # Redis state management
│   ├── tenancy.py              # Multi-tenant isolation
│   ├── email_sender.py         # SMTP email (Resend / MailHog)
│   ├── email_verification.py   # Email verification flow
│   ├── metrics.py              # Prometheus metrics
│   ├── mqtt_bus.py             # MQTT pub/sub integration
│   ├── ollama_service.py       # Local LLM inference client
│   ├── semantic_matching.py    # Semantic tool-to-category matching
│   ├── qms.py                  # QMS™ (Qualified Message Standard) logger
│   └── qms_schema.json         # QMS™ log schema
│
├── agents/                     # Agent implementations
│   ├── __init__.py             # Central agent registry + metadata
│   ├── registry.yaml           # Agent registry manifest
│   ├── base.py                 # SecureBaseAgent abstract class (514 lines)
│   ├── backup_agent.py         # Automated backup agent
│   ├── compliance_check_agent.py  # Compliance verification agent
│   ├── demo_agent.py           # Example/template agent
│   ├── doc_prep_agent.py       # Document preparation agent
│   ├── document_agent.py       # Document processing agent
│   ├── memory_agent.py         # Memory / knowledge management agent
│   ├── ollama_agent.py         # Local LLM interaction agent
│   ├── transaction_agent.py    # Transaction coordination agent
│   └── alien_adapter.py        # Quarantine adapter for external frameworks
│
├── api/                        # Route handlers
│   ├── __init__.py
│   ├── auth_routes.py          # Authentication endpoints
│   ├── compliance_routes.py    # Compliance framework endpoints
│   ├── identiclaw_routes.py    # Agent identity (DID) endpoints
│   ├── mcp_gateway.py          # MCP server - 13 tools, Goose / Claude Desktop
│   ├── openclaw_routes.py      # OpenClaw governance endpoints (12 routes)
│   ├── security_routes.py      # Security event endpoints
│   └── tenancy_routes.py       # Multi-tenant management endpoints
│
├── toolroom/                   # Supply-chain security for agent tools
│   ├── __init__.py
│   ├── cage.py                 # Tool sandboxing
│   ├── executor.py             # Gated tool execution
│   ├── foreman.py              # Tool approval workflow
│   ├── function_tools.py       # Function-based tool wrappers
│   ├── manifest.py             # Tool manifest validation
│   ├── registry.py             # Tool registry
│   ├── TOOLROOM.md             # Toolroom documentation
│   └── tools/                  # Installed tool packages
│
├── alembic/                    # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial_schema.py
│       ├── 002_identiclaw_identity.py
│       └── 003_openclaw_instances.py
│
├── federation/                 # Cross-instance trust
│   ├── mtls.py                 # mTLS certificate management
│   └── trust.py                # Federation manager, trust protocols
│
├── gateway/                    # Egress security
│   ├── egress_proxy.py         # Outbound traffic control + domain whitelist
│   ├── Dockerfile
│   └── requirements.txt
│
├── celery_app/                 # Background task processing
│   └── worker.py               # Celery worker + beat configuration
│
├── persistence/                # Data storage adapters
│   └── (Redis / file adapters)
│
├── monitoring/                 # Observability configuration
│   ├── prometheus.yml          # Prometheus scrape config
│   ├── prometheus/
│   │   └── alerts.yml          # Alert rules
│   ├── grafana/
│   │   ├── dashboards/         # Dashboard JSON definitions
│   │   └── provisioning/       # Grafana provisioning config
│   └── mosquitto/
│       └── mosquitto.conf      # MQTT broker config
│
├── .github/                    # GitHub configuration
│   ├── workflows/
│   │   ├── ci.yml              # CI pipeline (5 stages: unit, security, docker, integration, quality)
│   │   ├── codeql.yml          # CodeQL SAST - Python security analysis
│   │   └── summary.yml         # PR/push summary workflow
│   ├── ISSUE_TEMPLATE/         # Bug report and feature request templates
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS              # Auto-review assignment for security paths
│   ├── dependabot.yml          # Automated pip + Actions dependency updates
│   └── FUNDING.yml             # GitHub Sponsors configuration
│
├── scripts/                    # Operational utilities
│   ├── generate_secrets.sh     # Secret generation + .env sync + mosquitto password
│   ├── generate_individual_proof_sheets.py  # Generate TB-TEST-* sheets (721 files)
│   ├── generate_class_level_proof_sheets.py # Generate TB-PROOF-053+ class-level sheets
│   ├── backup.sh               # Backup script
│   ├── restore.sh              # Restore script
│   ├── run_all_tests.sh        # Convenience test runner script
│   ├── dr_test.sh              # Disaster recovery test
│   ├── governance_smoke_test.sh  # 13-step live governance verification
│   ├── seed_demo_data.py       # Demo data setup
│   ├── test_security_flow.py   # API integration test
│   └── test_federation.py      # Federation test
│
├── tests/                      # Test suite — 5,416 passing, 3 skipped, 0 failed (CI run #309)
│   ├── conftest.py             # Pytest fixtures + _register_user helper
│   │
│   ├── — Core governance & security —
│   ├── test_openclaw.py        # OpenClaw governance engine (55 tests)
│   ├── test_qms.py             # QMS v2.2.0 protocol (115 tests)
│   ├── test_identiclaw.py      # Agent identity — DID / Ed25519 (50 tests)
│   ├── test_security_battery.py  # 9-category security attack surface (96 tests)
│   ├── test_behavioral.py      # Trust progression behavioral specs (30 tests)
│   ├── test_contracts.py       # Enum contract tripwires (7 tests)
│   ├── test_signing.py         # Cryptographic signing (13 tests)
│   ├── test_secrets.py         # Secrets management (48 tests)
│   ├── test_capabilities.py    # Capability enforcement (15 tests)
│   │
│   ├── — Infrastructure & integration —
│   ├── test_api.py             # API endpoint smoke tests (19 tests)
│   ├── test_e2e_integration.py # End-to-end workflows (29 tests)
│   ├── test_integration.py     # Integration layer (26 tests)
│   ├── test_observability.py   # Metrics and monitoring (40 tests)
│   ├── test_ollama.py          # Local LLM inference (49 tests)
│   ├── test_toolroom.py        # Toolroom supply-chain security (129 tests)
│   ├── test_mqtt_stress.py     # MQTT stress tests (excluded from standard run)
│   │
│   ├── — Core module depth tests (one file per module) —
│   ├── test_core_qms_depth.py                  # 165 tests
│   ├── test_core_audit_depth.py                # 159 tests
│   ├── test_core_semantic_matching_depth.py    # 127 tests
│   ├── test_core_data_classification_depth.py  # 122 tests
│   ├── test_core_threat_response_depth.py      # 115 tests
│   ├── test_core_trust_levels_depth.py         # 100 tests
│   ├── test_core_phi_deidentification_depth.py # 100 tests
│   ├── test_core_tenancy_depth.py              # 97 tests
│   ├── test_core_manners_depth.py              # 96 tests
│   ├── test_core_hitrust_controls_depth.py     # 95 tests
│   ├── test_core_training_depth.py             # 85 tests
│   ├── test_core_rbac_depth.py                 # 85 tests
│   ├── test_core_openclaw_depth.py             # 83 tests
│   ├── test_core_session_management_depth.py   # 79 tests
│   ├── test_core_data_retention_depth.py       # 79 tests
│   ├── test_core_tenant_rate_limiting_depth.py # 78 tests
│   ├── test_core_minimum_necessary_depth.py    # 75 tests
│   ├── test_compliance_depth.py                # 74 tests
│   ├── test_core_rate_limiting_depth.py        # 68 tests
│   ├── test_core_compliance_depth.py           # 68 tests
│   ├── test_core_captcha_depth.py              # 68 tests
│   ├── test_core_approval_depth.py             # 67 tests
│   ├── test_core_breach_notification_depth.py  # 66 tests
│   ├── test_core_secrets_depth.py              # 64 tests
│   ├── test_core_capabilities_depth.py         # 64 tests
│   ├── test_core_sanctions_depth.py            # 63 tests
│   ├── test_core_anomaly_depth.py              # 61 tests
│   ├── test_core_user_management_depth.py      # 60 tests
│   ├── test_core_secure_storage_depth.py       # 60 tests
│   ├── test_core_system_analysis_depth.py      # 59 tests
│   ├── test_core_legal_hold_depth.py           # 55 tests
│   ├── test_core_baa_tracking_depth.py         # 54 tests
│   ├── test_core_email_verification_depth.py   # 53 tests
│   ├── test_core_rotation_depth.py             # 51 tests
│   ├── test_core_contingency_testing_depth.py  # 51 tests
│   ├── test_core_mfa_depth.py                  # 49 tests
│   ├── test_core_emergency_access_depth.py     # 49 tests
│   ├── test_core_signing_depth.py              # 47 tests
│   ├── test_core_middleware_depth.py           # 47 tests
│   ├── test_core_phi_disclosure_depth.py       # 46 tests
│   ├── test_core_delegation_depth.py           # 41 tests
│   ├── test_core_persistence_depth.py          # 40 tests
│   ├── test_core_metrics_depth.py              # 36 tests
│   ├── test_core_auth_depth.py                 # 26 tests
│   ├── test_core_auth_dependencies_depth.py    # 18 tests
│   │
│   ├── — Agent depth tests —
│   ├── test_agents_transaction_depth.py        # 140 tests
│   ├── test_agents_memory_depth.py             # 100 tests
│   ├── test_agents_document_depth.py           # 62 tests
│   ├── test_agents_alien_adapter_depth.py      # 56 tests
│   ├── test_agents_backup_depth.py             # 50 tests
│   ├── test_agents_demo_depth.py               # 42 tests
│   ├── test_agents_base_depth.py               # 29 tests
│   │
│   ├── — API routes depth tests —
│   ├── test_security_routes_depth.py           # 58 tests
│   ├── test_tenancy_routes_depth.py            # 38 tests
│   ├── test_mcp_gateway_depth.py               # 34 tests
│   ├── test_auth_routes_depth.py               # 27 tests
│   │
│   ├── — Toolroom depth tests —
│   ├── test_toolroom_registry_depth.py         # 105 tests
│   ├── test_toolroom_manifest_depth.py         # 92 tests
│   ├── test_toolroom_function_tools_depth.py   # 42 tests
│   ├── test_toolroom_executor_depth.py         # 40 tests
│   ├── test_toolroom_foreman_depth.py          # 38 tests
│   │
│   ├── — Supplemental —
│   ├── test_user_mgmt_and_analysis.py          # 68 tests
│   ├── test_depth_infrastructure.py            # 31 tests
│   ├── test_depth_hardening.py                 # 28 tests
│   ├── test_coverage_boost.py                  # 106 tests
│   ├── test_coverage_boost2.py                 # 70 tests
│   ├── test_coverage_boost3.py                 # 25 tests
│   ├── test_coverage_boost4.py                 # 33 tests
│   ├── test_coverage_boost5.py                 # 124 tests
│   └── test_coverage_boost6.py                 # 44 tests
│
├── proof_sheets/               # 788 proof documents - every claim and every test, backed by code
│   ├── INDEX.md                # Full index (788 documents, verification status)
│   ├── TB-PROOF-001_tests_passing.md
│   ├── TB-PROOF-002_security_tests.md
│   ├── ... (TB-PROOF-001 through TB-PROOF-066, class-level evidence)
│   └── individual/             # 721 individual test proof sheets (TB-TEST-* series)
│       ├── sec/                # 96 sheets - security battery
│       ├── qms/                # 115 sheets - QMS™ protocol tests
│       ├── tool/               # 129 sheets - Toolroom tests
│       ├── ocl/                # 55 sheets - OpenClaw governance tests
│       ├── idn/                # 50 sheets - IdentiClaw identity tests
│       ├── oll/                # 49 sheets - Ollama LLM tests
│       ├── obs/                # 40 sheets - Observability tests
│       ├── beh/                # 30 sheets - Behavioral tests
│       ├── e2e/                # 29 sheets - End-to-end integration tests
│       ├── scrt/               # 48 sheets - Secrets management tests
│       ├── int/                # 26 sheets - Cross-system integration tests
│       ├── cap/                # 15 sheets - Capability enforcement tests
│       ├── sign/               # 13 sheets - Message signing tests
│       ├── api/                # 19 sheets - API endpoint tests
│       └── ctrct/              # 7 sheets - Enum contract tests
│
├── huggingface_space/          # HuggingFace live demo
│   ├── app.py                  # Gradio app - live governance pipeline demo
│   ├── README.md               # HF Space config (frontmatter) + description
│   └── requirements.txt
│
├── frontend/                   # Static dashboard assets
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
├── website/                    # Marketing website
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
├── screenshots/                # README and documentation images + demo GIFs
│
├── docs/                       # Technical documentation
│   ├── Operation Documents/
│   │   ├── DEVELOPER_GUIDE.md         # Embedded Python agent development
│   │   ├── OPENCLAW_INTEGRATION_GUIDE.md  # External agent integration (REST API)
│   │   ├── OPENCLAW_OPERATIONS.md     # Day-to-day OpenClaw operations
│   │   ├── DEPLOYMENT_GUIDE.md        # Full deployment guide
│   │   ├── INSTALLATION_GUIDE_WINDOWS.md  # Windows setup
│   │   ├── TROUBLESHOOTING.md
│   │   ├── PRICING_MODEL.md
│   │   └── SHARED_RESPONSIBILITY.md
│   ├── System Documents/
│   │   ├── API_REFERENCE.md
│   │   ├── SECURITY_ARCHITECTURE.md
│   │   ├── ENV_CONFIGURATION.md
│   │   ├── ENCRYPTION_AT_REST.md
│   │   ├── SECRETS_MANAGEMENT.md
│   │   ├── SOC2_TYPE_I.md
│   │   ├── HA_ARCHITECTURE.md
│   │   ├── PROJECT_OVERVIEW.md
│   │   └── DATA_PROCESSING_AGREEMENT.md
│   ├── Compliance Documents/
│   │   ├── COMPLIANCE_ROADMAP.md
│   │   ├── HEALTHCARE_COMPLIANCE.md
│   │   ├── LEGAL_COMPLIANCE.md
│   │   ├── MANNERS_COMPLIANCE.md
│   │   └── PENTEST_PREPARATION.md
│   ├── Backup and Recovery Documents/
│   │   ├── BACKUP_RECOVERY.md
│   │   ├── DISASTER_RECOVERY.md
│   │   ├── INCIDENT_RESPONSE.md
│   │   └── Restore_and_Recover_Guide.md
│   ├── QMS Documents/
│   │   └── QMS_SPECIFICATION.md   # QMS™ protocol reference v2.1.6
│   └── Testing Documents/
│       ├── ADDITIONAL_AWS_TESTS.md
│       ├── DISASTER_RECOVERY_TEST.md
│       ├── HARDENING_CC.md
│       ├── governance_smoke_test_result.txt
│       └── user_ui_tests.md
│
├── licenses/                   # Third-party license files
│
├── LICENSE                     # Apache License 2.0
├── NOTICE                      # Apache 2.0 required attribution
├── README.md                   # Project overview, GIFs, screenshots, architecture
├── QUICKSTART.md               # 5-minute path: clone to first governance decision
├── CHANGELOG.md                # Version history (keepachangelog format)
├── CITATION.cff                # Machine-readable citation (GitHub cite button)
├── CODE_OF_CONDUCT.md
├── COMMERCIAL_LICENSE.md       # Commercial licensing terms
├── CONTRIBUTING.md
├── GOVERNANCE.md               # Project governance, decisions, release process
├── SECURITY.md                 # Vulnerability reporting and responsible disclosure
├── SUPPORT.md                  # Support channels and response times
├── TRADEMARKS.md               # Trademark policy (ClawCoat, QMS™)
├── DOC_INDEX.md                # Master navigation index for all 70+ documents
├── PROOF_INDEX.md              # Entry point for 788 proof documents
├── Makefile                    # Developer shortcuts: make test, run, lint, clean
├── requirements.txt            # Runtime Python dependencies (version-pinned)
├── requirements-dev.txt        # Dev/lint/test tooling (isort, bandit, coverage)
└── docs/                       # All non-root documentation (see docs/ section above)
    ├── AMBASSADORS.md          # Ambassador program
    ├── GLOSSARY.md             # Term definitions
    ├── MANNERS.md              # Manners compliance framework
    ├── PROJECT_STRUCTURE.md    # This file
    ├── TESTING.md              # Test procedures and suite breakdown
    ├── TERMS_OF_USE.md         # Terms of use, liability, indemnification
    └── USER_GUIDE.md           # End-user guide to the admin dashboard
```

---

## Key Files by Function

### OpenClaw Governance Pipeline
```
api/openclaw_routes.py → core/openclaw.py → core/trust_levels.py → core/manners.py → core/approval.py → core/audit.py
```

### Embedded Python Agent Execution
```
agents/base.py (SecureBaseAgent) → core/capabilities.py → core/approval.py → gateway/egress_proxy.py → core/audit.py
```

### External Agent Integration (REST)
```
POST /v1/openclaw/{id}/action → api/openclaw_routes.py → core/openclaw.py (evaluate_action) → core/audit.py
```

### MCP Gateway (Goose / Claude Desktop)
```
GET /mcp → api/mcp_gateway.py → core/openclaw.py (trust-gated) → core/audit.py
```

### Authentication Chain
```
main.py → core/auth.py → core/rbac.py → core/mfa.py → core/session_management.py
```

### Federation Flow
```
main.py → federation/trust.py → federation/mtls.py → core/signing.py → (remote instance)
```

---

## Environment Files

| File | Purpose | Git |
|------|---------|-----|
| `.env.example` | Template with all variables | Tracked |
| `.env` | Actual secrets | Ignored |
| `secrets/` | Docker secrets (API keys, passwords) | Ignored |
| `.dockerignore` | Build exclusions | Tracked |

---

## Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| `traefik` | 80 / 443 | Reverse proxy, TLS 1.2+, HSTS |
| `mcp_server` | 8000 | Main API + MCP gateway at /mcp |
| `worker` | - | Celery background tasks |
| `beat` | - | Scheduled tasks |
| `redis` | 6379 | Message broker, cache, agent state |
| `postgres` | 5432 | Persistent relational storage |
| `ollama` | 11434 | Local LLM inference (no cloud AI) |
| `open-webui` | 3000 | Chat interface for local LLMs |
| `mosquitto` | 1883 | MQTT agent messaging bus |
| `prometheus` | 9090 | Metrics collection |
| `grafana` | 3001 | Monitoring dashboards |
| `mailhog` *(dev only)* | 1025 / 8025 | SMTP capture for development - `--profile dev` |

> Production deployments omit `--profile dev`. MailHog is replaced by real SMTP vars in `.env`.

---

## Integration Paths

| Use Case | Path |
|---|---|
| Python agent inside ClawCoat | Inherit `SecureBaseAgent` - see `docs/Operation Documents/DEVELOPER_GUIDE.md` |
| External agent (any language/framework) | Call `/v1/openclaw/{id}/action` - see `docs/Operation Documents/OPENCLAW_INTEGRATION_GUIDE.md` |
| Goose / Claude Desktop | Point MCP client at `http://localhost:8000/mcp` with API key - see `goose.yaml` |

---

*For setup instructions, see `README.md`. For API details, see `docs/System Documents/API_REFERENCE.md`.*
