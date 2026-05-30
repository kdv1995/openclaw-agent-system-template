# Facebook Content Factory

Purpose: create Ukrainian Facebook content for `example brand` focused on painful AI/business problems, practical AI-agent use cases, and useful operator/founder guidance.

Publishing target:
- Postiz integration: `example brand` / `facebook` / profile `codebezmezh`
- Integration ID: `cmojta1o20165o70ygbci5fit`

Workflow:
1. Research timely AI-agent/business pain points and practical lifehacks.
2. Write Facebook-native posts for business owners/operators.
3. Generate a unique thematic supporting image through OpenClaw `image_generate` with model `openai/gpt-image-2` for this exact post package.
4. Main orchestrator sends the final post + image preview to the operator.
5. Publish through Postiz only after the operator explicitly approves the exact post and image.

Rules:
- Do not publish automatically.
- Do not use direct Facebook APIs.
- the operator's routing rule: image posts and business-pain/useful AI content go to Facebook `example brand`; viral/fresh news and insights found specifically in X/Twitter go to Threads.
- Validate approval packages with `skills/content-quality-gates/scripts/validate_facebook_package.mjs`.
- Do not reveal secrets.
- Avoid generic AI hype and fake urgency.
- Prefer concrete business pain, examples, checklists, and clear advice.
- Every Facebook post must have its own unique thematic image. Repeated images, generic templates, and unrelated fallback assets fail validation.
- Facebook images should be designed as feed hooks, not passive illustrations: one visible pain, one visual contrast, and optionally one short Ukrainian headline on-image.
- Use on-image text sparingly: 3-7 words, large and readable, no paragraphs or fake UI labels.
- Do not reuse older assets or “close enough” generated images as a fallback. If OpenClaw `image_generate` / `openai/gpt-image-2` is blocked, keep Facebook blocked and report the blocker instead of publishing with a substitute image.
