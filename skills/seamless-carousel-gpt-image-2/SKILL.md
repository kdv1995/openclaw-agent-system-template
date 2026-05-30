---
name: "seamless-carousel-gpt-image-2"
description: "Create seamless social carousel images with GPT Image 2.0 backgrounds and exact local text overlays."
---

# Seamless Carousel GPT Image 2.0

Use when the operator asks for seamless/swipeable carousels for Threads, Instagram, TikTok, or Facebook.
This is the mandatory default skill for the operator's carousel generation workflow: if the task is to create a carousel, route through this skill unless the operator explicitly asks for a different method.
Use the tested "AI agent carousel" format by default when he asks to make carousels for his personal AI/automation content.
The canonical creative style is the "business loss must not die in chat" format: a bold, direct, painful business statement in huge Ukrainian poster type, backed by a clean AI/operator-system visual. Treat this as the operator's default creative style for carousels and adjacent social creatives.

## Brand Source Of Truth

Use `<brand-docs>/docs/BRAND.md` as the primary brand reference for the operator's personal-brand carousels.

Core tokens:

- Brand: `Код Без Меж / Code Without Borders`.
- Canvas: `1080x1350` portrait social slides by default.
- Palette: `#F7F5F2` paper, `#141414` ink, `#0A0A0A` black, `#E40914` red, `#FFFFFF` white.
- Display type: `Unbounded 900` for every major visible carousel text element. This matches the operator's approved "ЛІД НЕ ЧЕКАЄ / ТВОЮ ПАУЗУ" reference and the personal-brand source of truth.
- Hard typography lock: carousel text must read as bold poster type, not thin editorial type. If a generated or rendered slide looks visually light, narrow, subtle, or secondary, treat it as failed and re-render with larger `Unbounded 900`.
- Supporting type: keep visible carousel overlays inside the approved brand system: Unbounded 900 for display/counters/CTA emphasis, Inter only for short explanatory body lines, JetBrains Mono only for tiny metadata/eyebrows, and Space Grotesk only for button-like CTA chrome.
- Slide rule: one large display size plus one small supporting size per slide. Do not stack 3+ text sizes.
- Use red as a single decisive accent: one word, one rail, one node, one CTA marker. Avoid multi-accent palettes.
- Default light format: paper background, ink type, red accent rail/dot/keyword.
- Statement format: ink background, paper/white type, red accent word.
- Climax CTA format: red background, white type, optional white knock-out word.

Brand constraints:

- Do not use pure white as the main background unless the slide is intentionally inverted.
- Do not use blue/purple sci-fi gradients, neon, robots, crypto/gaming UI, or cold generic SaaS stock styling.
- Keep phone-feed readability above decorative detail.
- Add all Ukrainian/English text locally. GPT Image backgrounds must not contain readable text.

## Output Goal

- Generate a sequence of standalone carousel slides that visually hand off from one slide to the next.
- Use the previous slide as the visual reference for the next slide, instead of slicing one wide panorama.
- Keep continuity through repeated objects, lines, interface rails, lighting, palette, and edge-to-edge visual hooks.
- Add all important text locally after generation so Ukrainian copy stays exact and readable.
- Default brand palette: paper, ink, black, red, white from `BRAND.md`.
- Default model route: OpenClaw `image_generate` with `model: openai/gpt-image-2`.

## Tested Default Format

This was tested with the operator on 2026-05-23 and should be the default for professional carousel experiments:

- 3 slides by default: `hook -> mechanism/reveal -> CTA/payoff`.
- Format: vertical `4:5` social slide, exported as `1024x1536` or higher, not tiny square drafts.
- Image generation: make backgrounds only with GPT Image 2.0; no readable generated text inside the image.
- Typography: add all text locally after generation with `Unbounded 900` for the large poster text. Do not use Outbound for the operator's carousels.
- Text scale: very large, phone-readable from the feed. If it feels subtle on desktop, it is too small for Instagram and must be re-rendered.
- Minimum poster scale: slide-1 hooks and final CTAs should normally occupy 55-75% of the slide width and 30-55% of the slide height. Do not accept small centered captions, thin titles, light weights, or polite H2-style typography for feed hooks.
- Poster headline rule: use the exact visual standard from the operator's approved reference sent on 2026-05-23: square, heavy `Unbounded 900`, uppercase, 2-4 tight lines, near full-width, line-height around 0.82-0.92, negative tracking around `-0.035em` to `-0.045em`, and strong black/red/knock-out contrast.
- Bold headline default: every new carousel should use this heavy poster headline treatment unless the operator specifically asks for a softer layout. The headline must be the first thing the eye catches in the feed.
- First-slide headline priority: the text must be the dominant visual object. Background UI/details support the headline and must never compete with it.
- Layout: large negative space on upper-left/center-left for text; visual system mostly center-right/lower-right.
- Visual language: premium SaaS/editorial, Swiss-inspired layout, warm paper/off-white, deep ink/black, vivid red accents, crisp shadows.
- Story handoff: use a red interface rail/line entering from the left and exiting to the right until the last slide.
- CTA: final slide must include a clear action and can use the keyword `агент` when the conversion mechanic is Telegram/comment DM.

