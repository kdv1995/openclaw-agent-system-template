# Stage Task: Learning Curator

## Agent brief
`<workspace>/social-growth-os/agents/09-learning-curator.md`

## Goal
Convert performance results into durable learnings and next experiments.

## Inputs
- Run folder: `runs/<run_id>/`
- Config: `orchestrator.yaml`
- Previous stage outputs from the same run folder

## Deliverables
state/learnings.md

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
