# ClawFilters — Telegram Gateway Guide

**Govern your agents from anywhere. Approve, reject, and suspend from your phone.**

---

## Overview

The Telegram Gateway connects ClawFilters's HITL approval system to a Telegram bot. When an agent action hits a governance gate, a message fires to your configured chat with inline Approve and Reject buttons. Tap to decide. The gate resolves. The action proceeds or is blocked — before execution.

This is not a notification add-on. It is a full governance channel. Every decision made through Telegram is recorded in the audit chain with the same weight as a web UI decision.

**What it does:**

- Sends HITL approval requests as Telegram messages with inline Approve / Reject buttons
- `/kill <agent_id>` — suspends an agent instantly from anywhere
- `/pending` — lists all open approval requests
- `/status` — active agents, trust tiers, Manners scores, pending gate count
- Sends "ClawFilters online" on startup and "offline" on shutdown
- Operates in polling mode (default) or webhook mode (for HTTPS deployments)

---

## Prerequisites

- A running ClawFilters deployment (v11.0.3+)
- A Telegram account
- Access to [@BotFather](https://t.me/BotFather) on Telegram

---

## Step 1 — Create a Telegram Bot

1. Open Telegram and start a conversation with **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g. `ClawFilters Governance`)
4. Choose a username ending in `bot` (e.g. `clawfilters_ops_bot`)
5. BotFather returns a token — copy it. This is your `TELEGRAM_BOT_TOKEN`.

Keep this token private. It gives full control of the bot.

---

## Step 2 — Create a Private Channel or Group

ClawFilters sends governance messages to a single configured chat. A private group with only you (and the bot) is the recommended setup for operator use.

**Create a private group:**
1. In Telegram, create a new group
2. Name it (e.g. `ClawFilters Ops`)
3. Add your bot to the group

**Get the Chat ID:**

Option A — via the Telegram API (simplest):
```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```
Send any message to the group, then open that URL in a browser. Look for `"chat":{"id":...}` in the result. The ID is your `TELEGRAM_CHAT_ID`. Group IDs are negative numbers (e.g. `-1001234567890`).

Option B — add `@RawDataBot` or `@userinfobot` to the group temporarily, send a message, read the chat ID, then remove the bot.

---

## Step 3 — Configure ClawFilters

Add to your `.env` file:

```env
# --- Telegram Gateway ---
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=1234567890:ABCDefGhIjKlMnOpQrStUvWxYz
TELEGRAM_CHAT_ID=-1001234567890
```

For **webhook mode** (HTTPS deployments — recommended for production):

```env
TELEGRAM_WEBHOOK_URL=https://your-clawfilters-domain.com
```

Leave `TELEGRAM_WEBHOOK_URL` empty to use polling mode (default). Polling works on any deployment including localhost and non-HTTPS setups.

---

## Step 4 — Restart ClawFilters

```bash
docker compose up -d mcp_server
```

On startup, the bot sends a message to your chat:

> 🦞 **ClawFilters online** — governance gateway active.

If you do not see this message, check the logs:

```bash
docker compose logs mcp_server | grep -i telegram
```

---

## Using the Gateway

### HITL Approval Requests

When an agent action requires human approval, a message fires automatically:

```
🚨 HITL Gate — URGENT
ID: APPR-3F7A2B1C9D04
Agent: openclaw:demo_quarantine
Action: filesystem.delete_file
File deletion — requires human approval
⚠️ Risk: data_loss, first_agent_action
⏱ Expires: 14:30 UTC 21 Mar

[✅ Approve]  [❌ Reject]
```

Tap **Approve** or **Reject**. The message updates to show the decision and who made it. The agent's action either proceeds or is blocked.

The first response wins. If the web UI and Telegram both show the request, whichever is tapped first resolves the gate.

---

### Commands

Send these as messages to the bot's chat:

| Command | Effect |
|---|---|
| `/pending` | List all open approval requests |
| `/status` | System summary — active agents, tiers, Manners scores, pending gates |
| `/kill <agent_id>` | Suspend an agent immediately — all subsequent actions blocked until reinstated |
| `/help` | Command reference |

**Example — suspend an agent:**
```
/kill openclaw:rogue_agent_id
```
Response:
```
🛑 Kill switch activated — agent openclaw:rogue_agent_id suspended.
```

**Example — check status:**
```
/status
```
Response:
```
📊 ClawFilters Status
  Pending HITL gates: 2
  Active OpenClaw instances: 5
  • demo_quarantine [quarantine] score=1.00
  • demo_probation [probation] score=0.87
  • demo_resident [resident] score=0.94
  • demo_citizen [citizen] score=0.91
  • demo_agent [agent] score=0.96
```

---

## Polling vs. Webhook Mode

| | Polling | Webhook |
|---|---|---|
| **Setup** | No configuration beyond the token and chat ID | Requires `TELEGRAM_WEBHOOK_URL` pointing to a public HTTPS URL |
| **Works on localhost** | Yes | No |
| **Works without HTTPS** | Yes | No |
| **Latency** | ~1–2 seconds | Near-instant |
| **Recommended for** | Local, dev, homelab | Production (DigitalOcean, VPS with domain) |

In polling mode, ClawFilters runs a background thread that long-polls Telegram every 20 seconds. In webhook mode, Telegram pushes updates to `POST /v1/telegram/webhook` on your ClawFilters instance.

ClawFilters automatically switches modes based on whether `TELEGRAM_WEBHOOK_URL` is set.

---

## Security Notes

- **Keep the bot private.** Only add it to a channel you control. Anyone in the channel can send commands.
- **Bot token = full bot control.** Treat it like a password. Store it in `.env` (never in source code).
- **Decisions are audited.** Every Telegram approve/reject is recorded in the cryptographic audit chain with `decided_by: telegram:<username>`.
- **The bot does not have ClawFilters API credentials.** It communicates only through the internal `approval_gate` and `openclaw_manager` — no external API exposure.

---

## Audit Trail

All Telegram-originated decisions appear in the audit chain:

```json
{
  "event_type": "task_completed",
  "message": "Approval request APPR-3F7A2B1C9D04 approved by telegram:jeff_ops",
  "actor": "telegram:jeff_ops",
  "resource": "APPR-3F7A2B1C9D04"
}
```

Kill-switch events:

```json
{
  "event_type": "security_event",
  "message": "Kill switch: openclaw:rogue_agent suspended",
  "actor": "telegram:jeff_ops"
}
```

---

## Troubleshooting

**Bot is configured but no startup message received:**
- Verify `TELEGRAM_BOT_TOKEN` is correct (test: `curl https://api.telegram.org/bot<TOKEN>/getMe`)
- Verify `TELEGRAM_CHAT_ID` is correct — group IDs are negative numbers
- Confirm the bot was added to the group before ClawFilters started
- Check logs: `docker compose logs mcp_server | grep -i telegram`

**Webhook mode not receiving updates:**
- Verify `TELEGRAM_WEBHOOK_URL` is publicly reachable over HTTPS
- Check webhook status: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
- ClawFilters registers the webhook at `<TELEGRAM_WEBHOOK_URL>/v1/telegram/webhook`

**Tap on Approve/Reject does nothing:**
- The request may have already been resolved (web UI or timeout)
- Check `/pending` — if the request no longer appears, it was resolved elsewhere
- Expired requests return no error from the button; check the audit trail

**`/kill` returns "Agent not found":**
- Verify the agent ID exactly — use `/status` to see registered agents
- The agent may already be suspended

---

*ClawFilters v11.1.0+ · Quietfire AI · Apache 2.0*
