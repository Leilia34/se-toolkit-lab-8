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

