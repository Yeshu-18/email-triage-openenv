#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPACE_URL="${1:-}"
DOCKER_BUILD_TIMEOUT="${DOCKER_BUILD_TIMEOUT:-900}"

log() { echo "[INFO] $*"; }
pass() { echo "[PASS] $*"; }
fail() { echo "[FAIL] $*"; exit 1; }

if [ -n "$SPACE_URL" ]; then
  log "Step 1/3: Checking Space reset endpoint"
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$SPACE_URL/reset" -H "Content-Type: application/json" -d '{"task_id":"email_easy"}')
  if [ "$HTTP_CODE" = "200" ]; then
    pass "HF Space /reset is healthy"
  else
    fail "HF Space /reset returned HTTP $HTTP_CODE"
  fi
else
  log "Step 1/3: Skipped Space check (pass Space URL as first argument)"
fi

log "Step 2/3: Docker build"
if ! command -v docker >/dev/null 2>&1; then
  fail "docker command not found"
fi

if command -v timeout >/dev/null 2>&1; then
  timeout "$DOCKER_BUILD_TIMEOUT" docker build "$REPO_DIR"
else
  docker build "$REPO_DIR"
fi
pass "Docker build succeeded"

log "Step 3/3: openenv validate"
if ! command -v openenv >/dev/null 2>&1; then
  fail "openenv command not found. Install with: pip install openenv-core"
fi

cd "$REPO_DIR"
openenv validate
pass "openenv validate passed"
