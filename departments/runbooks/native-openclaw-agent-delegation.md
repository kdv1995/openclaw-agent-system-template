# Native OpenClaw Agent Delegation

Status: active draft.

## Purpose

Let the main orchestrator keep Telegram/direct conversation lightweight while specialist OpenClaw agents execute bounded tasks in parallel and report back with evidence.

## Default Pattern

1. Orchestrator receives template owner's request.
2. Orchestrator decides whether the task belongs to a specialist.
3. Orchestrator spawns a native OpenClaw child session for short parallel work, or writes a durable task file for long-running work.
4. Specialist works in its own domain and does not message template owner directly.
5. Specialist reports back with required fields.
6. Orchestrator verifies evidence and replies to template owner.

## Native Runtime Delegation

Use native OpenClaw subagents for short work that should run while the orchestrator continues other tasks.

Recommended fields:

- `agentId`: configured specialist id, e.g. `threads-research`
- `context`: `isolated` by default, `fork` only if the child needs the user transcript
- `cwd`: `<workspace>`
- `mode`: `run`
- `runtime`: `subagent`
- `taskName`: stable snake_case task name
- task text starts with `[Subagent Task]`

The task text must include:

- Owner
- Goal
- Inputs
- Constraints
- Allowed external actions
- Deliverables
- Required report format

## Durable File Delegation

Use durable handoff when work may outlive the current chat turn.

Paths:

- inbox: `<openclaw-home>/departments/inbox/`
- active: `<openclaw-home>/departments/active/`
- done: `<openclaw-home>/departments/done/`
- reports: `<openclaw-home>/departments/reports/`

## Specialist Map

- `threads-research`: X/Twitter/Threads/web signal discovery, topic angles, source verification.
- `threads-writer`: Ukrainian Threads drafts, chains, hooks, CTA, content packages.
- `threads-editor`: quality gates, duplication checks, tone, factual risk.
- `threads-scheduler`: queue/schedule state, Postiz dry-runs, scheduling after approval.
- `threads-analytics`: Postiz/platform analytics snapshots and learnings.
- `threads-learning`: updates content rules based on performance.
- `publishing-ops`: final external publishing/scheduling/reporting through Postiz.
- `memory-curator`: memory capture and archive/promotion work.
- `elevenlabs-calls`: ElevenLabs calls, transcripts, recordings, approved outbound calls.

## Threads Content Flow

1. Main orchestrator creates research task for `threads-research`.
2. `threads-research` reports 3-5 strong topics with evidence.
3. Main chooses topic or asks template owner for approval if needed.
4. Main creates writing task for `threads-writer`, including:
   - `skills/threads-ai-agents-automation-growth/SKILL.md`
   - `skills/threads-viral-news-factory/SKILL.md` when news-led
5. `threads-writer` writes package to `content-factory/threads/runs/`.
6. `threads-editor` validates.
7. Main asks template owner for publishing approval unless already explicitly granted.
8. `publishing-ops` or `threads-scheduler` publishes/schedules through Postiz and writes evidence.

## Automatic Cron Flow

Current daily jobs live in `<openclaw-home>/cron/jobs.json`:

- `daily-ai-agent-trends-review-delivered`: `0 11 * * *` Europe/Kyiv. Daily Threads AI-agent trends autopublish through Postiz after validation. Threads topics must start from X/Twitter signal.
- `daily-facebook-ai-content-factory-review-delivered`: `15 11 * * *` Europe/Kyiv. Daily Facebook `Your Brand` autopublish through Postiz after validation. Visuals must use OpenClaw `image_generate` with model `openai/gpt-image-2`.
- `content-growth-slot-14-delivered`: `0 14 * * *` Europe/Kyiv. Daily second growth slot, creating and autopublishing Threads + Facebook packages through Postiz after validation.
- `content-growth-slot-18-delivered`: `0 18 * * *` Europe/Kyiv. Daily third growth slot, creating and autopublishing Threads + Facebook packages through Postiz after validation.
- `weekly-social-growth-analytics-sunday-delivered`: `0 13 * * 0` Europe/Kyiv. Sunday analytics and strategy correction: reviews the week's Threads/Facebook post performance, writes a weekly analytics report, updates concise learnings, recommends strategy changes for the next week, and sends template owner a Telegram digest.

Architecture rule: scheduled cron jobs must have explicit Telegram delivery (`delivery.mode="announce"`) so successful runs produce visible publishing evidence or blockers. template owner enabled no-approval autopublishing for scheduled Threads/Facebook content-factory jobs on 2026-05-20; this applies only to Postiz publishing after validation. Direct platform fallbacks still require separate approval.

Tool routing rule: if a cron run delegates Facebook visual work, delegate it to `visual-designer` or generate in the main cron session before `publishing-ops`. `publishing-ops` is for Postiz publishing and verification only; it should not generate images.

## Report Format

Every specialist returns:

```text
Status: completed|partial|blocked
Changed:
Evidence:
Blockers:
Next suggested action:
```

## Safety

- No specialist sends Telegram/user-facing replies unless explicitly authorized.
- No publishing, outbound calls, or external writes without current explicit approval and exact scope.
- No token/secret values in reports.
- If unsure, report `blocked` instead of guessing.
