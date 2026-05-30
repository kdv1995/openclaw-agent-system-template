---
name: facebook-ai-business-image-factory
description: "Create Facebook image posts about business pain solved by AI agents."
---

# Facebook AI Business Image Factory

Use for `example brand` Facebook content.

## Routing

- Destination: Facebook `example brand` through Postiz after the operator approves the generated image review package.
- Postiz integration: `cmojta1o20165o70ygbci5fit`.
- Content type: business pain, useful AI-agent case, practical workflow.
- Creative style: use the operator's canonical "business loss must not die in chat" format for image hooks by default. Example logic: `ТВОЇ ЛІДИ НЕ МАЮТЬ ВМИРАТИ В ЧАТІ.` Adapt the noun and place of loss to the post pain.
- Image required unless the operator explicitly asks for text-only Facebook.
- Every Facebook post needs a unique, thematic image generated for that exact post. Never reuse older images, generic templates, or adjacent-topic assets.
- Plain viral news without image routes to Threads.
- Visual generation route: OpenClaw `image_generate` with model `openai/gpt-image-2`, the configured default image model for this factory.

## Workflow

1. Pick one concrete business pain.
2. Explain how an AI agent can close or reduce it.
3. Include limits and approval boundaries. Good agents do not silently send money, delete data, pressure customers, or change terms.
4. Generate one unique, thematic image through OpenClaw `image_generate` using model `openai/gpt-image-2`. The image must match the exact post angle and business pain. Do not use the local legacy `imagegen` API skill/CLI for this factory unless the operator explicitly changes the route.
5. Validate the package:
   - Facebook post has a concrete pain in the first 2 lines
   - image exists, is unique to this post, thematic, and suitable for feed
   - image headline, if present, uses huge bold poster typography and is not thin/small/subtle
   - target integration is `cmojta1o20165o70ygbci5fit`
   - no direct Facebook API use
6. For scheduled content-factory cron jobs, research/text can run autonomously, but generated image posts now require the operator review before publishing. Send the image, final text, exact prompt, and pain rationale to Telegram; publish only after clear approval.
7. If Postiz fails, do not use direct fallback automatically. Report the blocker and wait for explicit fallback approval.
8. Direct Facebook Pages API fallback is allowed only after explicit approval and only with credentials from `.env`, using `scripts/facebook_page_publish_direct_fallback.mjs`. This requires `FB_PAGE_ID` and `FB_PAGE_ACCESS_TOKEN` in `~/.openclaw/.env`; `META_APP_SECRET` is optional for appsecret proof.
9. If OpenClaw `image_generate` is unavailable or model `openai/gpt-image-2` is not configured, mark the Facebook item as `blocked:image_generation_route`, do not publish text-only fallback unless the operator explicitly approved it, and report partial success instead of treating unrelated platform outputs as failed.

## Image Defaults

- Preferred: 1:1 square, 1080x1080 or higher.
- Acceptable: 1024x1024 minimum for generated images.
- Alternate: 4:5 portrait, 1080x1350 for feed-first posts.
- Format: PNG or JPG.
- Every generated visual needs a clear feed hook, not only a literal illustration of the post topic.
- Default hook structure: one visible business pain, one visual contrast, one short overlay headline based on `ТВОЇ <цінність> НЕ МАЮТЬ ВМИРАТИ В <хаосі/чаті/таблицях/директі/ручних процесах>.`
- Overlay text is allowed and encouraged when it increases scroll-stop value, but keep it to 3-7 Ukrainian words. Use one large headline only; avoid paragraphs, fake UI text, and small unreadable labels.
- Typography lock for the operator's style: overlay headlines must be huge, heavy, poster-like Ukrainian type. Use `Unbounded 900` for local overlays when rendering text outside the generator; if asking GPT Image 2 to render text, specify "bold black poster typography, thick block letters, large uppercase, not thin, not light, not delicate". Reject and regenerate any image where the main headline looks thin or small.
- Feed readability rule: the main image headline must be understandable from a phone preview in under one second. If it reads like a subtle title or caption instead of a bold hook, it fails validation.
- Prefer image concepts that show tension/resolution: chaos to control, missed money to recovered revenue, manual bottleneck to approval workflow, overload to prioritized queue.
- Make the AI agent visible as a practical dashboard/assistant layer, routing or highlighting work for human approval. Do not show a humanoid robot unless the operator explicitly asks.
- Prompt for strong composition: bold focal point, clean negative space, safe crop margins, and business-readable contrast.
- Avoid readable fake UI text, fake logos, distorted hands, stock-photo smiles, excessive neon.
- Never paste or store access tokens/app secrets from chat. If a secret was sent in chat, ask the operator to rotate it and put the replacement in `.env`.

## References

- `references/platform-limits.md`
