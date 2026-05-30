# Threads Content Factory

Local factory for producing Ukrainian Threads drafts for `example brand` / the operator.

It does not publish anything. It creates reviewable JSON/Markdown batches in `runs/`.

## Flow

1. Edit a brief in `state/brief.sample.json` or create a new one.
2. Generate a batch:

```bash
node scripts/generate_threads_batch.mjs --brief state/brief.sample.json --count 20
```

3. Validate the latest batch:

```bash
node scripts/validate_batch.mjs runs/<batch>.json
```

4. Add generated drafts to the queue:

```bash
node scripts/enqueue_batch.mjs runs/<batch>.json
```

5. Preview the publishing plan for a day:

```bash
node scripts/schedule_from_queue.mjs --date 2026-05-20
```

6. Create the scheduled posts in Postiz after review:

```bash
node scripts/schedule_from_queue.mjs --date 2026-05-20 --publish
```

Default schedule is configured in `state/schedule.config.json`:

- max 3 Threads posts/day
- `09:00`, `14:00`, `18:00`
- account: `example_threads_handle`

## Output

Each generated post has:

- `hook`
- `body`
- `cta`
- `post`
- `pillar`
- `format`
- `score`
- `warnings`

Threads limit is treated as 500 chars. The generator keeps drafts under that by default.

For viral/news posts, use skill `threads-viral-news-factory` and validate approval packages with:

```bash
node skills/content-quality-gates/scripts/validate_threads_package.mjs <package.json>
```

## Agent Mode

This factory now has separate OpenClaw specialist agents:

- `threads-research`: finds content angles
- `threads-writer`: writes drafts
- `threads-editor`: approves/rejects drafts
- `threads-scheduler`: schedules approved posts in Postiz
- `threads-analytics`: collects performance snapshots
- `threads-learning`: updates durable content rules

The operating model is in `runbooks/agent-operating-model.md`.

Specialists report back to the main orchestrator. They do not message Telegram directly.

Note: OpenClaw may need a session/gateway reload before newly configured `threads-*` agents are addressable by `agentId`. Until then, main can still run them as role-based subagents using the files in `agents/`.

## Reliability Rules

- Queue first, publish second.
- Scheduler is idempotent by local state: it will not exceed 3 created posts for the same day/account.
- Dry-run is the default. Nothing is sent to Postiz unless `--publish` is passed.
- Generated drafts, queue state, and scheduled state are stored locally for audit.
