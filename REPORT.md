# Lab 8 — Report by Leilia

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

## Task 2A — Deployed agent

Nanobot gateway запущен как Docker сервис.

**Startup log:**
nanobot-1 | 🐈 Starting nanobot gateway version 0.1.4.post6 on port 18790…
nanobot-1 | ✓ Channels enabled: webchat
nanobot-1 | MCP: registered tool ‘mcp_lms_lms_health’ from server ‘lms’
nanobot-1 | MCP: registered tool ‘mcp_lms_lms_labs’ from server ‘lms’
nanobot-1 | MCP server ‘lms’: connected, 9 tools registered
nanobot-1 | Agent loop started


---

## Task 2B — Web client

**WebSocket тест:**
$ websocat “ws://localhost:42002/ws/chat?access_key=02051955”
{“content”:“What labs are available?”}
{“type”:“text”,“content”:"Here are the available labs in the LMS:

Lab 01 – Products, Architecture & Roles
Lab 02 — Run, Fix, and Deploy a Backend Service
…
Lab 08 — lab-08
"}

**Flutter UI:** Доступен по адресу `http://10.93.26.99:42002/flutter`


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
🔍 Health Check Summary
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

