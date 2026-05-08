#!/usr/bin/env bash
# Priority scheduler v2 (2026-04-17 pivot)
# Determines current wake group based on time in Asia/Ho_Chi_Minh timezone.
#
# Schedule (weekday Mon-Fri):
#   08:00-11:59  wake1_products  (KP, Aiora, QShip)
#   12:00-13:59  wake2_products  (same — second pass)
#   14:00-16:59  wake3_core      (knowledge/web/mcp-core, qwen3-embed, skret, jules)
#   17:00-20:59  wake4_plugins   (8 MCP plugin repos + claude-plugins)
#
# Schedule (weekend Sat-Sun):
#   09:00-11:59  weekend_research (WS-4 Gemma-4, WS-5 tiny distill, Akasha)
#
# Outside these windows → off_hours.
set -euo pipefail

NOW="${FAKE_NOW:-$(TZ=Asia/Ho_Chi_Minh date '+%Y-%m-%d %H:%M:%S')}"
DOW=$(TZ=Asia/Ho_Chi_Minh date -d "$NOW" '+%u')    # 1=Mon, 7=Sun
HOUR=$(TZ=Asia/Ho_Chi_Minh date -d "$NOW" '+%H')
HOUR=$((10#$HOUR))                                  # force decimal, no octal

CONFIG="${HERMES_CONFIG:-$HOME/.config/hermes/config.yaml}"

case "${1:-}" in
  --print-wake)
    if (( DOW >= 6 )); then
      if (( HOUR >= 9 && HOUR < 12 )); then
        echo "weekend_research"
      else
        echo "off_hours"
      fi
    elif (( HOUR >= 8 && HOUR < 12 )); then
      echo "wake1_products"
    elif (( HOUR >= 12 && HOUR < 14 )); then
      echo "wake2_products"
    elif (( HOUR >= 14 && HOUR < 17 )); then
      echo "wake3_core"
    elif (( HOUR >= 17 && HOUR < 21 )); then
      echo "wake4_plugins"
    else
      echo "off_hours"
    fi
    ;;
  --trigger)
    WAKE=$(bash "$0" --print-wake)
    [ "$WAKE" = "off_hours" ] && exit 0
    echo "Triggering Hermes wake group: $WAKE"
    # Hermes doesn't have a native "wake group" command; instead we cron-trigger
    # cron jobs through `hermes cron run` or just log for now.
    if command -v hermes >/dev/null 2>&1; then
      hermes cron run --group "$WAKE" 2>&1 || echo "hermes cron run failed or not configured"
    else
      echo "hermes binary not found on PATH"
      exit 1
    fi
    ;;
  *)
    echo "Usage: $0 --print-wake | --trigger" >&2
    exit 2
    ;;
esac
