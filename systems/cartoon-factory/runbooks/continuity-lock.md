# Runbook: Continuity Lock

## Purpose

Prevent character drift between images, video clips, voice tracks, and final edit.

## Before Scene Generation

Confirm:

- character card exists;
- approved reference images exist;
- outfit and colors are copied into the prompt;
- action does not require changing identity;
- camera framing keeps identity visible;
- previous scene ending pose is considered.

## Prompt Requirements

Every Gemini scene prompt must include:

- character name;
- approved reference asset path or ID;
- exact outfit;
- core colors;
- body proportions;
- face identity lock;
- scene-specific action;
- camera movement;
- start and end pose;
- negative constraints.

## After Scene Generation

Reject or regenerate if:

- face identity changed;
- outfit changed;
- character age changed;
- style changed;
- transition breaks the previous scene;
- important action is unclear.
