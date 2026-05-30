# Lead to Landing OS

Operational pipeline for turning qualified outbound leads into researched landing-page projects.

The main orchestrator owns the operator communication, scope control, and final verification. Specialist agents work on bounded tasks and report back with evidence.

## Default Flow

1. `lead-qualifier` selects and prepares leads from the approved Google Sheets scope.
2. `calls-agent` calls only the approved rows/batch, saves transcript/audio/status, and updates the lead record.
3. If the lead is interested, `business-researcher` researches the business and extracts missing context.
4. `ui-ux-designer` turns the offer, audience, and research into a landing-page structure and UX spec.
5. `visual-designer` creates landing visual direction and image prompts/assets. Landing images must use GPT image model 2.0 through the subscribed ChatGPT/OpenClaw image route, not the legacy OpenAI API CLI path.
6. `full-stack-developer` builds or updates the landing page from the approved UX/design spec.
7. `seo-optimizer` audits the page, keywords, technical SEO, metadata, analytics readiness, and conversion tracking.
8. Main orchestrator verifies outputs and reports next action to the operator.

## Safety

- Outbound calls require explicit approved scope: sheet name/range/rows, caller number, purpose, and script.
- Public publishing, sending emails, live deploys, and destructive CRM changes require explicit task permission.
- Agents do not message the operator directly unless the task explicitly says so.

## Paths

- agent specs: `lead-to-landing-os/agents/`
- new tasks: `lead-to-landing-os/tasks/inbox/`
- active tasks: `lead-to-landing-os/tasks/active/`
- done tasks: `lead-to-landing-os/tasks/done/`
- run outputs: `lead-to-landing-os/runs/`
- reports: `lead-to-landing-os/reports/`
- state/learnings: `lead-to-landing-os/state/`
