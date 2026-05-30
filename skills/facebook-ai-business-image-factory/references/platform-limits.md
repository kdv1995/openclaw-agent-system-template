# Facebook Image Post Defaults

Operational defaults for `example brand`:

- Preferred feed image: square 1:1, 1080x1080 or higher.
- Generated minimum accepted: 1024x1024.
- Alternate feed image: 4:5, 1080x1350.
- Format: PNG or JPG.
- Post target: Postiz integration `cmojta1o20165o70ygbci5fit`.

Post shape:

- Opening: concrete business pain in first 2 lines.
- Body: problem -> agent workflow -> approval boundaries -> first practical step.
- CTA: soft, useful, not bait.

Validation:

```bash
node skills/content-quality-gates/scripts/validate_facebook_package.mjs <json-file>
```

Direct fallback when Postiz is unavailable:

```bash
set -a
. ~/.openclaw/.env
set +a
node scripts/facebook_page_publish_direct_fallback.mjs <json-file>
```

Required env:

- `FB_PAGE_ID`
- `FB_PAGE_ACCESS_TOKEN` with Page publishing permissions

Optional env:

- `META_APP_ID`
- `META_APP_SECRET` for appsecret proof

Expected JSON shape:

```json
{
  "platform": "facebook",
  "integrationId": "cmojta1o20165o70ygbci5fit",
  "content": "post text",
  "imagePath": "/absolute/path/to/image.png"
}
```
