---
name: facebook-ai-business-image-factory
description: "Create Facebook image posts about business pain solved by AI agents."
---

# Facebook AI Business Image Factory

Use for `Your Brand` Facebook content.

## Routing

- Destination: Facebook `Your Brand` through Postiz.
- Postiz integration: `POSTIZ_FACEBOOK_ID`.
- Content type: business pain, useful AI-agent case, practical workflow.
- Image required unless template owner explicitly asks for text-only Facebook.
- Every Facebook post needs a unique, thematic image generated for that exact post. Never reuse older images, generic templates, or adjacent-topic assets.
- Plain viral news without image routes to Threads.
- Visual generation route: OpenClaw `image_generate` with model `openai/gpt-image-2`, the configured default image model for this factory.

## Workflow

1. Pick one concrete business pain.
2. Explain how an AI agent can close or reduce it.
3. Include limits and approval boundaries. Good agents do not silently send money, delete data, pressure customers, or change terms.
4. Generate one unique, thematic image through OpenClaw `image_generate` using model `openai/gpt-image-2`. The image must match the exact post angle and business pain. Do not use the local legacy `imagegen` API skill/CLI for this factory unless template owner explicitly changes the route.
5. Validate the package:
   - Facebook post has a concrete pain in the first 2 lines
   - image exists, is unique to this post, thematic, and suitable for feed
   - target integration is `POSTIZ_FACEBOOK_ID`
   - no direct Facebook API use
6. For scheduled content-factory cron jobs, template owner has enabled no-approval autopublishing through Postiz after package validation.
7. If Postiz fails, do not use direct fallback automatically. Report the blocker and wait for explicit fallback approval.
8. Direct Facebook Pages API fallback is allowed only after explicit approval and only with credentials from `.env`, using `scripts/facebook_page_publish_direct_fallback.mjs`. This requires `FB_PAGE_ID` and `FB_PAGE_ACCESS_TOKEN` in `<openclaw-home>/.env`; `META_APP_SECRET` is optional for appsecret proof.
9. If OpenClaw `image_generate` is unavailable or model `openai/gpt-image-2` is not configured, mark the Facebook item as `blocked:image_generation_route`, do not publish text-only fallback unless template owner explicitly approved it, and report partial success instead of treating unrelated platform outputs as failed.

## Image Defaults

- Preferred: 1:1 square, 1080x1080 or higher.
- Acceptable: 1024x1024 minimum for generated images.
- Alternate: 4:5 portrait, 1080x1350 for feed-first posts.
- Format: PNG or JPG.
- Avoid readable fake UI text, fake logos, distorted hands, stock-photo smiles, excessive neon.
- Never paste or store access tokens/app secrets from chat. If a secret was sent in chat, ask template owner to rotate it and put the replacement in `.env`.

## References

- `references/platform-limits.md`
