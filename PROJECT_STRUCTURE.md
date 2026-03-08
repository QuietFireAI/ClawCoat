# TelsonBase Project Structure

**Version:** v11.0.1 | **Updated:** March 8, 2026

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
├── run_all_tests.sh            # Convenience test runner script
├── goose.yaml                  # Goose MCP client config (copy to ~/.config/goose/)
├── .env.example                # Environment template (copy to .env)
│
├── core/                       # Security & governance engine (~60 modules)
│   │
│   ├── — Governance —
│   ├── openclaw.py             # OpenClaw governance engine + OpenClawManager singleton
│   ├── trust_levels.py         # AgentTrustLevel enum (QUARANTINE → AGENT), permission matrix
│   ├── manners.py              # Manners compliance scoring engine
│   ├── identiclaw.py           # Agent identity (DID, Ed25519, verifiable credentials)
│   │
│   ├── — Auth & Access —
│   ├── config.py               # Centralized settings (pydantic)
│   ├── auth.py                 # JWT authentication
│   ├── auth_dependencies.py    # FastAPI auth dependency helpers
│   ├── rbac.py                 # Role-based access control (4-tier)
│   ├── mfa.py                  # TOTP multi-factor authentication (RFC 6238)
│   ├── captcha.py              # CAPTCHA challenge/response
│   ├── sessions.py             # Session store
│   ├── session_management.py   # HIPAA-compliant idle timeout
│   ├── delegation.py           # Permission delegation
│   ├── emergency_access.py     # Break-glass emergency access
│   │
│   ├── — Security —
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
│   ├── — Compliance —
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
│   ├── — Infrastructure —
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
│   ├── mcp_gateway.py          # MCP server — 13 tools, Goose / Claude Desktop
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
├── scripts/                    # Operational utilities
│   ├── generate_secrets.sh     # Secret generation + .env sync + mosquitto password
│   ├── generate_individual_proof_sheets.py  # Generate TB-TEST-* sheets (721 files)
│   ├── generate_class_level_proof_sheets.py # Generate TB-PROOF-053+ class-level sheets
│   ├── backup.sh               # Backup script
│   ├── restore.sh              # Restore script
│   ├── dr_test.sh              # Disaster recovery test
│   ├── governance_smoke_test.sh  # 13-step live governance verification
│   ├── seed_demo_data.py       # Demo data setup
│   ├── test_security_flow.py   # API integration test
│   └── test_federation.py      # Federation test
│
├── tests/                      # Test suite — 720 passing, 1 skipped
│   ├── conftest.py             # Pytest fixtures + _register_user helper
│   ├── test_api.py             # API endpoint tests
│   ├── test_behavioral.py      # Behavioral anomaly tests
│   ├── test_capabilities.py    # Permission enforcement tests
│   ├── test_contracts.py       # Enum contract tripwires (TenantType, AgentTrustLevel)
│   ├── test_e2e_integration.py # End-to-end integration tests (29)
│   ├── test_identiclaw.py      # Agent identity tests
│   ├── test_integration.py     # Integration tests
│   ├── test_mqtt_stress.py     # MQTT stress tests (excluded from standard run)
│   ├── test_observability.py   # Metrics and monitoring tests
│   ├── test_ollama.py          # Local LLM tests
│   ├── test_openclaw.py        # OpenClaw governance tests
│   ├── test_qms.py             # QMS logging tests
│   ├── test_secrets.py         # Secrets management tests
│   ├── test_security_battery.py  # 96-test security battery
│   ├── test_signing.py         # Cryptographic signing tests
│   └── test_toolroom.py        # Toolroom supply-chain tests
│
├── proof_sheets/               # 787 proof documents — every claim and every test, backed by code
│   ├── INDEX.md                # Full index (787 documents, verification status)
│   ├── TB-PROOF-001_tests_passing.md
│   ├── TB-PROOF-002_security_tests.md
│   ├── ... (TB-PROOF-001 through TB-PROOF-066, class-level evidence)
│   └── individual/             # 721 individual test proof sheets (TB-TEST-* series)
│       ├── sec/                # 96 sheets — security battery
│       ├── qms/                # 115 sheets — QMS™ protocol tests
│       ├── tool/               # 129 sheets — Toolroom tests
│       ├── ocl/                # 55 sheets — OpenClaw governance tests
│       ├── idn/                # 50 sheets — IdentiClaw identity tests
│       ├── oll/                # 49 sheets — Ollama LLM tests
│       ├── obs/                # 40 sheets — Observability tests
│       ├── beh/                # 30 sheets — Behavioral tests
│       ├── e2e/                # 29 sheets — End-to-end integration tests
│       ├── scrt/               # 48 sheets — Secrets management tests
│       ├── int/                # 26 sheets — Cross-system integration tests
│       ├── cap/                # 15 sheets — Capability enforcement tests
│       ├── sign/               # 13 sheets — Message signing tests
│       ├── api/                # 19 sheets — API endpoint tests
│       └── ctrct/              # 7 sheets — Enum contract tests
│
├── huggingface_space/          # HuggingFace live demo
│   ├── app.py                  # Gradio app — live governance pipeline demo
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
│       ├── TEST_RESULTS_6.0.0CC.md
│       ├── VALIDATION_REPORT_v7.4.0CC.md
│       ├── governance_smoke_test_result.txt
│       └── user_ui_tests.md
│
├── licenses/                   # Third-party license files
│
├── LICENSE                     # Apache License 2.0
├── README.md                   # Project overview and quick start
├── AMBASSADORS.md              # Ambassador program
├── CHANGELOG.md                # Version history
├── CITATION.cff                # Machine-readable citation (GitHub cite button)
├── CODE_OF_CONDUCT.md
├── COMMERCIAL_LICENSE.md       # Commercial licensing terms
├── CONTRIBUTING.md
├── TERMS_OF_USE.md             # Terms of use, liability, indemnification (replaces DISCLAIMER.md)
├── GLOSSARY.md                 # Term definitions
├── MANNERS.md                  # Manners compliance framework documentation
├── PROJECT_STRUCTURE.md        # This file
├── SECURITY.md                 # Vulnerability reporting
├── TESTING.md                  # Test procedures
├── TRADEMARKS.md               # Trademark policy
└── USER_GUIDE.md               # End-user guide
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
| `worker` | — | Celery background tasks |
| `beat` | — | Scheduled tasks |
| `redis` | 6379 | Message broker, cache, agent state |
| `postgres` | 5432 | Persistent relational storage |
| `ollama` | 11434 | Local LLM inference (no cloud AI) |
| `open-webui` | 3000 | Chat interface for local LLMs |
| `mosquitto` | 1883 | MQTT agent messaging bus |
| `prometheus` | 9090 | Metrics collection |
| `grafana` | 3001 | Monitoring dashboards |
| `mailhog` *(dev only)* | 1025 / 8025 | SMTP capture for development — `--profile dev` |

> Production deployments omit `--profile dev`. MailHog is replaced by real SMTP vars in `.env`.

---

## Integration Paths

| Use Case | Path |
|---|---|
| Python agent inside TelsonBase | Inherit `SecureBaseAgent` — see `docs/Operation Documents/DEVELOPER_GUIDE.md` |
| External agent (any language/framework) | Call `/v1/openclaw/{id}/action` — see `docs/Operation Documents/OPENCLAW_INTEGRATION_GUIDE.md` |
| Goose / Claude Desktop | Point MCP client at `http://localhost:8000/mcp` with API key — see `goose.yaml` |

---

*For setup instructions, see `README.md`. For API details, see `docs/System Documents/API_REFERENCE.md`.*
