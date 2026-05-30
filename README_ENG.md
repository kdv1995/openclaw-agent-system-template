# OpenClaw Agent System Template

Sanitized starter kit for building a personal AI operations workspace on top of OpenClaw-style agents, skills, runbooks, and specialist delegation.

This repository is a template. It intentionally does not include private memory, live state, credentials, customer files, logs, generated media, tokens, or production exports.

## What This System Can Do

- Run a main personal orchestrator with durable workspace memory.
- Route bounded work to specialist agents through written task handoffs.
- Manage lead-to-landing workflows: lead filtering, calls, business research, UX, visuals, implementation, SEO.
- Operate content/social publishing pipelines with separate research, writing, adaptation, publishing, analytics, and learning stages.
- Monitor marketplace categories through a configurable eBay Watch service with scoring, deduplication, and optional Telegram digests.
- Structure cartoon/video production packages with script, storyboard, voice, motion, and QA handoffs.
- Build Telegram bot prototypes with PostgreSQL, Docker, segmentation flows, and follow-up logic.
- Keep repeatable runbooks for agent-to-agent communication, safety boundaries, and reporting.
- Use skills as portable operational knowledge for design, SEO, security, browser automation, image generation, transcription, publishing, and more.

## Repository Layout

```text
agent-workspace/          Core identity, memory, and tool note templates.
departments/              Durable handoff folders and orchestration runbooks.
specialists/              Specialist agent skill packs.
systems/                  Example multi-agent operating systems.
examples/                 Example app templates, including a Telegram business bot.
skills/                   Reusable local OpenClaw skills.
docs/                     Setup, capabilities, and security guidance.
prompts/                  Ready-to-use prompt templates for orchestrator and specialist workflows.
```

## Quick Start

1. Install OpenClaw and any local tools your setup needs.
2. Copy `agent-workspace/*.template.md` into your active workspace and rename them to `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `HEARTBEAT.md`, and `MEMORY.md`.
3. Fill in your own identity, timezone, preferences, tool notes, and safety rules.
4. Add credentials only through local `.env` files or your secrets manager. Never commit real credentials.
5. Use `departments/inbox/` for new delegated tasks and `departments/reports/` for specialist results.
6. Start with `systems/lead-to-landing-os/`, `systems/social-growth-os/`, `systems/content-factory/`, or `systems/ebay-watch/` as examples of larger agent workflows.

## Safety Model

The template uses a strict separation:

- public template files: instructions, examples, runbooks, skill docs;
- private runtime files: `.env`, memory, live state, logs, media, transcripts, customer data;
- external actions: publishing, outbound calls, email, and deploys require explicit human approval unless a durable config says otherwise.

See [docs/SECURITY.md](docs/SECURITY.md) before adapting this for production.

## Not Included

This export deliberately excludes:

- `.env` files and API tokens;
- personal memory files;
- Telegram, Google, Meta, Postiz, ElevenLabs, and GitHub credentials;
- generated media and archives;
- live state from real campaigns;
- customer/lead datasets;
- call transcripts, recordings, and logs.

## License

Add your own license before public reuse.
