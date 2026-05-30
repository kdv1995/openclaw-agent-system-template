# Design Quality Skill Routing

Status: active.

## Purpose

Use `ui-ux-pro-max` and `superdesign` together as the default design intelligence and quality workflow for landing pages, dashboards, app UI, visual directions, and frontend implementation.

Installed shared skill:
`workspace/skills/ui-ux-pro-max/SKILL.md`

Installed workflow skill:
`workspace/skills/superdesign/SKILL.md`

Agent-local copies:
- `ui-ux-designer`: `workspace/ui-ux-designer/skills/ui-ux-pro-max/SKILL.md`
- `visual-designer`: `workspace/visual-designer/skills/ui-ux-pro-max/SKILL.md`
- `full-stack-developer`: `workspace/full-stack-developer/skills/ui-ux-pro-max/SKILL.md`
- `ui-ux-designer`: `workspace/ui-ux-designer/skills/superdesign/SKILL.md`
- `visual-designer`: `workspace/visual-designer/skills/superdesign/SKILL.md`
- `full-stack-developer`: `workspace/full-stack-developer/skills/superdesign/SKILL.md`

## When Orchestrator Should Require It

Require `ui-ux-pro-max` when a task involves:
- landing-page UX structure
- website/app/dashboard visual design
- component styling
- color palette or typography decisions
- conversion layout
- mobile responsiveness
- UI polish or redesign
- frontend implementation of visible UI
- pre-delivery UI/UX QA

Skip it for:
- backend-only work
- database/API tasks
- infrastructure
- non-visual scripts
- copy-only tasks

## Routing

Use native OpenClaw specialists first:
- UX structure and conversion flow: `ui-ux-designer`
- visual direction and asset prompts: `visual-designer`
- implementation and responsive verification: `full-stack-developer`
- final UI/UX verification: `qa-agent`

Use imported Claude agents only for narrow expert help when native specialists do not cover the task:
- `claude-design-ui-designer`
- `claude-design-ux-architect`
- `claude-engineering-frontend-developer`

When delegating to an imported Claude design/frontend agent, explicitly include:
`Use ~/.openclaw/workspace/skills/ui-ux-pro-max/SKILL.md as the design quality reference.`

## Minimum Quality Gate

Before reporting completion on visible UI, the responsible agent must include evidence for:
- layout workflow: ASCII wireframe or equivalent component map
- selected product/style direction
- color/typography rationale
- theme tokens or implementation variables
- animation/micro-interaction plan where relevant
- mobile and desktop layout behavior
- accessibility basics: contrast, focus, labels, touch targets
- anti-patterns avoided
- verification performed, such as screenshot review, Playwright check, or local preview

## Useful Commands

Search product/design recommendations:

```bash
python3 ~/.openclaw/workspace/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain product -n 5
```

Search UI style recommendations:

```bash
python3 ~/.openclaw/workspace/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain style -n 5
```

Search stack-specific guidance:

```bash
python3 ~/.openclaw/workspace/skills/ui-ux-pro-max/scripts/search.py "<query>" --stack nextjs -n 5
```
