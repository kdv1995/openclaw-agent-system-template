# Threads Factory Agent Operating Model

## Current Architecture

`the operator -> main orchestrator -> specialist agent -> report -> main verification -> the operator`

Specialists do not reply to Telegram. They write reports and return concise status to main.

## Runtime Delegation

Use OpenClaw configured agents when available:

- `threads-research`
- `threads-writer`
- `threads-editor`
- `threads-scheduler`
- `threads-analytics`
- `threads-learning`

For short tasks, main can message/spawn the agent directly.

For durable tasks, main writes a handoff into `tasks/inbox/`. The specialist moves it through:

- `tasks/active/`
- `tasks/done/`
- `reports/`

## Required Handoff

```markdown
# Task: <short title>

Owner: <agent-id>
Requested by: main
Created: YYYY-MM-DD HH:mm Europe/Kyiv
Priority: normal|high|urgent
External action allowed: no|yes, scope: ...

## Goal
...

## Inputs
- paths:
- account:
- constraints:

## Rules
...

## Deliverables
...

## Report format
Status:
Changed:
Evidence:
Blockers:
Next suggested action:
```

## Publishing Safety

Only `threads-scheduler` may create Postiz posts for this factory, and only with explicit scheduling approval from main/the operator.
