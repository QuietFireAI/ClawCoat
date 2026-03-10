# Video - Claude Desktop Governed by TelsonBase

Real AI agent. Real governance. No curl simulation.

---

## What's Happening

Claude Desktop on your machine connects to TelsonBase on the DO server via MCP.
The `claude-desktop-demo` agent is registered at QUARANTINE.
Claude tries something it's not allowed to do. TelsonBase stops it.
You promote it. Claude tries again. It works.

---

## Before You Record

Claude Desktop is already configured. The agent is registered.
Just confirm the MCP server connected:
- Open Claude Desktop
- Look for the hammer icon (tools) in the chat toolbar
- If it's there - connected. If not - fully quit Claude Desktop (system tray → Quit) and reopen.

---

## The Script

**Step 1 - Ask Claude to list agents**

Type in Claude Desktop:
```
List all the agents registered in TelsonBase
```

Claude calls `list_agents` - QUARANTINE+ tool, the session has access.
You see agent names, trust levels, Manners scores come back.
This proves the connection is live.

---

**Step 2 - Ask Claude to list tenants (this gets blocked)**

Type:
```
List all the tenants
```

Claude calls `list_tenants` - requires PROBATION+. Session is at QUARANTINE.

Claude gets back:
```
Tool 'list_tenants' requires 'probation' trust - session is at 'quarantine'.
Administrator: promote this session in the TelsonBase dashboard.
```

**That is TelsonBase governing a real AI agent in real time.**
Claude didn't decide not to do it. TelsonBase stopped it.

---

**Step 3 - Promote the agent (Git Bash, while still recording)**

Open Git Bash alongside Claude Desktop. Paste this as one block:

```bash
ssh root@159.65.241.102 'KEY=$(cat /root/telsonbase/secrets/telsonbase_mcp_api_key) && curl -s -X POST http://localhost:8000/v1/openclaw/ad80d359aecd4bfa/promote -H "X-API-Key: $KEY" -H "Content-Type: application/json" -d "{\"new_level\":\"probation\",\"reason\":\"Promoted for video demo - earned access\"}" | python3 -m json.tool'
```

You see `"trust_level": "probation"` come back.

---

**Step 4 - Ask the same question again**

Back in Claude Desktop:
```
Now list all the tenants
```

Claude calls `list_tenants` again. Same agent, same tool, same question.
This time it works.

**That is earned promotion. Same agent. Different answer.**

---

## Agent Details (DO Server)

| Field | Value |
|---|---|
| instance_id | ad80d359aecd4bfa |
| name | claude-desktop-demo |
| starting trust | quarantine |
| agent_key | da283437c8f4161f5bb52cbe992aca89a2b82368bc034416a4512ce6fbb6ab5b |

---

## After the Video - Reset for Next Run

Demote back to quarantine so you can run it again:

```bash
ssh root@159.65.241.102 'KEY=$(cat /root/telsonbase/secrets/telsonbase_mcp_api_key) && curl -s -X POST http://localhost:8000/v1/openclaw/ad80d359aecd4bfa/demote -H "X-API-Key: $KEY" -H "Content-Type: application/json" -d "{\"new_level\":\"quarantine\",\"reason\":\"Reset after video demo\"}"'
```
