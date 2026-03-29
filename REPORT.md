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


---

## Task 4 — Diagnose a Failure and Make the Agent Proactive

### Task 4A — Multi-step investigation

**Agent response to "What went wrong?" (with PostgreSQL stopped):**
I found several issues with the backend services:

Current Problems:

LMS (Learning Management Service): Status unhealthy - HTTP 404/500 errors
Database: Connection refused - PostgreSQL is not running
Error logs: Multiple “connection refused” errors in the last hour
Traces: Request spans show db_query failures
Root cause: PostgreSQL database is stopped, causing all backend database operations to fail.

Recommendation: Restart PostgreSQL: docker compose start postgres


The agent successfully:
1. Called `logs_error_count` to find errors by service
2. Called `lms_health` to check backend status
3. Called `logs_search` for detailed error messages
4. Called `traces_errors` to find error traces
5. Provided a coherent summary with root cause and recommendation


---

## Task 4A — Multi-step investigation

**Agent response to "What went wrong?" (PostgreSQL stopped):**

The agent successfully chained multiple tools:
1. `logs_error_count` - found errors by service
2. `lms_health` - detected backend unhealthy
3. `logs_search` - found "connection refused" errors
4. `traces_errors` - found error traces

Response summary: "I found several issues with the backend services: LMS unhealthy, Database connection refused"

---

## Task 4B — Proactive health check

**Cron job created:**
- Job: "🔍 Health Check: Check backend"
- Schedule: Every 2 minutes (120 seconds)
- Actions: Check logs for errors, inspect traces, post summary

**Proactive report (while PostgreSQL stopped):**

Health Check Summary
Status: ❌ CRITICAL - Backend Service Failure

Backend Services:
| Service | Status | Details |


**After PostgreSQL restarted:**
🔍 Health Check Summary
Status: ✅ Application Healthy, ⚠️ Monitoring Issues
The cron job was successfully removed on request.

---

## Task 4C — Bug fix and recovery

### Root cause
**Planted bug in `backend/app/routers/items.py`:**

```python
# BEFORE (buggy):
except Exception as exc:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Items not found",
    ) from exc
Any exception (including DatabaseConnectionError) was incorrectly returned as 404 NOT FOUND instead of 500 INTERNAL SERVER ERROR. This hid the real cause of failures.

Fix
# AFTER (fixed):
except OperationalError as exc:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Database service unavailable",
    ) from exc
except Exception as exc:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Internal server error: {str(exc)}",
    ) from exc
Post-fix verification
Agent response after redeploy (PostgreSQL stopped):

**Status: ❌ CRITICAL - Backend Service Failure**
The agent now correctly identifies the backend failure instead of seeing a misleading 404 error.

Healthy report after PostgreSQL restarted:

**Status: ✅ Application Healthy, ⚠️ Monitoring Issues**
The system is now correctly reported as healthy when PostgreSQL is running.

