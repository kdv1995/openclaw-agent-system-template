# Quickstart

## 1. Create Your Workspace

```bash
mkdir -p ~/.openclaw/workspace
cp agent-workspace/AGENTS.template.md ~/.openclaw/workspace/AGENTS.md
cp agent-workspace/SOUL.template.md ~/.openclaw/workspace/SOUL.md
cp agent-workspace/USER.template.md ~/.openclaw/workspace/USER.md
cp agent-workspace/TOOLS.template.md ~/.openclaw/workspace/TOOLS.md
cp agent-workspace/HEARTBEAT.template.md ~/.openclaw/workspace/HEARTBEAT.md
cp agent-workspace/MEMORY.template.md ~/.openclaw/workspace/MEMORY.md
```

Edit these files for your identity, timezone, preferred tone, external-action rules, and tools.

## 2. Add Secrets Locally

Create local `.env` files only on your machine:

```bash
cp examples/tg-business-bot-template/.env.example examples/tg-business-bot-template/.env
```

Never commit `.env`, tokens, private keys, customer exports, call recordings, or platform state.

## 3. Use Specialist Handoffs

Create a task file in `departments/inbox/` with:

- owner;
- goal;
- inputs;
- constraints;
- allowed external actions;
- deliverables;
- evidence required;
- blocker reporting format.

Move accepted work to `departments/active/` and final reports to `departments/reports/`.

## 4. Start With an Example System

Use `systems/lead-to-landing-os/` for a business lead pipeline or `systems/social-growth-os/` for content operations.

Keep real campaign state outside the template repo.
