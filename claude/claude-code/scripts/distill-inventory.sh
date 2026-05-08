#!/usr/bin/env bash
# Bash wrapper for distill_inventory.py.
# Usage: ./distill-inventory.sh [--output PATH]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python "$SCRIPT_DIR/distill_inventory.py" "$@"
