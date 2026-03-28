# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

<!-- Paste the agent's response to "What is the agentic loop?" and "What labs are available in our LMS?" -->

## Task 1B — Agent with LMS tools

<!-- Paste the agent's response to "What labs are available?" and "Describe the architecture of the LMS system" -->

## Task 1C — Skill prompt

<!-- Paste the agent's response to "Show me the scores" (without specifying a lab) -->

## Task 2A — Deployed agent

<!-- Paste a short nanobot startup log excerpt showing the gateway started inside Docker -->

## Task 2B — Web client

<!-- Screenshot of a conversation with the agent in the Flutter web app -->

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->

---

## Task 3A — Structured logging

### Happy path log excerpt:
2026-03-28 21:11:08,048 INFO [app.main] - request_started
2026-03-28 21:11:08,050 INFO [app.auth] - auth_success
2026-03-28 21:11:08,050 INFO [app.db.items] - db_query
2026-03-28 21:11:08,057 INFO [app.main] - request_completed

Structured log events visible:
- `request_started` — request received
- `auth_success` — authentication passed
- `db_query` — database operation
- `request_completed` — response sent (status 200)

### Error path log excerpt (PostgreSQL stopped):
From nanobot logs:
2026-03-28 21:20:47.262 | INFO - Response to webchat:
“It looks like the LMS backend is currently unavailable.
I’m getting HTTP 404 and 500 errors when trying to access the labs.”
The agent detected the backend failure through MCP tool calls returning errors.

### VictoriaLogs UI:
URL: `http://10.93.26.99:42002/utils/victorialogs/select/vmui`

Query example: `_stream:{service="backend"} AND level:error`


---

## Task 3B — Traces

VictoriaTraces UI: `http://10.93.26.99:42002/utils/victoriatraces`

Traces show the full request flow across services with timing information.
Each trace contains multiple spans representing individual operations.

---

## Task 3C — Observability MCP tools

### New MCP tools added:

**VictoriaLogs tools:**
- `logs_search` — Search logs using LogsQL query
- `logs_error_count` — Count errors per service over a time window

**VictoriaTraces tools:**
- `traces_list` — List recent traces for a service
- `traces_get` — Fetch a specific trace by ID
- `traces_errors` — Find traces containing errors

### Agent responses:

**Q: "Any errors in the last hour?" (normal conditions)**
A: "Yes, there are errors — but they're in the observability infrastructure itself, not necessarily in your application..."

**Q: "Any errors in the last hour?" (after stopping PostgreSQL)**
A: "Yes, there are errors. Here's what I found for the last hour:
**LMS Backend:** ❌ Unhealthy (HTTP 404 error)
**Observability infrastructure:** Connection errors..."
The agent correctly:
1. Called `logs_error_count` to get error overview
2. Called `traces_errors` to find error traces
3. Called `logs_search` for detailed error logs
4. Called `lms_health` to check backend status
5. Summarized findings concisely

### Files created:
- `mcp/mcp_observability/server.py` — MCP server for observability
- `mcp/mcp_observability/pyproject.toml` — Package config
- `nanobot/workspace/skills/observability/SKILL.md` — Observability skill prompt
- `nanobot/Dockerfile` — Updated with mcp_observability
- `nanobot/config.json` — Added observability MCP server config

