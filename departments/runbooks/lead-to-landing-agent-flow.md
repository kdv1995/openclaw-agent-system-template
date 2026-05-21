# Lead to Landing Agent Flow

## Purpose

Run a controlled pipeline from Google Sheets leads and approved outbound calls to researched landing-page creation.

## High-Level Flow

```text
template owner approval/scope
  -> lead-qualifier
  -> calls-agent
  -> interested?
      no  -> update status/report
      yes -> business-researcher
          -> ui-ux-designer
          -> visual-designer
          -> full-stack-developer
          -> seo-optimizer
          -> main orchestrator report
```

## Agents

- `lead-qualifier`: chooses rows from approved scope, removes duplicates/invalids, prepares call angles.
- `calls-agent`: calls only approved rows/batch, one by one, with transcripts/audio/status updates.
- `business-researcher`: researches interested businesses using public sources and call context.
- `ui-ux-designer`: creates conversion-first landing UX spec.
- `visual-designer`: creates visual direction and assets; landing images use GPT image model 2.0 through the subscribed ChatGPT/OpenClaw route.
- `full-stack-developer`: builds the landing page from approved specs.
- `seo-optimizer`: audits metadata, structure, local SEO, analytics, and conversion tracking.

## Required Scope Before Calls

The orchestrator must provide:

- sheet/source path or Google Sheets reference
- exact rows/batch
- caller number
- call purpose
- script/offer
- stop conditions

Default caller number for lead calls: `APPROVED_CALLER_ID`.

## Interested Lead Handoff

A lead can move to landing flow when:

- transcript/status says interested
- template owner manually marks it as interested
- lead explicitly asks for next step

The handoff package must include:

- business name
- contact/source
- category/location
- call transcript path
- call summary
- objections/questions
- promised next action

## Visual Rule

For landing work, generated images must use GPT image model 2.0 through the subscribed ChatGPT/OpenClaw image route. Do not use the legacy OpenAI API image CLI path unless template owner explicitly changes this rule.

## External Action Boundaries

- Calling: allowed only inside explicit approved scope.
- Deployment: requires explicit task permission for target environment.
- Client messages/emails: require explicit approval.
- Public publishing: requires explicit approval.
- Local specs/reports/code drafts: allowed.

## Report Contract

Every stage reports:

```text
Status: completed|partial|blocked
Changed:
Evidence:
Blockers:
Next suggested action:
```
