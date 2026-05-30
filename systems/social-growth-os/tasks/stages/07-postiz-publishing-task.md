# Stage Task: Publishing Ops / Postiz

## Agent brief
`systems/social-growth-os/agents/07-publishing-ops-postiz.md`

## Goal
After owner approval, upload approved media, create/schedule posts in Postiz, and verify IDs/status.

## Inputs
- Run folder: `runs/<run_id>/`
- Config: `orchestrator.yaml`
- Previous stage outputs from the same run folder

## Deliverables
publishing_report.md

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
