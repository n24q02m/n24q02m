#!/usr/bin/env bash
set -euo pipefail

SCHED="$(dirname "$0")/../../scripts/priority-scheduler.sh"

# Test 1: Weekday Monday 09:00 → wake1
actual=$(FAKE_NOW="2026-04-20 09:00:00" bash "$SCHED" --print-wake)
expected="wake1_products"
[[ "$actual" == "$expected" ]] || { echo "FAIL T1: got $actual, want $expected"; exit 1; }

# Test 2: Weekday Tuesday 12:30 → wake2
actual=$(FAKE_NOW="2026-04-21 12:30:00" bash "$SCHED" --print-wake)
expected="wake2_products"
[[ "$actual" == "$expected" ]] || { echo "FAIL T2: got $actual, want $expected"; exit 1; }

# Test 3: Weekday Monday 14:00 → wake3
actual=$(FAKE_NOW="2026-04-20 14:00:00" bash "$SCHED" --print-wake)
expected="wake3_core"
[[ "$actual" == "$expected" ]] || { echo "FAIL T3: got $actual, want $expected"; exit 1; }

# Test 4: Weekday Friday 18:00 → wake4
actual=$(FAKE_NOW="2026-04-24 18:00:00" bash "$SCHED" --print-wake)
expected="wake4_plugins"
[[ "$actual" == "$expected" ]] || { echo "FAIL T4: got $actual, want $expected"; exit 1; }

# Test 5: Saturday 10:00 → weekend_research
actual=$(FAKE_NOW="2026-04-25 10:00:00" bash "$SCHED" --print-wake)
expected="weekend_research"
[[ "$actual" == "$expected" ]] || { echo "FAIL T5: got $actual, want $expected"; exit 1; }

# Test 6: Sunday 09:00 → weekend_research
actual=$(FAKE_NOW="2026-04-26 09:00:00" bash "$SCHED" --print-wake)
expected="weekend_research"
[[ "$actual" == "$expected" ]] || { echo "FAIL T6: got $actual, want $expected"; exit 1; }

# Test 7: Off-hours (weekday 03:00) → off_hours
actual=$(FAKE_NOW="2026-04-20 03:00:00" bash "$SCHED" --print-wake)
expected="off_hours"
[[ "$actual" == "$expected" ]] || { echo "FAIL T7: got $actual, want $expected"; exit 1; }

echo "ALL PASS (7 tests)"
