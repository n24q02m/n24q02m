# Harness-First — No Out-of-Band User Setup

Trước E2E matrix BẮT BUỘC follow 4-step pattern, KHÔNG run-and-fix cycle.

## 4-step pre-flight

1. **Read latest** `<memory>/e2e-execution-audit-*.md` failure-mode catalog + relevant `feedback_*.md` (`feedback_full_live_test.md`, `feedback_relay_fill_all_fields.md`, `feedback_stdio_fallback_local_only.md`)
2. **Audit driver source** cover hết failure modes catalog
3. **Build "Harness Readiness checklist"** + fix all gaps trong 1 commit/PR
4. **THEN run sequential 1-1**

## Cấm pattern

"start config → bug → fix → restart → next config → bug khác → fix → restart" (root cause "lần nào cũng khác, không lần nào hoàn thiện" 2 tuần liên tiếp).

## NO out-of-band user setup

TUYỆT ĐỐI KHÔNG đề xuất user "register `http://127.0.0.1:<port>/callback` ở upstream dashboard", "pin port", "grant account ngoài driver". Config nào cần out-of-band setup mỗi run = anti-pattern.

Phải hoặc:
- (a) Prod-stable callback + tunnel
- (b) Driver-controlled tunnel + provider DCR API
- (c) Loopback OAuth provider chấp nhận `http://127.0.0.1:<any>` (Google Desktop)
- HOẶC reclassify khỏi T2 matrix

## Violation

2026-04-27 (525c9518) USER #44/45: notion-oauth pin port 38765 + email-outlook prompt user click MS device-code.

Memory: `feedback_harness_first_no_run_fix_cycle.md` + `feedback_no_out_of_band_test_setup.md`.
