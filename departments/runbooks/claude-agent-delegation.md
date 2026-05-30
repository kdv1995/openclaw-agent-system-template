# Claude Agent Delegation

Status: active.

## Purpose

Expose Claude agent markdown profiles from a local Claude agents directory, such as `~/.claude/agents`, as callable OpenClaw subagents without replacing the existing OpenClaw specialist system.

## Registry

- JSON catalog: `departments/agent-catalog/claude-agents-catalog.json`
- Markdown catalog: `departments/agent-catalog/claude-agents-catalog.md`
- Runtime ids: `claude-<source-file-slug>`
- Imported count: 147

## Delegation Pattern

Use these agents only through the main orchestrator. Choose an imported Claude agent when the request matches a catalog role and no existing OpenClaw specialist owns the work more directly. Existing OpenClaw specialists remain the default for the operator's operational systems such as publishing ops, memory, calls, lead-to-landing, QA, CRM, and analytics.

For short work, spawn a native OpenClaw child session with:

- `agentId`: one of the `claude-*` ids from the catalog
- `context`: `isolated` unless conversation history is required
- `cwd`: `~/.openclaw/workspace`
- task text starting with `[Subagent Task]`

Include owner, goal, inputs, constraints, allowed external actions, deliverables, and the standard report format.

## Safety

Imported Claude agents are configured with no message sending, no cron/gateway/browser, and no image/video generation by default. If a task needs external access or a richer tool profile, the orchestrator should either handle that directly, use an existing trusted OpenClaw specialist, or update the specific imported agent deliberately with a config backup.

## Verification

After config edits, run:

```bash
jq empty ~/.openclaw/openclaw.json
node ~/.openclaw/workspace/scripts/check-openclaw-architecture.mjs
```
