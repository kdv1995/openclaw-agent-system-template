# Content Factory System

Portable social/content workflow skeleton for OpenClaw.

This template includes:

- Threads factory agents, schemas, validation scripts, and Postiz payload examples.
- Facebook image-post workflow agents and editorial rules.
- Meta analytics helper scripts.
- Postiz verification helper.

It intentionally excludes:

- real run folders
- queue/state files
- platform tokens
- Postiz raw responses
- generated media
- private analytics reports

## Setup

1. Copy only the pieces you need into your workspace.
2. Put secrets in a local `.env` or secret manager, never in Git.
3. Keep generated runs under ignored `runs/`, `state/`, `reports/`, or `tmp/`.
4. Require explicit approval before publishing unless your workspace config defines a durable autopublishing rule.
