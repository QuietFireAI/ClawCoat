---
title: ClawCoat
emoji: 🦞
colorFrom: purple
colorTo: indigo
sdk: gradio
sdk_version: "5.20.0"
app_file: app.py
pinned: true
license: apache-2.0
tags:
  - ai-governance
  - ai-agents
  - mcp-gateway
  - agent-security
  - trust-tiers
  - active-decision-making
  - human-in-the-loop
  - audit-trail
  - zero-trust
  - self-hosted
  - mcp
  - goose
  - kill-switch
  - agentic-ai
short_description: "Every agent call: allow, gate, or block. Five tiers."
---

# ClawCoat - Active Decision Making

**Every OpenClaw tool call passes through ClawCoat before execution. Allow, gate for human approval, or block. Every time.**

This Space connects to a live ClawCoat deployment running the full governance pipeline. Select a demo agent, pick an action, and see an actual governance decision.

## What You're Seeing

This is not a simulation. The decisions come from a live ClawCoat instance running the full stack — trust tier enforcement, Manners Engine scoring in real time, HITL approval gates, and a cryptographic audit chain recording every event.

- **Active decision making** — every call evaluated before execution. Allow, gate, or block.
- **Five trust tiers** — QUARANTINE → PROBATION → RESIDENT → CITIZEN → AGENT, earned by behavior
- **Manners Engine** — 8-factor behavioral score (0.0–1.0) updated in real time on every action
- **Kill switch** — suspend an agent instantly, every subsequent action rejected
- **HITL gates** — actions held for human approval regardless of trust tier
- **Audit chain** — every governance decision recorded, cryptographically chained

## Trust Tier Flow

```
QUARANTINE → PROBATION → RESIDENT → CITIZEN → AGENT
 (all gated)  (safe tools)  (read/write)  (broad)   (apex)
```

No agent arrives at AGENT tier. Every agent starts at QUARANTINE and earns its way up through demonstrated behavioral compliance. The Manners Engine drives automatic demotion. Human operators drive promotion.

## The Agent Autonomy SLA

ClawCoat is the working implementation of the Agent Autonomy SLA — a formal per-tier commitment framework defining what an OpenClaw agent may do, under what conditions, and with what audit trail. Jouneaux and Cabot identified this as an open challenge in November 2025 ([arXiv:2511.02885](https://arxiv.org/abs/2511.02885)) and defined `OversightLevel` as a first-class quality metric for AI agent services. ClawCoat makes it runtime-enforced and behaviorally dynamic.

## Full Repository

**[github.com/QuietFireAI/ClawCoat](https://github.com/QuietFireAI/ClawCoat)**

Source code, documentation, proof sheets, deployment guide, and full test suite.
6,254 tests passing. 0 high-severity findings. Apache 2.0. Self-hosted.

---

*ClawCoat v11.0.3 · Quietfire AI · Apache 2.0*
