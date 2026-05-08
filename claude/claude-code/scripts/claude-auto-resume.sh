#!/bin/bash
# Claude Code auto-resume wrapper
# Retries claude command when rate limited
# Usage: claude-auto-resume.sh [claude args...]

MAX_RETRIES=5
RETRY_DELAY=60

for i in $(seq 1 $MAX_RETRIES); do
  claude "$@"
  EXIT_CODE=$?

  # Exit code 0 = normal exit, don't retry
  if [ $EXIT_CODE -eq 0 ]; then
    break
  fi

  # Check if rate limited (exit code varies, check recent output)
  if [ $i -lt $MAX_RETRIES ]; then
    echo "[auto-resume] Session ended (exit $EXIT_CODE). Waiting ${RETRY_DELAY}s before retry $((i+1))/$MAX_RETRIES..."
    sleep $RETRY_DELAY
  fi
done