## Canonical Creative Pattern

Default to this style when the operator says "our style", "креативи", "карусель", "зроби щоб продавало", or gives a business pain:

- Core idea: `ТВОЇ <цінність/ліди/заявки/гроші/клієнти> НЕ МАЮТЬ ВМИРАТИ В <хаосі/чаті/таблицях/директі/ручних процесах>.`
- Tone: direct founder/operator pain, not generic AI education.
- Visual promise: the operator builds an operating layer that catches the business event, routes it, reminds people, pings the right person, and keeps the process alive.
- Slide 1: one painful statement, maximum type scale, one red emotional/action word or phrase.
- Slide 2: show the mechanism in one sentence: agent catches, filters, assigns, reminds, escalates, or prepares next action.
- Slide 3: business payoff plus CTA: fewer lost leads, less chaos, faster response, visible control; CTA can ask to write `АГЕНТ`, `БОТ`, or a topic-specific keyword.
- Keep it conversational and concrete. Avoid abstract promises like "AI transformation", "digitalization", "future of work", or "automation ecosystem" unless the caption explains them through a real business pain.

Strong hook formulas:

1. `ТВОЇ ЛІДИ НЕ МАЮТЬ ВМИРАТИ В ЧАТІ.`
2. `ТВОЇ ЗАЯВКИ НЕ МАЮТЬ ЛЕЖАТИ БЕЗ ВІДПОВІДІ.`
3. `ТВОЇ ГРОШІ НЕ МАЮТЬ ЗАСТРЯГАТИ В ХАОСІ.`
4. `ТВОЯ КОМАНДА НЕ МАЄ ПАМ'ЯТАТИ ВСЕ ВРУЧНУ.`
5. `БІЗНЕС НЕ МАЄ ТРИМАТИСЯ НА "Я ЗАБУВ".`

This pattern should be used across carousels, Facebook image posts, Threads visuals, TikTok covers, and sales creatives unless the operator explicitly asks for another format.

### Tested AI Agent Slide Copy Pattern

Use this copy shape unless the operator gives a stronger one:

1. Hook: `ТВОЇ ЛІДИ НЕ ГУБЛЯТЬСЯ. ЇХ ГУБИТЬ ХАОС.`
2. Mechanism: `АГЕНТ ЛОВИТЬ ЗАЯВКУ, ФІЛЬТРУЄ І ГОТУЄ НАСТУПНИЙ КРОК.`
3. CTA: `НАПИШИ "АГЕНТ" - ПОКАЖУ, ЯК ЦЕ ПРАЦЮЄ.`

Keep slide text direct and high-contrast. Do not use paragraphs on the image; put nuance in the caption.

## Dark Format Variant

Use this when the operator asks for the dark format, more dramatic business/AI visuals, or a stronger premium look:

- Background: `#141414` ink or `#0A0A0A` black canvas, not blue/purple sci-fi.
- UI elements: `#F7F5F2` paper cards, graphite panels, vivid `#E40914` red accent rail, restrained shadows/glow.
- Typography: Unbounded 900 in paper/white; red only for one emphasis word or CTA marker.
- Keep the same 3-slide logic and local text overlay workflow.
- Avoid neon, robots, holograms, cyberpunk, and unreadable small text.
- The dark version should still feel like expensive SaaS/editorial design, not a gaming or crypto template.

## Workflow

1. Define the carousel story in 3-7 beats.
2. Generate slide 1 as a complete standalone composition with no readable text, no logos, no watermarks.
3. Make slide 1 include a clear visual handoff that exits the right edge: line, cable, UI rail, object, glow, or motion path.
4. Generate slide 2 using slide 1 as the reference image. Continue the handoff from the left edge and create a new handoff exiting the right edge.
5. Repeat until the final slide. The final slide resolves the visual path and leaves space for a CTA.
6. Overlay exact local text on every slide. Do not rely on GPT Image for Ukrainian text.
7. Inspect every slide before publishing: hook strength, text readability, edge continuity, contrast, safe margins, and CTA clarity.
8. Send the PNG slides as Telegram attachments for review unless the operator explicitly approved publishing.

