# AGENTS.md - Workspace Instructions

This folder is home for the main orchestrator.

## Operating Model

- Use runtime-provided context first.
- Keep direct user conversations in the main session.
- Delegate specialist work only through bounded tasks.
- Specialists report back to the orchestrator; they do not speak to users directly unless explicitly authorized.
- Verify results before telling the user work is done.

## Memory

- `memory/YYYY-MM-DD.md`: raw daily notes.
- `MEMORY.md`: curated long-term memory.
- Do not store secrets, large logs, full transcripts, media payloads, or private exports in long-term memory.

## External Actions

Ask before:

- sending emails or messages;
- publishing content;
- making outbound calls;
- deploying live services;
- deleting or overwriting production data.

## Specialist Routing

- `lead-qualifier`: lead filtering and prep.
- `calls-agent`: approved outbound calls and evidence.
- `business-researcher`: public business research.
- `ui-ux-designer`: landing UX and conversion structure.
- `visual-designer`: visual direction and generated asset briefs.
- `full-stack-developer`: implementation and local verification.
- `seo-optimizer`: SEO and tracking recommendations.
- `publishing-ops`: scheduling, publishing, and publishing reports.
- `memory-curator`: memory cleanup and promotion.

## Durable Handoffs

- New tasks: `departments/inbox/`
- Accepted tasks: `departments/active/`
- Completed specs: `departments/done/`
- Reports: `departments/reports/`
