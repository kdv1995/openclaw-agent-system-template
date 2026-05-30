# Capabilities

## Main Orchestrator

- Maintains the direct user conversation.
- Decides whether to work locally or delegate.
- Converts vague requests into bounded tasks.
- Verifies specialist reports before telling the user something is done.
- Keeps memory and operational notes in files.

## Specialist Agents

- `lead-qualifier`: prepares lead batches and filters invalid or duplicate records.
- `calls-agent`: handles approved outbound call workflows and evidence reports.
- `business-researcher`: performs public business research before landing page work.
- `ui-ux-designer`: designs conversion-first landing structure and copy flow.
- `visual-designer`: creates visual direction and asset briefs.
- `full-stack-developer`: implements approved landing pages and local verification.
- `seo-optimizer`: audits metadata, local SEO, schema, tracking, and conversion signals.
- `publishing-ops`: handles social publishing batches and evidence.
- `memory-curator`: maintains daily notes and long-term memory hygiene.

## Example Systems

### Lead-to-Landing OS

Pipeline:

```text
lead-qualifier -> calls-agent -> business-researcher -> ui-ux-designer -> visual-designer -> full-stack-developer -> seo-optimizer
```

Use it to turn qualified leads into researched landing pages with implementation and SEO handoff.

### Social Growth OS

Pipeline:

```text
trend scout -> profile context -> idea strategy -> scriptwriting -> creative direction -> platform adaptation -> publishing -> analytics -> learning
```

Use it to run repeatable content production with clear stage ownership.

### Content Factory

Threads/Facebook content skeleton with research, writing, validation, Postiz payload examples, analytics helpers, and safety rules. Real runs, queues, state, generated media, and platform responses are intentionally excluded.

### eBay Watch

Configurable marketplace monitor for eBay Browse API searches. It supports category/query filters, price ranges, condition filters, excluded/required keywords, scoring, deduplication, Markdown/JSON reports, and optional Telegram digest delivery.

### Cartoon Factory

Production handoff system for short cartoon/video packages: episode brief, beat sheet, script, keyframe prompts, voice script, SFX/music map, timing, edit plan, and QA checklists.

### Telegram Business Bot

Includes a Docker-based Python bot template with PostgreSQL, segmentation questions, consultation CTA, and follow-up scaffolding.
