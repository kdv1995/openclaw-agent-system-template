# Threads Platform Limits

Operational defaults for the operator's Threads factory:

- Hard limit: 500 characters per Threads post.
- Preferred news format: 3-7 posts in a reply chain.
- Single post is an exception: use only for tiny updates, replies, or when the operator explicitly asks for a short post.
- Each post should usually be 120-420 characters, with 500 as the hard limit.
- Use Postiz integration `cmn2z0wij06plpb0yrviw718g` for `example_threads_handle`.

Validation:

```bash
node skills/content-quality-gates/scripts/validate_threads_package.mjs <json-file>
```

Direct fallback when Postiz is unavailable:

```bash
set -a
. ~/.openclaw/.env
set +a
node scripts/threads_publish_direct_fallback.mjs <json-file>
```

Required env:

- `THREADS_ACCESS_TOKEN`
- `THREADS_USER_ID`

Expected JSON shape:

```json
{
  "platform": "threads",
  "integrationId": "cmn2z0wij06plpb0yrviw718g",
  "format": "thread",
  "posts": ["hook/news", "context", "why it matters", "takeaway"]
}
```
