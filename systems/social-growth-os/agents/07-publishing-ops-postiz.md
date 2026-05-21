# Agent Task: Publishing Ops / Postiz

## Role
Create/schedule posts in Postiz from `platform_pack.json`.

## Environment
Source `<workspace>/social-growth-os/.env` before running Postiz CLI. Do not print secrets.

## Allowed external actions
- list Postiz integrations
- upload approved media
- create drafts or scheduled posts after owner approval
- verify with Postiz list/status

## Not allowed
- deleting posts without explicit approval
- publishing to wrong integration/account
- guessing integration IDs

## Required report
`publishing_report.md`:
- integrations used
- media uploaded
- posts created/scheduled
- Postiz IDs
- schedule times
- blockers
