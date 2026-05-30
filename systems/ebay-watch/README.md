# eBay Watch

Twice-daily eBay monitoring service for a configured marketplace category.
This template ships without credentials, chat IDs, or active searches.

## What It Does

- Searches configured eBay categories/queries.
- Scores items by price, seller feedback, shipping, freshness, and keyword fit.
- Deduplicates already-seen item IDs.
- Saves raw JSON and Markdown reports.
- Sends Telegram digest when run with `--notify`.

## Setup

1. Put eBay API credentials in your local `.env` file or the shell environment:

   ```bash
   EBAY_CLIENT_ID=...
   EBAY_CLIENT_SECRET=...
   ```

2. Copy `config.example.json` to `config.json` and edit it:

   - set `enabled: true`
   - set `query`
   - optionally set `categoryIds`, `minPrice`, `maxPrice`, required/excluded keywords

3. Test:

   ```bash
   node scripts/run-ebay-watch.mjs
   ```

4. Notify Telegram:

   ```bash
   node scripts/run-ebay-watch.mjs --notify
   ```

## Schedule

Suggested OpenClaw cron jobs:

- `ebay-watch-morning-0930-delivered`
- `ebay-watch-evening-1930-delivered`

Both use `Europe/Kyiv`.
