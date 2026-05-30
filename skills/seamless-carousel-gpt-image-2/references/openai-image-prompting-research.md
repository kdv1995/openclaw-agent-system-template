# OpenAI Image Prompting Research

Research date: 2026-05-23.

Primary sources:

- OpenAI API image generation docs: https://platform.openai.com/docs/guides/image-generation/
- OpenAI Cookbook GPT Image 1.5 prompting guide: https://developers.openai.com/cookbook/examples/multimodal/image-gen-1.5-prompting_guide
- OpenAI Cookbook generate images with GPT Image: https://developers.openai.com/cookbook/examples/generate_images_with_gpt_image
- OpenAI Cookbook image evals: https://developers.openai.com/cookbook/examples/multimodal/image_evals
- OpenAI ChatGPT Images help: https://help.openai.com/en/articles/11084440-images-in-chatgpt

## Findings For Carousel Work

The strongest pattern for carousels is a structured prompt, not a short aesthetic phrase.

Use this order:

1. Role/output: what slide this is and what it is for.
2. Format: aspect ratio, standalone slide, platform, resolution intent.
3. Story beat: what this slide communicates.
4. Composition: where the main objects go and where text space must remain.
5. Style system: medium, palette, lighting, hierarchy, depth, texture.
6. Continuity: what enters/exits edges and what must match the previous slide.
7. Constraints: no text/logos/watermarks, preserve layout/style, avoid unwanted genres.
8. Quality gates: readable on phone, premium/editorial, not cluttered.

## Rules That Matter

- Use GPT Image for backgrounds and visual systems; add exact Ukrainian text locally when precision matters.
- If asking the image model to render text, put literal text in quotes or uppercase and specify font, placement, color, and size. For our production carousel flow, local text is safer.
- Specify negative space explicitly, for example: "large clean negative-space area in upper-left and center-left for huge overlay text."
- For UI/SaaS visuals, describe the product/interface as if it already exists. Use layout, hierarchy, spacing, cards, queues, rails, states, and controls instead of abstract concept-art language.
- For sequential carousels, do not generate one panorama and crop it unless speed matters more than quality. Generate slide-by-slide and use the previous slide as a reference.
- For multi-turn generation, restate critical invariants every time: palette, typography-safe zones, no readable text, no logos, no humanoid robots, red rail continuity.
- For edits, phrase changes as "change only X, keep everything else the same" and repeat preserve constraints.
- Evaluate with a rubric: instruction following, text/readability, style match, brand consistency, composition, and phone-feed clarity.

## Default Carousel Prompt Template

```text
Create slide <N> background for a premium <TOTAL>-slide Instagram carousel about <TOPIC>.
Format: 4:5 vertical social slide, standalone slide, not a panorama slice.

Story beat for this slide:
<HOOK / MECHANISM / PAYOFF>.

Composition:
Leave a large clean negative-space area in the upper-left and center-left for huge Ukrainian text overlay added later.
Place the main visual system mostly center-right and lower-right.
Use a bold red editorial interface rail that <enters from LEFT / exits through RIGHT / resolves into CTA node>.

Style:
Premium SaaS/editorial carousel, Swiss-inspired layout, warm off-white canvas, deep black UI elements, vivid strategic red accents, crisp shadows, subtle depth, restrained professional business design.

Visual elements:
<specific UI cards / CRM blocks / queues / approvals / pipeline / messages / decision tiles>.

Continuity:
Match the previous slide's palette, lighting, spacing, red rail, and interface style.

Constraints:
No readable text, no letters, no numbers, no logos, no watermark, no humanoid robots, no sci-fi cliches, no neon, no cluttered template look.
Must be readable and premium on a phone feed.
```

## Dark Format Prompt Delta

Replace the style block with:

```text
Premium dark SaaS/editorial carousel, deep charcoal/black canvas, off-white typography-safe areas, graphite UI panels, restrained red interface rail, crisp shadows, subtle depth, executive/business feel.
Avoid blue-purple cyberpunk, neon glow, gaming HUDs, crypto aesthetics, and sci-fi robots.
```

## Practical Workflow

1. Draft carousel copy first: slide 1 hook, slide 2 mechanism, slide 3 CTA.
2. Generate background only for slide 1.
3. Add local text and inspect phone readability.
4. Generate slide 2 using slide 1 as visual reference, continuing the rail/story.
5. Generate slide 3 using slide 2 as visual reference, resolving into CTA.
6. Add local Unbounded 900 text.
7. Check: text, safe zones, continuity, brand feel, no generated letters.
8. Publish only the versions that have both image and local text.
