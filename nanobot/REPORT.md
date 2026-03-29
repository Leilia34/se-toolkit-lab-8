## Task 1A — Bare agent

### Q: What is the agentic loop?
A: The agentic loop is the iterative reasoning and action cycle that autonomous AI agents use to accomplish tasks. It typically follows this pattern:
1. Perceive — Observe the current state of the environment or task
2. Think/Reason — Analyze the situation, plan next steps, make decisions
3. Act — Execute an action (call a tool, modify files, send messages, etc.)
4. Observe Results — See the outcome of the action
5. Repeat — Continue the loop until the goal is achieved

### Q: What labs are available in our LMS?
A: I don't have direct access to your LMS (Learning Management System) through my available tools...
### Task 1B — Agent with LMS tools

**Q: What labs are available?**

A: Agent returned 8 labs via MCP tools:
| ID | Title |
|----|-------|
| 1 | Lab 01 – Products, Architecture & Roles |
| 2 | Lab 02 — Run, Fix, and Deploy a Backend Service |
| 3 | Lab 03 — Backend API: Explore, Debug, Implement, Deploy |
| 4 | Lab 04 — Testing, Front-end, and AI Agents |
| 5 | Lab 05 — Data Pipeline and Analytics Dashboard |
| 6 | Lab 06 — Build Your Own Agent |
| 7 | Lab 07 — Build a Client with an AI Coding Agent |
| 8 | lab-08 |
**Q: Describe the architecture of the LMS system**

A: Agent described the full architecture:
- **Core Components**: LMS Backend (Healthy, 56 items in system)
- **Data Model**: 
  - Learners (258 registered students)
  - Labs (8 available)
  - Tasks & Submissions (with attempt tracking)
  - Groups (11 student groups: CSE и DSAI)
- **API Endpoints**: lms_health, lms_labs, lms_learners, lms_pass_rates, lms_timeline, lms_groups, lms_top_learners, lms_completion_rate, lms_sync_pipeline
- **Key Features**: Multi-task labs, Attempt tracking, Group analytics, Timeline tracking, Sync pipeline


## Task 1C — Skill prompt

### Q: Show me the scores (without specifying a lab)
A: Agent provided comprehensive analytics:
- Completion Rates by Lab (table with 8 labs, 100% for Lab 01, 0% for Lab 08)
- Top Learners for Lab 04 (10 students with 100% scores)
- Average Scores by Task for Labs 01-04
- Key Insights: perfect completion for Lab 01, Lab 08 not started, optional tasks have lower scores

The skill prompt helped the agent:
1. Format data in readable tables
2. Provide key insights automatically
3. Offer follow-up questions
