#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-$HOME/.openclaw/workspace/social-growth-os}"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_DIR="$BASE/runs/$RUN_ID"
mkdir -p "$RUN_DIR"
cp "$BASE/orchestrator.yaml" "$RUN_DIR/orchestrator.yaml"
cp "$BASE/tasks/end-to-end-social-growth-run.md" "$RUN_DIR/task.md"
cat > "$RUN_DIR/README.md" <<EOF
# Social Growth Run $RUN_ID

Use the agent briefs in $BASE/agents.
Write each stage output into this folder.
EOF
printf '%s
' "$RUN_DIR"
