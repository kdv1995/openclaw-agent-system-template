---
name: business-video-production
description: Use when creating short vertical business videos/reels for the operator from a business pain, content-factory post, or OpenClaw/AI-agent scenario. Applies to scripting, shot planning, production assembly, QA, and Telegram delivery.
---

# Business Video Production

## Default Output

- Format: vertical 9:16, 1080x1920 minimum, 30fps, H.264 + AAC MP4.
- Style: premium video-first production, not a slideshow and not an infographic reel.
- Duration: usually 35-45 seconds unless the operator specifies otherwise.
- Language: Ukrainian by default.
- Delivery: send final MP4 in Telegram with a short QA note and local file path.

## Default Production Stack

- Use GPT Image 2.0 / ChatGPT Images 2.0 through the operator's subscription for still images, reference frames, keyframes, and carousel-like visuals.
- Use Higgsfield for actual motion/video clip generation and animation. Prefer the configured Higgsfield MCP route when available; use the Higgsfield CLI only when the operator explicitly approves or the task context already authorizes CLI fallback.
- Do not silently substitute generic non-Higgsfield `video_generate`/`image_generate` routes for a Higgsfield task. If Higgsfield MCP/CLI is unavailable, report the blocker before continuing.
- Use ElevenLabs/sag for Ukrainian voiceover and SFX/audio assets when needed.
- Assemble, trim, mix, and QA the final vertical MP4 locally with a controllable timeline/render tool such as ffmpeg, Remotion, HyperFrames, or an equivalent local pipeline.

## Creative Rules

- Start from one concrete business pain, not a broad AI topic.
- Build a human story arc: visible pressure -> specific failure -> system intervention -> controlled next action.
- Every scene needs motion, action, consequence, or emotional reaction. UI can support the story but cannot be the whole story.
- Avoid talking-head/lip-sync unless the face/voice identity is intentionally produced and reviewed.
- Use male/narrator voiceover when the request implies the operator-style business content and no other voice is specified.
- Keep OpenClaw/AI positioned as process control: catches drops, assigns, reminds, escalates, prepares next actions, asks approval where money/terms/reputation are involved.

## No-Subtitles Default

- Do not add caption subtitles by default.
- Do not add a lower CTA text line on the final frame by default.
- On-screen text is allowed only as sparse production overlay: hook, risk label, system state, or final keyword.
- If the operator asks for a clean cut, remove caption overlays and verify the last frame has no accidental subtitle/CTA residue.

## Scenario Structure

Use this compact structure before production:

1. **Назва**: short Ukrainian title.
2. **Біль**: one sentence describing the business pain.
3. **Гачок**: first 1-2 seconds, readable on phone.
4. **Сцени**: 4-6 beats with time ranges, visual action, and voiceover idea.
5. **CTA**: one keyword, only if needed.

## QA Checklist

- Video exists and plays.
- Duration matches target.
- 1080x1920 vertical, no accidental horizontal crop.
- Audio exists and is synced.
- First 2 seconds communicate the pain.
- Last frame has no unwanted subtitles or lower CTA line.
- No random stock-like filler, neon robot imagery, or UI-only scene where a human consequence is needed.
