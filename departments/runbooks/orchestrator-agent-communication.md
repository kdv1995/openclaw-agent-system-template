# Orchestrator ↔ Specialist Agent Communication

## Roles

- Orchestrator: talks to the operator, plans work, decides what to delegate, verifies results, asks for approval before external/destructive actions.
- Specialist agents: own one operational domain, execute bounded tasks, keep their own workspace memory, and report back with evidence.

## Contract

All specialist work follows this contract:

1. the operator talks to the main orchestrator.
2. The orchestrator decides whether to handle the task directly or delegate it.
3. A specialist agent receives a bounded task with owner, scope, allowed actions, inputs, deliverables, and report format.
4. The specialist works inside its own domain/workspace and does not broaden scope without approval.
5. The specialist reports back to the orchestrator with evidence, blockers, and next suggested action.
6. The orchestrator verifies the result, resolves cross-agent context, and replies to the operator.

Specialists are workers with domain ownership, not independent user-facing assistants.

## Default handoff format

```markdown
# Task: <short title>

Owner: <agent-name>
Requested by: orchestrator
Created: YYYY-MM-DD HH:mm Europe/Kyiv
Priority: normal|high|urgent
External action allowed: no|yes, scope: ...

## Goal
...

## Inputs
- paths:
- accounts/services:
- constraints:

## Rules
- ...

## Deliverables
- ...

## Report format
Status: completed|blocked|partial
Changed:
Evidence:
Blockers:
Next suggested action:
```

## Communication channels

1. Direct runtime delegation: orchestrator spawns or messages the specialist session.
2. Durable file handoff: orchestrator writes task specs to `~/.openclaw/departments/inbox/`; specialists move work through `active/`, `done/`, and write reports to `reports/`.
3. Shared evidence: specialists should include exact paths, post IDs, command/test summaries, and blockers.

## Direct Runtime Delegation

Use direct runtime delegation for short, bounded work that should finish during the current conversation:

- Spawn or message the specialist with the task spec.
- Prefer isolated context unless the specialist needs current chat history.
- Include explicit external-action permission if any outside service write is expected.
- The specialist returns a concise report, not a message to the operator.

## Durable File Handoff

Use durable handoff for long-running, resumable, scheduled, or autonomous work:

- New tasks start in `~/.openclaw/departments/inbox/`.
- A specialist moves an accepted task to `active/`.
- Completed task specs move to `done/`.
- Reports go to `reports/YYYY-MM-DD-<task>.md`.
- Reports must include evidence enough for the orchestrator to verify the outcome without guessing.

## Boundaries

- Specialists do not impersonate the operator.
- Specialists do not send direct Telegram/user-facing replies unless the task explicitly says to do that.
- Specialists do not make public/external/destructive actions unless the task explicitly allows it.
- Specialists do not read broad personal memory unless needed for the task.
- If unsure, specialist reports a blocker instead of guessing.

## Required Report Fields

Every specialist report must include:

- `Status`: completed, partial, or blocked.
- `Changed`: files, systems, records, posts, calls, or notes changed.
- `Evidence`: paths, IDs, command summaries, logs, transcripts, screenshots, or API response IDs.
- `Blockers`: none, or the exact missing permission/input/tool.
- `Next suggested action`: what the orchestrator should do next.

## Verification

The orchestrator should not treat a specialist task as complete until at least one meaningful verification step exists:

- direct file inspection
- test/lint/build result
- API/listing confirmation
- created object ID
- transcript/audio/report path
- dry-run result
- explicit blocker

For visible UI, landing pages, dashboards, or frontend implementation, also follow:
`departments/runbooks/design-quality-skill-routing.md`