## Legacy Panorama Mode

Only use a single wide image sliced into slides for fast low-stakes tests or if the operator explicitly asks for a panoramic crop.
Do not use panorama slicing for production posts by default; it tends to produce weak slide-by-slide storytelling.

## Prompt Pattern

Use this structure for slide 1:

```text
Create slide 1 background for a premium <N>-slide seamless carousel about <topic>.
Format: <aspect ratio> social slide.
This is a standalone first slide, not a slice of a panorama.
Visual beat: <beat one>.
Include a strong visual handoff that exits the right edge so slide 2 can continue it.
No humanoid robots. No logos. No readable text, no letters, no numbers, no watermarks.
Leave generous negative space for large Ukrainian overlay text to be added later.
```

Use this structure for middle slides:

```text
Create slide <K> background for the same premium seamless carousel.
Use the provided previous slide as visual reference.
Continue the line/object/UI rail entering from the left edge, evolve the story into <beat K>,
and create a new visual handoff exiting the right edge.
Keep the same black/red/white palette, lighting, depth, and interface style.
No humanoid robots. No logos. No readable text, no letters, no numbers, no watermarks.
Leave generous negative space for local overlay text.
```

Use this structure for the final slide:

```text
Create final slide background for the same premium seamless carousel.
Use the provided previous slide as visual reference.
Continue the visual handoff from the left edge and resolve it into <final outcome>.
Leave a strong CTA text area and a clear action/focus object.
No humanoid robots. No logos. No readable text, no letters, no numbers, no watermarks.
```

## Text Rules

- Mandatory font rule: carousel headlines, red emphasis words, large counters, slide numbers, and CTA emphasis use `Unbounded 900`. This is the standard from the approved "ЛІД НЕ ЧЕКАЄ / ТВОЮ ПАУЗУ" reference. Never use `Outbound` for the operator's carousel overlays.
- Thin-font ban: never use thin, regular, light, medium, condensed-looking, delicate, or low-contrast text for carousel hooks, claims, counters, or CTAs. This includes visually thin output even if the prompt says "bold". If the visible result is not heavy, it fails review.
- Big-font requirement: main slide text must be poster-large, uppercase, blocky, and dominant. Default target size for 1080x1350 overlays is roughly 115-180px for hooks, adjusted only to prevent clipping; final CTA should use similarly large display type.
- Supporting text rule: short explanatory body lines may use Inter from `BRAND.md`; tiny metadata/eyebrows may use JetBrains Mono; button/chrome CTA labels may use Space Grotesk. Do not introduce Arial, system UI, or unrelated fallback fonts.
- One strong line per slide.
- Short words, large type, high contrast.
- Avoid tiny paragraphs inside the image.
- For hooks, prefer oversized poster typography: black first claim, red emotional/action phrase, optional black rectangle with paper/white knock-out word. This format has priority over restrained H2 sizing when the goal is attention in feed.
- Use caption/post text for nuance.
- Put the strongest hook on slide 1.
- Make each slide force the next swipe: hook -> mechanism -> payoff/CTA.
- Use the same bold display font across all slides to preserve the seamless carousel identity from first to last slide.
- Prefer uppercase for hooks and CTAs in this format.
- Keep safe margins generous; text should not touch edges or busy UI elements.

## Typography QA Gate

Before sending or scheduling any carousel slide for the operator, inspect it at phone-feed scale and reject it unless all are true:

- The main text is clearly `Unbounded 900` or an equally heavy local display render.
- The hook/CTA is the dominant object on the slide, larger than the background interface/visual motif.
- No important selling line uses thin, light, regular, or subtle typography.
- The first slide can be understood in under one second from a small preview.
- Red emphasis is bold and intentional, not a thin accent label.

If any check fails, regenerate or re-render the text overlay before delivery. Do not ask the operator to catch this manually.

## Layout Defaults

- 3-slide default: generate three separate `4:5` slides using the previous slide as reference.
- Instagram feed carousel: export square or 4:5 only after visual review.
- Threads/TikTok repost: use the same slides, but keep caption native to platform.

## Safety

- Do not publish externally without explicit approval.
- If generated text appears in the image, regenerate or crop it out.
- If GPT Image 2.0 route is unavailable, mark blocked instead of using the legacy local OpenAI API route unless the operator approves.
