# TelsonBase - Quickstart

**From clone to your first governance decision: under 5 minutes.**

This guide is for developers and evaluators. It assumes Docker Desktop is installed. If you need the full Windows walkthrough, see `docs/Operation Documents/INSTALLATION_GUIDE_WINDOWS.md`.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (running)
- Git Bash (Windows) or any POSIX shell (macOS/Linux)
- Port 8000 free on localhost

---

## Step 1 - Clone and Configure

```bash
git clone https://github.com/QuietFireAI/TelsonBase.git
cd TelsonBase
cp .env.example .env
```

---

## Step 2 - Generate Secrets

Run this in **Git Bash** (Windows) or your POSIX shell:

```bash
bash scripts/generate_secrets.sh
```

This creates the `secrets/` directory and populates `.env` with all cryptographic material. No manual editing required.

---

## Step 3 - Start the Platform

```bash
docker compose up -d --build
```

12 services start: API, Postgres, Redis, Celery, MQTT, Ollama, Prometheus, Grafana, Traefik, and the governance engine.

Wait ~30 seconds, then verify:

```bash
curl http://localhost:8000/health
# {"status": "healthy", ...}
```

---

## Step 4 - Run Database Migrations

```bash
docker compose exec mcp_server alembic upgrade head
```

Run this once after first startup. The API returns 500 until migrations complete.

---

## Step 5 - Get Your API Key

```bash
cat secrets/telsonbase_mcp_api_key
```

Export it for the steps below:

```bash
export API_KEY=$(cat secrets/telsonbase_mcp_api_key)
```

---

## Step 6 - Register an Agent

```bash
curl -s -X POST http://localhost:8000/v1/agents/register \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "my_first_agent", "tenant_id": "default"}' | python3 -m json.tool
```

The response includes an `agent_id` and confirms initial trust level: **QUARANTINE**.

Every new agent starts at QUARANTINE. No exceptions.

---

## Step 7 - See Governance in Action

Attempt an action from QUARANTINE. The governance engine will block it:

```bash
# Replace AGENT_ID with the id from Step 6
curl -s -X POST http://localhost:8000/v1/agents/AGENT_ID/action \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action_type": "http_post", "target": "https://example.com"}' | python3 -m json.tool
```

Expected response: `{"decision": "BLOCKED", "reason": "Trust level QUARANTINE cannot perform http_post"}`.

That decision is now in the tamper-evident audit trail.

---

## What Just Happened

1. Agent registered → landed at **QUARANTINE** (no trust yet earned)
2. Action attempted → **OpenClaw** evaluated the action against the trust policy
3. Governance decision written to the **SHA-256 hash-chained audit trail**

To see the audit trail:

```bash
curl -s http://localhost:8000/v1/audit?limit=5 \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool
```

---

## Next Steps

| What | Where |
|---|---|
| Promote an agent through trust tiers | `docs/MANNERS.md` |
| Full agent governance walkthrough | `docs/Operation Documents/OPENCLAW_INTEGRATION_GUIDE.md` |
| Run the full test suite | `make test` or see `docs/TESTING.md` |
| Deploy to a server | `docs/Operation Documents/DEPLOYMENT_GUIDE.md` |
| Compliance documentation | `docs/Compliance Documents/` |
| All documentation | `DOC_INDEX.md` |

---

## Running the Tests

```bash
# Unit tests (no Docker services required)
make test-unit

# Full suite
make test

# Security battery (96 tests)
make test-security
```

---

*TelsonBase v11.0.1 · Apache 2.0 · [telsonbase.com](https://telsonbase.com)*
