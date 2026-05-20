#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_FILE="$REPO_ROOT/state/daily_prepare.lock"
LOG_DIR="$REPO_ROOT/logs/raw"
LOG_FILE="$LOG_DIR/$(date +%F).log"
PROMPT_FILE="$REPO_ROOT/prompts/cron-agent.md"

resolve_codex() {
  if [[ -n "${CODEX_BIN:-}" && -x "$CODEX_BIN" ]]; then
    printf '%s\n' "$CODEX_BIN"
    return 0
  fi

  if command -v codex >/dev/null 2>&1; then
    command -v codex
    return 0
  fi

  local candidate
  for candidate in /home/blech/.vscode/extensions/openai.chatgpt-*/bin/linux-x86_64/codex; do
    if [[ -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}

run_python_fallback() {
  echo "$(date -Is) running Python fallback daily_prepare.py $*"
  python3 scripts/daily_prepare.py "$@"
}

run_codex_agent() {
  local codex_bin="$1"
  local prompt_path
  prompt_path="$(mktemp /tmp/civis-lens-cron-prompt.XXXXXX.md)"
  trap 'rm -f "$prompt_path"' RETURN

  {
    printf 'Run date: %s\n\n' "${CIVIS_RUN_DATE:-$(date +%F)}"
    cat "$PROMPT_FILE"
  } > "$prompt_path"

  echo "$(date -Is) running Codex agent for Civis Lens AU"
  "$codex_bin" \
    --search \
    --ask-for-approval never \
    exec \
    --sandbox workspace-write \
    -C "$REPO_ROOT" \
    - < "$prompt_path"
}

publish_generated_changes() {
  if [[ "${CIVIS_AUTO_COMMIT:-1}" != "1" ]]; then
    echo "$(date -Is) auto-commit disabled by CIVIS_AUTO_COMMIT"
    return 0
  fi

  git add agendas/queue.yaml docs/operations.md README.md TODO.md
  git add policies runs manual_batches outputs

  if git diff --cached --quiet; then
    echo "$(date -Is) no generated changes to commit"
    return 0
  fi

  echo "$(date -Is) committing prepared civic agenda bundle"
  git commit -m "Prepare daily civic agenda bundle"

  if [[ "${CIVIS_AUTO_PUSH:-1}" == "1" ]]; then
    echo "$(date -Is) pushing prepared civic agenda bundle to origin/main"
    git push origin HEAD:main
  fi
}

mkdir -p "$LOG_DIR" "$REPO_ROOT/state"

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "$(date -Is) another Civis Lens AU run is already active" >> "$LOG_FILE"
  exit 0
fi

cd "$REPO_ROOT"

{
  echo "$(date -Is) starting Civis Lens AU daily preparation"

  if [[ "${1:-}" == "--smoke-agent" ]]; then
    codex_bin="$(resolve_codex)"
    echo "$(date -Is) smoke testing Codex agent at $codex_bin"
    "$codex_bin" --ask-for-approval never exec --sandbox workspace-write -C "$REPO_ROOT" "Reply with READY only. Do not edit files or run tools."
  elif [[ "${1:-}" == "--python-only" ]]; then
    shift
    run_python_fallback "$@"
    publish_generated_changes
  else
    if codex_bin="$(resolve_codex)"; then
      run_codex_agent "$codex_bin"
      publish_generated_changes
    else
      echo "$(date -Is) Codex CLI not found; falling back to queue-only preparation"
      run_python_fallback "$@"
      publish_generated_changes
    fi
  fi

  echo "$(date -Is) finished Civis Lens AU daily preparation"
} >> "$LOG_FILE" 2>&1
