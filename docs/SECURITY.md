# Security Notes

This repository is designed to be safe as a public template, but you must keep runtime data separate.

## Never Commit

- `.env` files;
- API keys, bot tokens, OAuth tokens, cookies, private keys;
- call transcripts or recordings;
- lead/customer databases;
- Google Sheets exports;
- generated campaign state;
- private memory files;
- platform upload IDs or publishing state;
- raw logs from production workflows.

## Recommended Secret Handling

- Use local `.env` files for development.
- Use a cloud secret manager for production.
- Rotate any token that was ever pasted into chat, logs, or committed history.
- Keep `.env.example` files with placeholder values only.

## External Action Rules

Require explicit human approval for:

- outbound phone calls;
- email and direct messages;
- publishing to social platforms;
- live deployments;
- deleting or overwriting production data.

## Export Hygiene

Before sharing a new archive or pushing to GitHub:

```bash
rg -n --hidden "BOT_TOKEN|API_KEY|SECRET|PASSWORD|PRIVATE KEY|ghp_|github_pat_|xox|sk-" .
git status --short
```

Review all matches manually. False positives are normal; real secrets are not.
