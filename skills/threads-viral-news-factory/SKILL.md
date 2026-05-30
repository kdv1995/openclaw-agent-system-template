---
name: threads-viral-news-factory
description: "Find X/Twitter-led viral AI news and prepare Threads posts through Postiz."
---

# Threads Viral News Factory

Use for the operator's Threads workflow.

## Routing

- Source: X/Twitter first.
- Destination: Threads `example_threads_handle` through Postiz, with direct Threads API fallback only when explicitly approved or when Postiz is unavailable and the operator has asked to publish now.
- Content type: viral/fresh news or strong insight from X/Twitter.
- No images by default. Image posts route to Facebook unless the operator says otherwise.
- Default format for news: multi-post thread, not a single post.

## Workflow

1. Search X/Twitter for current signal.
2. Verify claims with official or credible sources when the claim could be wrong.
3. Draft a Ukrainian thread with a clear chain:
   - post 1: strong hook and the news
   - post 2: context and source credibility
   - post 3: why it matters for AI agents/business/workflows
   - post 4+: implications, caveats, practical takeaways, or opinion
4. Validate every Threads item before Postiz:
   - each post <= 500 characters
   - news packages must contain 3-7 posts by default
   - single-post format is allowed only for tiny updates, replies, or when the operator explicitly asks for "коротко"
   - mini-thread can exceed 7 posts only when the operator asks for depth
   - no generic "AI is the future" angle
   - clear "why this matters" sentence in the chain
5. Publish through Postiz only after explicit approval or an explicit current request to publish.
6. If Postiz fails and the operator explicitly approves fallback, use direct Threads API via `scripts/threads_publish_direct_fallback.mjs`. This requires `THREADS_ACCESS_TOKEN` and `THREADS_USER_ID` in `~/.openclaw/.env`.

## Quality Bar

- The post must not be just a translated headline.
- Add context: who/what/why it matters, then turn it into a readable chain.
- Use X/Twitter as discovery evidence, not as unquestioned truth.
- Keep the first post strong enough to stand alone in the feed.
- Avoid overclaiming and unsourced rumors.
- Never paste or store access tokens from chat. If a token was sent in chat, ask the operator to rotate it and put the replacement in `.env`.

## References

- `references/platform-limits.md`
