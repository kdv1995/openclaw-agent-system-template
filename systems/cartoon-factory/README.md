# Cartoon Factory

Project-level factory for producing short animated episodes with stable characters, controlled voice direction, scene timing, transitions, music, sound effects, and QA.

This is not a Telegram bot feature. It is an OpenClaw workspace production system.

## Stack

- Character images and visual references: ChatGPT Images 2.0 / OpenClaw GPT image route
- Video generation: Gemini Video Generation Tool
- Voice and sound effects: ElevenLabs
- Music: approved music generation route
- Orchestration: OpenClaw main orchestrator with specialist handoffs

## Core Principle

Every episode is a production package, not a single prompt. The factory must preserve character identity, voice identity, timing, transitions, and story quality across all generated assets.

## Folder Map

- `show-bible.md` - global rules for world, style, story, tone, and quality.
- `STACK.md` - fixed tool stack and tool-specific constraints.
- `characters/` - canonical character profiles and image reference packs.
- `voices/` - ElevenLabs voice maps, delivery rules, and pronunciation notes.
- `style-guide/` - visual rules, camera language, transitions, subtitles, music, and SFX.
- `episode-template/` - reusable package structure for each new episode.
- `episodes/` - active and completed episode packages.
- `qa/` - quality checklists and continuity review templates.
- `runbooks/` - operating procedures for creating and reviewing episodes.

## MVP Target

Start with a 45-60 second episode. The first test should prove:

- the same character remains visually stable across 5-7 scenes;
- voice timing matches scene timing;
- transitions feel intentional rather than randomly stitched together;
- the first 3 seconds create a clear hook;
- the final beat lands cleanly.
