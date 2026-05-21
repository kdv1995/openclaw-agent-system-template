# Stage Task: Analytics Analyst

## Agent brief
`<workspace>/social-growth-os/agents/08-analytics-analyst.md`

## Goal
Collect metrics at 24h/48h/72h/7d and classify posts.

## Inputs
- Run folder: `runs/<run_id>/`
- Config: `orchestrator.yaml`
- Previous stage outputs from the same run folder

## Deliverables
analytics_report.md

## Report format
```markdown
Status: completed|blocked|partial
Inputs used:
- ...
Outputs written:
- ...
Evidence:
- ...
Blockers:
- none / ...
Next action:
- ...
```

## Safety
Do not print secrets. Do not publish externally unless this is the Postiz stage and owner approval is present in the run folder.
