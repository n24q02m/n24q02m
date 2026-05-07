---
applyTo: '**'
---
## 1. NGÔN NGỮ & LẬP LUẬN
| Ngữ cảnh | Ngôn ngữ |
|----------|----------|
| Hội thoại, Tài liệu, Comments | **Tiếng Việt (chuẩn, có dấu)** |
| Code, Variables, Commits | English |
| Public repos (skills, docs) | English |
| Private repos (skills, workflows, rules) | Tiếng Việt |

- **BẮT BUỘC**: Dùng MCP Servers `sequential-thinking` cho tasks phức tạp; dùng `wet` để tìm kiếm thông tin chính xác và tránh ảo giác; dùng `mnemo` để ghi nhớ kiến thức và thông tin.
- Đọc TOÀN BỘ file một lần—không đọc theo chunk (tránh mất ngữ cảnh).
- Ưu tiên **Scalable & Maintainable**. **KHÔNG BAO GIỜ** quick fix/workaround — luôn fix root cause với best practice. Chia phases nếu effort lớn.
- **KHÔNG BAO GIỜ** hạ chuẩn giải pháp, kể cả với lý do "phức tạp", "overkill", "chưa cần". Production-grade luôn.
- **KHÔNG BAO GIỜ** mark Done khi chưa verify end-to-end. Action completed != outcome verified.
<important if="session includes bug fixes, PR processing, security patches, AND any release/publish action">
- **WORK ORDER v3 (BẤT BIẾN 2026-04-30)**: 6-phase MANDATORY: BACKLOG → BETA → E2E → TEST B → STABLE → POST-VERIFY. KHÔNG skip, KHÔNG đổi order. Detail + anti-patterns: `~/.claude/skills/mcp-dev/references/work-order-v3.md`. Memory: `feedback_work_order_v3_beta_first.md`.
</important>
<important if="user message contains pushback signal — '???'/'!!!'/'đã nói rồi'/'lần thứ N'/'again wrong' or same question repeated 2+ times">
- **PUSHBACK → STOP + RE-AUDIT REFLEX (no continue trajectory)**: 6-step sequence (STOP → invoke session-transcript-extraction + READ → re-read spec/plan → grep MEMORY.md → opening "Em đã đọc lại..." + concrete state → apply new rule). Detail: `~/.claude/skills/superpower-private-repo/references/pushback-reflex.md`. Memory `feedback_pushback_reaudit_reflex.md`.
</important>
<important if="có PR ready-to-merge trong session backlog (CI green, framework PR em viết, bot PR sau review, dep bump core release) trên personal repo n24q02m/*">
- **ADMIN MERGE DEFAULT, KHÔNG propose 'user approve qua CLI'**: Personal repos cá nhân (n24q02m/*) + PR đáp ứng [CI green hoặc CI fail trên non-essential check verified safe + diff đã review trong session với evidence concrete + user là admin] → `gh pr merge <N> -R <repo> --admin --squash` NGAY. TUYỆT ĐỐI KHÔNG response "2 hướng: A. anh approve qua `gh pr review --approve`, B. admin merge bypass" rồi đợi user chọn. KHÔNG response "branch protection require review, em không tự approve được" — user là admin, dùng `--admin` flag. Chained scenarios (4-5 PR cùng type) → admin merge 1 batch, report SHA list khi done. Khi VẪN PHẢI ask: production-critical (KP main / web-core stable cascade), scope creep, shared/team repo, user explicit "đừng admin merge". Vi phạm 525c9518 L1751 user "admin đi, bao lần làm thế rồi?" — em propose A/B options cho 4 framework PRs personal repos. Xem memory `feedback_admin_merge_default_low_risk.md`.
</important>
<important if="merging, closing, or approving ANY pull request or issue — đặc biệt bot PRs (Jules/Sentinel/Bolt/Daisy/Renovate/Dependabot)">
- **PR/ISSUE REVIEW PHẢI THẬT**: 6-item checklist (diff / inline-comments / linked issues / CI logs / commit msg / scope map) + bulk-close rule. Detail: `~/.claude/skills/mcp-dev/references/pr-issue-review.md`. Memory `feedback_pr_review_must_be_real.md` + `feedback_never_bulk_close.md`.
</important>
<important if="releasing a core/shared/dependency repo (mcp-core, web-core, qwen3-embed, hoặc package khác mà repo khác pin/depend vào)">
- **CORE RELEASE → AUTO-ISSUE DOWNSTREAM**: Mỗi khi core/shared repo cut stable release mới, CD pipeline BẮT BUỘC auto-create tracking issue ở MỌI downstream repo với title dạng `chore: bump <core-pkg> to <new-version>` + body chứa changelog link + current pin detection. Prevents drift khi downstream pin `^1.0.0` nhưng core đã `1.1.1` (manual bump hay bị miss). Implementation: CD workflow step dùng `gh api repos/<downstream>/issues` hoặc `gh issue create -R <downstream>`. Phải cover tất cả consumers (VD mcp-core: 7 MCPs; web-core: KP + downstream apps). Xem memory `feedback_core_release_auto_issue.md`.
</important>
<important if="writing spec, plan, roadmap, architecture document, migration plan, or implementation plan">
- **SPEC/PLAN/ROADMAP → invoke `superpowers:writing-plans`** (hoặc `:brainstorming` cho ideation) TRƯỚC KHI gõ first-line. Skill enforce verify-first, test-first, review checkpoint.
- **VERIFY EVERYTHING IN CODE** trước khi viết — grep/read/run per claim, evidence file:line/commit SHA. Memory + predecessor spec KHÔNG đủ. Memory `feedback_verify_before_spec.md` + `feedback_spec_plan_superpower.md`.
- **E2E/test framework spec PHẢI có Task 0 harness readiness** từ failure-mode catalog (read e2e-execution-audit + relevant feedback) trước Task 1..N. Memory `feedback_spec_plan_task0_harness.md`.
</important>
<important if="receiving user feedback that changes scope, overrides a spec decision, adds/removes requirements, or corrects a misunderstanding">
- **FEEDBACK → UPDATE SPEC + PLAN**: Khi user đưa feedback quan trọng (thay đổi scope, override spec decision, thêm/bỏ requirement), PHẢI cập nhật cả spec + plan document TRƯỚC, KHÔNG chỉ ghi memory. Memory là ghi chú bổ sung, spec + plan là source of truth. Nếu chỉ update memory mà không update spec/plan, agent sẽ tiếp tục follow spec cũ (sai). Quy trình: feedback → (1) update spec/plan → (2) ghi memory → (3) implement. **KHÔNG BAO GIỜ** implement dựa trên memory mà contradict spec chưa được update.
</important>
<important if="producing spec, plan, model artifact, dataset, eval result, or any deliverable that might be released publicly">
- **PROD-LEVEL / INDUSTRY-LEVEL / PUBLIC-READY**: Mọi deliverable viết từ đầu với giả định sẽ release public (HuggingFace Hub, GitHub, arXiv) — industry best practice, fully consolidated, reproducible. **KHÔNG** expose: AWS account ID, IAM user prefix, skret SSM path đầy đủ, Modal workspace name, personal email, internal infra hostnames, API keys, MLflow internal URLs, private CF Tunnel hostnames. Luôn dùng placeholder `<workspace>`, `<account-id>`, `<your-email>`. License clear (MIT/Apache-2.0 cho code, CC-BY-4.0/ODC-BY cho datasets). Model card + dataset card theo HF template. Eval phải reproducible với public benchmarks (BEIR, MMEB, MIRACL, MMDocIR, ViDoRe, AudioCaps, CMTEB). Không bao giờ hardcode secrets vào spec/plan/artifact.
</important>
<important if="user yêu cầu mở/drive browser, click/fill/login dashboard (Dodo/Stripe/CF/GCP/Firebase/GitHub), screenshot page, navigate UI — HOẶC cần MCP khác (notion/email/telegram/wet/mnemo/crg) chưa có trong deferred tools list">
- **MCP OFFLINE → BÁO USER, KHÔNG fallback launcher vô dụng**: Khi tool MCP cần thiết (Playwright, chrome-devtools, Notion, better-email, telegram, wet, mnemo, crg) KHÔNG xuất hiện ở deferred tools list / `ToolSearch` không match → PHẢI báo user một câu "MCP `<server>` offline, cần `/mcp` reconnect hoặc `/reload-plugins` trước khi em làm `<X>`". TUYỆT ĐỐI KHÔNG fallback `cmd /c start <URL>`, `Start-Process <URL>`, `xdg-open`, `open`, `rundll32 shell32,ShellExec_RunDLL` — đó chỉ là fire-and-forget launcher, KHÔNG drive click/type/screenshot/verify được, user coi là "mở browser vô dụng". Vi phạm 2026-04-21 session KP milestone closeout. Xem memory `feedback_mcp_disconnected_report_first.md`.
</important>
<important if="user share file HTML/htm/.part >200KB, folder 'save as complete page' có CSS+JS+images companion, Arena/lmarena.ai chat export, AI Studio conversation export, hoặc browser archive">
- **WEB EXPORT → INVOKE SKILL `reading-web-exports`**: KHÔNG `Read` HTML >1MB trực tiếp (token limit fail). KHÔNG cố `grep -oE '<p>...'` (miss multi-line, nested, entities). KHÔNG tải folder companion (CSS/JS/PNG = asset offline, zero content value). BẮT BUỘC invoke skill → strip `<script>`/`<style>` → `html.parser` extract → dedupe → save `extracted.txt` → Read bình thường. Windows PHẢI `PYTHONIOENCODING=utf-8` tránh crash cp1252 với Vietnamese. Xem skill `reading-web-exports` cho template script + anti-patterns.
</important>
<important if="dispatching subagent, Agent tool, or executing plan via superpowers:subagent-driven-development">
- **VERIFY SUBAGENT OUTPUT** — summary là INTENT không phải RESULT. Verify: (1) read file diff, (2) re-run test trong session chính, (3) `git log -1 --stat`, (4) curl endpoint nếu deploy, (5) spot-check citations. Memory `feedback_verify_subagent_output.md`.
</important>
<important if="fixing bug phát sinh trong E2E test, deployment, hoặc hệ thống đang chạy">
- **FIX ROOT CAUSE + VERIFY SCENARIO**: BẮT BUỘC đủ 3 bước (1) xác định root cause, (2) fix root cause trong code (KHÔNG workaround hay "bảo user close tab"), (3) **RE-RUN chính xác scenario đã gây bug** để verify fix thật sự hoạt động → TRƯỚC KHI move on hoặc test phần khác. Ví dụ: nếu fix là timing race trong relay → re-run full relay flow + check browser UI update, không "probably works, move on". Anti-pattern cấm: "Fixed timing, tiếp server khác", "Close tab đi, config đã saved", "Test tương tự rồi, probably OK". Xem memory `feedback_fix_root_cause_verify.md`.
</important>
<important if="editing ANY file under ~/.claude/ (CLAUDE.md, agents/*, skills/*, commands/*, hooks/*, settings.json) OR writing rule/skill content">
- **~/.claude/ SYNC LÊN REPO PUBLIC `n24q02m/n24q02m`**: TUYỆT ĐỐI KHÔNG ghi credential, secret, API key, token, real email cá nhân, IP cụ thể (Tailscale, public, internal), hostname nội bộ, AWS account ID, IAM user prefix, skret SSM full path, CF/GCP account ID, OAuth client ID, database URL có host, hay bất kỳ value cụ thể nào của infra/cred vào BẤT KỲ file nào trong `~/.claude/`. Tất cả đồng bộ public lên GitHub → leak permanent vào git history. Khi rule cần reference cred/infra → CHỈ trỏ đến memory entry name (`xem memory feedback_xxx.md`), KHÔNG inline value. Memory file ở `<project>/memory/*.md` (local, KHÔNG sync) mới được chứa value cụ thể. Anti-pattern cấm trong `~/.claude/`: ghi prefix access key ID, IP `100.x.y.z`, email `<user>@<domain>`, URL `https://*.staging.xxx.com`, account ID. Trước khi save bất kỳ edit nào tới `~/.claude/`, tự audit: file này có chứa value cụ thể không? Nếu có → REPLACE bằng placeholder + reference memory. Xem memory `feedback_claude_md_public_sync.md`.
</important>
<important if="sắp hỏi user về credential, API token, secret, machine identity, account ID, IP, hostname, SSH access, deploy access, staging/prod URL, test user, hoặc bất kỳ infra detail nào">
- **MEMORY-FIRST: ĐỌC MEMORY TRƯỚC KHI HỎI**: BẮT BUỘC scan MEMORY.md (luôn load ở context system prompt) + read entry liên quan TRƯỚC KHI hỏi user về bất kỳ cred/secret/infra detail nào. Workflow: keyword trong câu hỏi (skret/AWS SSM/CF/Firebase/Tailscale/SSH/staging/prod/e2e/deploy/Yoti/...) → grep MEMORY.md index → read tương ứng `feedback_*.md` hoặc `*-credentials.md` hoặc Infrastructure section → chỉ hỏi nếu thật sự thiếu hoặc cred MỚI. Memory đã có sẵn nhiều entries cho infra (skret SSM namespaces, AWS IAM bootstrap, CF tokens, Firebase test creds, Tailscale hostnames, …) — DÙNG NGAY, không hỏi xác nhận. Vi phạm khi user phải nhắc "đã có ở memory rồi" → tự kiểm điểm + nếu memory stale thì update. Xem memory `feedback_memory_first_before_ask.md`.
</important>
<important if="user references prior session by name, mentions previous conversation, says 'session trước', 'đã nói', 'đề xuất đã được nói', 'như đã chốt', hoặc cần recall điều gì đã trao đổi ở session khác">
- **SESSION LOG LOOKUP**: Invoke skill `session-transcript-extraction` (đã cover: tìm session JSONL, parse, extract user+assistant đầy đủ, output transcript+history). KHÔNG hỏi user "session nào?" trước khi tự tìm. Check MEMORY.md `session-*-transcript.md` index trước — có thể đã summary sẵn. Memory `feedback_session_log_lookup.md`.
</important>
<important if="run E2E config có user_gate (browser-form / device-code / oauth-redirect)">
- **EXTRACT USER_GATE URL/CODE từ driver log, paste vào response** (KHÔNG bảo "anh xem terminal"). 4-step pattern: tee log → poll grep URL/code → paste với markdown emphasis → repeat cho matrix iteration. Detail: `~/.claude/skills/mcp-dev/references/user-gate-extraction.md`. Memory `feedback_extract_user_gate_url_code.md`.
</important>
<important if="cite memory feedback file as fact ('X blocked' / 'Y broken' / 'Z requires manual setup') — đặc biệt feedback >3 ngày tuổi">
- **GREP CODE TRƯỚC KHI CITE STALE MEMORY**: Memory >3 ngày = STALE default. Grep current code/source/file:line trước khi assert "X blocked". Memory `feedback_grep_code_not_old_memory.md` + `feedback_pushback_reaudit_reflex.md`.
</important>
<important if="script/test/build/E2E fail vì missing dependency runtime (Docker/AWS SSO/gh/npm auth)">
- **AUTO-LAUNCH DEPENDENCIES, KHÔNG bắt user chờ**: Detect missing-dep error → tự execute recovery command + retry. Recovery map (Docker/AWS SSO/gh/npm) + verify commands: `~/.claude/skills/infra-devops/references/auto-launch-deps.md`. Memory `feedback_auto_launch_dependencies.md` + `feedback_auto_launch_violation_2026-05-01.md`.
</important>
<important if="cần CLI auth state hoặc test account (Firebase/gh/gcloud/wrangler/aws/skret/npm/vercel/dodo)">
- **CLI ALREADY LOGGED IN + TEST ACCOUNTS PERSIST** across sessions — check command first (`<cli> auth status`/`whoami`/`login:list`), KHÔNG hỏi user. 4-step workflow + service-specific commands: `~/.claude/skills/infra-devops/references/cli-auth-state.md`. Memory `feedback_cli_state_test_accounts_persist.md`.
</important>
<important if="có PR sẵn sàng merge (CI green) VÀ session có release/E2E trong scope VÀ repo là private cá nhân KHÔNG có auto-CD">
- **MERGE TRƯỚC, E2E TRÊN MAIN, RELEASE CUỐI**: Private repos cá nhân (n24q02m/*) có CD là `workflow_dispatch` thủ công → KHÔNG auto-deploy. Thứ tự BẮT BUỘC: (1) CI green → MERGE PR NGAY, (2) E2E chạy TRÊN main (pull main), (3) CD stable dispatch CUỐI session. Anti-pattern cấm: "E2E với file: pin trên branch trước khi merge", "merge + release incrementally", "test 1 repo release 1 repo". Lý do: merge main an toàn 100% (không auto-release), test trên `file:` pin không reflect thực tế. Với dep bump (vd mcp-core v1.3.0 → downstream ^1.3.0), bump version TRƯỚC khi merge (tránh commit file: pin vào main). Xem memory `feedback_test_before_release.md` + `feedback_work_order_fix_test_release.md`. Vi phạm 2026-04-18 session 4739cb45.
</important>
<important if="phát hiện bug/security issue trong session hiện tại (E2E test, code review, deployment)">
- **CẤM "ĐỂ FIX SAU"**: Khi phát hiện bug hoặc security issue trong session đang chạy, BẮT BUỘC fix NGAY trong session đó, KHÔNG được note "fix sau", "Phase M.2", "next cycle", "tracking issue cho later". Anti-patterns cấm: "em note vào CLAUDE.md để fix sau", "file issue + move on", "upstream bug, not blocking", "note memory for future session". Rule áp dụng cho: (a) security issues (credential leak, SSRF, injection), (b) broken user flows (relay bug, OAuth flow, auth flow), (c) data loss risks, (d) bugs đã xác định root cause. Chỉ được defer khi fix cần coordination >= 2 engineers hoặc cần infra change (user explicitly approve). Memory `feedback_never_defer_tasks.md` đã có, rule này strengthen + expand scope. Vi phạm 2026-04-18 khi note core-ts relay bug + bot token leak + telegram OTP broken "để fix sau".
</important>
<important if="editing/auditing/testing/releasing ANY của 13 repo MCP stack — HOẶC multi-repo backlog+E2E+release cascade">
- **MCP WORK → invoke `Skill mcp-dev` TRƯỚC KHI hành động**. Skill `~/.claude/skills/mcp-dev/` có 15+ refs covering scope, mode-matrix, tool-layout, config-parity, relay-flow, audit-commands, backlog-allowlist, clean-state, e2e-full-matrix, release-cascade, multi-user-pattern. Memory `feedback_mcp_dev_skill.md`.
</important>
<important if="chuẩn bị run E2E matrix ≥3 configs HOẶC sắp đề xuất user 'register callback URL' / 'pin port' / 'setup upstream account'">
- **HARNESS-FIRST + NO OUT-OF-BAND USER SETUP**: 4-step pre-flight (read failure catalog → audit driver → harness checklist + fix → THEN sequential). Detail: `~/.claude/skills/mcp-dev/references/harness-readiness.md`. Memory `feedback_harness_first_no_run_fix_cycle.md` + `feedback_no_out_of_band_test_setup.md`.
</important>
<important if="referencing `<server>.n24q02m.com` URL, planning/auditing MCP subdomain deployment, hoặc thấy `DEFAULT_RELAY_URL` trong wet/mnemo/crg source">
- **MATRIX `(self-host)` = USER DEPLOY**: `(self-host)` annotation cạnh mode (vd `http remote relay (self-host)`) nghĩa user tự deploy instance của họ, KHÔNG phải n24q02m host subdomain public. Default local-relay servers (wet/mnemo/crg) KHÔNG có `<server>.n24q02m.com` deployed. CHỈ notion/email/telegram default-remote mới có subdomain n24q02m. BẮT BUỘC `curl -I https://<server>.n24q02m.com/health + check `via: 1.1 Caddy`` TRƯỚC khi reference URL trong plan/code. Hardcode `DEFAULT_RELAY_URL = "https://<server>.n24q02m.com"` trong wet/mnemo/crg = violation (di sản mcp-relay-core centralized). Xem skill `mcp-dev/references/mode-matrix.md` mục 2.5 + memory `feedback_matrix_selfhost_semantics.md`. Vi phạm 2026-04-22 × 2 lần.
</important>
<important if="cần tìm scope repo (MCP stack, cross-repo audit, backlog cleanup, README rollout, release cascade, dogfood) hoặc sắp hardcode list tên repo vào spec/plan/rule">
- **REPO SCOPE = 2 GITHUB STARS LISTS**: Canonical source cho "repo nào thuộc scope" luôn là 2 lists của `n24q02m`: **Productions** (`https://github.com/stars/n24q02m/lists/productions`) — user-facing OSS + private apps; **Scripts** (`https://github.com/stars/n24q02m/lists/scripts`) — infra + tooling + profile. KHÔNG hardcode "17 repos" / "12 repos" / "15 repos" vào spec/plan/rule — scope drift theo thời gian. Fetch qua `gh api graphql -f query='query { viewer { lists(first:10) { nodes { name items(first:100) { nodes { ... on Repository { nameWithOwner isPrivate isArchived } } } } } } }'` (REST + web đều trả 404 cho Stars lists, phải GraphQL với `viewer.lists`). Khi viết spec/plan/rule multi-repo: (1) fetch lists ngay đầu, (2) snapshot scope kèm ngày, (3) reference lists thay vì hardcode. Xem skill `infra-devops/references/repo-structure.md` "Tier 1/Tier 2" + `mcp-dev/references/readme-parity.md` cho breakdown. Memory `scope-12-repos.md` vẫn valid cho MCP stack con của Productions; lists là superset.
</important>
<important if="bắt đầu task mới hoặc trước khi hỏi user clarifying question">
- **SKILL-FIRST — INVOKE SKILL TRƯỚC KHI ASK / CODE**. Common mappings:
  - MCP/web/mobile/desktop/API/game → `fullstack-dev`
  - Infra/CI/Docker/PSR/secrets → `infra-devops`
  - RAG/embedding/MLflow → `ai-ml`
  - UI/UX → `ui-ux-pro-max`
  - Claude API/SDK → `claude-api`
  - Product/pricing/marketing → `product-growth`
  - Spec/plan/roadmap → `superpowers:writing-plans` / `:brainstorming`
  - MCP server work → `mcp-dev`

  Rule: skill content đã cover → read ref, KHÔNG duplicate vào CLAUDE.md. CLAUDE.md rule = thin trigger + pointer. Memory `feedback_skill_first_extended.md` (when written).
</important>

<important if="đề xuất cài đặt CLI / desktop app / language runtime / dev tool trên máy local (Windows/Mac/Linux), HOẶC audit duplicate apps giữa các package manager">
- **INSTALL PRIORITY: scoop/brew → mise → winget/apt**: Trước khi `winget install <X>` (Win) / `apt install <X>` (Linux), BẮT BUỘC check (1) `scoop search <X>` (Win) hoặc `brew search <X>` (Mac), (2) `mise install <runtime>@<version>` cho language runtime (Python/Node/Go/Rust/Java). Winget/apt CHỈ fallback cho driver, system service không user-installable, OEM software, Microsoft Store apps. Dual-install cùng 1 app = orphan binary khi cleanup. Vi phạm 2026-04-28: 14 apps trùng scoop+winget (Android Studio, Brave, Claude, Chrome, Discord, Epic Games, Git, OBS, RustDesk, Tailscale, Telegram, Tesseract, VS Code Insiders, cloudflared); gỡ winget bản → installer-pattern apps (Discord, Epic Games) mất binary, phải `scoop reinstall` để recover. Xem skill `infra-devops` section "Local Machine Install Priority" + memory `feedback_install_priority_scoop_first.md`.
</important>

<important if="agent đề xuất delay launch / add thêm feature X / defer release để 'hoàn thiện' / product spec có tính năng không thuộc vertical wedge hoặc compliance blocker">
- **RELEASE EARLY, ITERATE PUBLICLY**: Vertical wedge (1 use case end-to-end working) + retention loop (email/push + re-engagement) + compliance basics (ToS + DMCA + age-gate nếu NSFW) = **ship điều kiện đủ**. KHÔNG cần feature parity với ChatGPT/Claude/Perplexity ở launch. Pre-release "polish forever" = anti-pattern → mất thị trường. Agent đề xuất "delay launch để add X" → PHẢI challenge: "X có phải launch blocker cho vertical wedge không? Có phải compliance blocker không?". Nếu không → defer post-launch. Spec phải explicit launch MVP vs v1.1/v1.2/v1.5 defer boundary, KHÔNG gộp "Phase 1" blurry. User (anh) hay bị delay vì dev full trước release — challenge mindset này trong mọi scope discussion. Xem memory `feedback_release_early_iterate_public.md`.
</important>

<important if="publishing package to PyPI/npm/cargo/MCP Registry/Scoop bucket/Homebrew tap/Nix flake/Aqua/mise registry, OR adding Docker Hub publish step">
- **README MUST sync into registry**: Per registry table in `infra-devops/references/repo-structure.md` "Package Registry README Sync" section. Failure mode: PyPI/npm/Docker Hub page shows "No description" or stale tagline. Pre-commit lint (`scripts/repo-bootstrap/verify-readme-sync.sh`) catches missing fields; CD gate (`verify-readme-sync` job) catches release-time drift. KHÔNG publish package without these gates wired up. Memory `feedback_package_readme_sync.md`.
</important>

<important if="creating new repo, scaffolding standard files, OR auditing existing repo for compliance with n24q02m repo standards">
- **REPO INIT/AUDIT/RETROFIT via bootstrap scripts**: Use `n24q02m/n24q02m/scripts/repo-bootstrap/{init,audit,apply,verify,promo-sync}.sh`. 6-medium GitHub-detail audit scope (About + Code security + Settings + Webhooks + Templates + Discussions + Community Standards + Root files + README). CI gate via composite action `n24q02m/n24q02m/.github/actions/repo-bootstrap-verify@main`. Idempotent: re-running `apply.sh` is noop on aligned files. KHÔNG manual-copy template files; KHÔNG skip audit on init. Memory `feedback_repo_init_bootstrap.md`.
</important>

<important if="task có ≥3 aspect độc lập (research đa chiều, competing hypotheses, cross-layer coordination, parallel modules) VÀ không phải quick single-file fix">
- **AGENT TEAM CHỦ ĐỘNG**: Đề xuất tạo team 3-5 teammate (sweet spot, ≥6 diminishing) thay vì chỉ subagent. 4 patterns + Windows constraints + token cost: `~/.claude/skills/superpower-private-repo/references/agent-team-patterns.md`. Memory `feedback_agent_teams_proactive.md`.
</important>

## 1.5. TOOL SELECTION HIERARCHY

| Task | Default | Special |
|------|---------|---------|
| Plan/spec writing | `superpowers:writing-plans` | MCP work → `mcp-dev` first |
| Brainstorming | `superpowers:brainstorming` | — |
| Plan ambition review | `gstack:plan-ceo-review` | — |
| Plan engineering review | `gstack:plan-eng-review` | — |
| Feature design | `feature-dev:code-architect` agent | — |
| Codebase exploration | `feature-dev:code-explorer` agent | — |
| Code review (local) | `gstack:review` | Heavy → `pr-review-toolkit:review-pr` |
| PR specialized | `pr-review-toolkit` agents (silent-failure-hunter / type-design-analyzer / pr-test-analyzer / comment-analyzer / code-simplifier) | — |
| Security review | `security-guidance` hook + `/security-review` | — |
| Debugging | `superpowers:systematic-debugging` | — |
| TDD | `superpowers:test-driven-development` | — |
| Plan execution | `superpowers:executing-plans` OR `subagent-driven-development` | — |
| Skill writing | `superpowers:writing-skills` | — |
| Plugin packaging | `plugin-dev` | — |
| Hook building | `hookify` | — |
| CLAUDE.md update | Manual edit | Bulk → `claude-md-management:claude-md-improver` |
| UI/frontend gen | `frontend-design` plugin | Personal → `gstack:design-*` or `ui-ux-pro-max` |
| MCP server work | `mcp-dev` | — |
| Infra/CI/CD | `infra-devops` | — |
| AI/ML/RAG | `ai-ml` | — |
| Headless QA | `gstack:qa` / `gstack:qa-only` | — |
| Bug bounty | `claude-bug-bounty` (vendor install) | — |
| Browser debug | `chrome-devtools-mcp:*` | — |
| Loop runner | `ralph-loop:*` or native `/loop` | — |
| Session log lookup | `session-transcript-extraction` | — |
| Ship workflow | `gstack:ship` | — |

## 1.6. NGUYÊN TẮC CODING (KARPATHY)
- **Surface assumptions, KHÔNG pick silently**: Trước khi code, state assumption; nếu có nhiều interpretation, liệt kê tất cả và hỏi, KHÔNG tự chọn một hướng rồi code 200 dòng.
- **Surgical diff**: Mỗi dòng thay đổi PHẢI trace trực tiếp về yêu cầu user. KHÔNG drive-by refactor (đổi quote style, thêm type hint, reformat, "improve" comment adjacent). Match existing style của file kể cả khi muốn khác. Dead code pre-existing: mention, đừng xoá.
- **Simplicity before speculation**: KHÔNG abstraction cho single-use, KHÔNG "flexibility/configurability" chưa được yêu cầu, KHÔNG error handling cho kịch bản bất khả thi. "Production-grade" != "over-engineered upfront" — scalable khi requirement thật sự xuất hiện, không phải preemptive Strategy pattern. Nguồn: https://github.com/forrestchang/andrej-karpathy-skills

## 2. CHUẨN MỰC CODE
- **KHÔNG** dùng emoji trong code/tài liệu kỹ thuật.
<important if="committing code or creating commits">
- **Commits**: CHỈ dùng `fix:` và `feat:` prefix. **KHÔNG BAO GIỜ** dùng `chore:`, `docs:`, `refactor:`, `ci:`, `build:`, `style:`, `perf:`, `test:` hay bất kỳ type nào khác. **KHÔNG BAO GIỜ** dùng `!` (breaking change indicator). **KHÔNG BAO GIỜ** skip pre-commit hooks (`--no-verify`, `--no-gpg-sign`).
</important>
<important if="discussing release version, picking version number, writing changelog, planning release, or anything related to semantic versioning">
- **PSR AUTO-VERSION**: Đọc skill `infra-devops/references/semantic-release.md` section "Anti-pattern: Tự pick version số trong spec/plan/PR" TRƯỚC khi viết spec/plan/PR có version. Tóm tắt: KHÔNG tự pick `v0.1.0`/`v1.0.0` — dùng placeholder `<auto>`. Memory `feedback_psr_auto_version.md`.
</important>
- **API**: REST + OpenAPI (Orval). **Test Coverage**: ≥ 95%.
- **Type-Safe SQL**: Python (SQLModel + Alembic), Go (sqlc + golang-migrate), TS (Drizzle).
- **DataFrames**: `polars` only. **Data Files**: JSONL format bắt buộc.
- **Security**: **KHÔNG BAO GIỜ** commit real credentials (phone, API keys, tokens, passwords). Luôn dùng placeholders. Dùng Doppler/Infisical/skret.
<important if="adding/moving/planning a secret in Doppler/Infisical/skret/SSM/any KV store, OR mapping runtime envs (dev/staging/prod) to secret-store namespaces, OR migrating between secret managers">
- **SECRET-ENV TAXONOMY (universal, 2 namespaces only)**: Secret manager (Infisical/skret/SSM/Doppler) có 2 envs: `dev` (local laptop ONLY) + `prod` (shared bởi cả prod + staging runtimes). Staging runtime deploy đọc từ cùng `prod` secret env; key khác biệt giữa prod và staging (Test Mode ID, staging DB password, beta host) dùng suffix `<PREFIX>_STAGING_<NAME>` trong chính `prod` namespace. **TUYỆT ĐỐI KHÔNG** tạo namespace thứ 3 `staging` — silent drift trap. Runtime-env taxonomy (dev + staging + prod deploys) ORTHOGONAL với secret-env — branch CD vẫn tag `:staging`, Watchtower vẫn pull, frontend vẫn auto-detect. Xem memory `feedback_env_taxonomy.md` + skill `infra-devops/references/security.md`.
</important>
- **skret CLI**: Auth qua `~/.aws/credentials` (IAM user `skret-vm-runtime` trên VM, hoặc personal AWS credentials trên dev laptop). Region `ap-southeast-1`. KHÔNG cần interactive login — boto3-style credential chain. `skret env -e prod --path=/<namespace>/prod --format=dotenv` để export, `skret run -e prod -- <cmd>` để run với secrets injected. Xem skill `infra-devops/references/security.md`.
<important if="cần read/write/list secret bất kỳ namespace SSM/Doppler/Infisical, HOẶC sắp gõ `aws ssm get-parameter`/`describe-parameters`/`put-parameter`">
- **DÙNG `skret`, KHÔNG `aws ssm` TRỰC TIẾP**: Mọi secret op (read/write/list) BẮT BUỘC qua `skret env`/`skret run`/`skret put`. CẤM `aws ssm get-parameter`, `aws ssm put-parameter`, `aws ssm describe-parameters` (bypass abstraction → backend coupling, audit gap, expose keys ngoài scope sandbox). Git Bash mangle path `--path=/foo` thành `C:/Program Files/Git/foo` → dùng `MSYS_NO_PATHCONV=1` prefix HOẶC chạy từ PowerShell, KHÔNG fallback `aws ssm`. Skret trống = backend trống (skret đọc cùng SSM), KHÔNG "double-check" qua `aws ssm`. Xem memory `feedback_skret_not_aws_ssm.md`. Vi phạm 2026-04-28 KP CNAME hunt: chạy `aws ssm describe-parameters --parameter-filters Values=/global` để hunt CF zone-edit token.
</important>
<important if="cần admin-level credential (DNS zone edit, CF account-wide token, GitHub org-admin PAT, IAM bootstrap, billing/registrar API), HOẶC định grep skret app namespace cho token loại này">
- **APP SKRET NAMESPACE = RUNTIME ONLY, KHÔNG hunt admin token ở đó**: `/<app>/prod` chỉ chứa secret app code ĐỌC LÚC RUNTIME (DB DSN, upstream API key app gọi, OAuth client secret app exchange, R2 keys app upload). Admin op (zone:edit, account-wide token, registrar API, billing API, org-admin PAT) KHÔNG nằm trong app namespace — putting them there expand blast radius (runtime exploit → DNS hijack). Trước khi grep skret, hỏi: "App runtime code có CALL credential này không?". Nếu KHÔNG → không hunt, chọn 1 trong: (a) user edit dashboard 30 giây, (b) user mint scoped token paste 1 lần, (c) tạo admin-only namespace `/admin-<scope>/prod` nếu recurring (vẫn không phải app namespace). Vi phạm 2026-04-28: hunt CF Zone:Edit token trong `/KnowledgePrism/prod` + `/oci-vm-infra/prod` + `/global/prod` (KP app không edit DNS — token không có ở đó). Xem memory `feedback_app_namespace_runtime_only.md` + `feedback_cf_global_token.md` (updated).
</important>
- **gh CLI list commands**: **LUÔN** pass `--limit 1000` cho `gh pr list`, `gh issue list`, `gh run list`, `gh release list`. Default 30/20 → miss items → sai metric. Với audit/security/release gates → dùng default = BUG. Xem memory `feedback_gh_cli_pagination.md`.
- **Google OAuth "Desktop/Installed app" client_secret = PUBLIC secret**: Client secret `GOCSPX-...` dùng trong Desktop OAuth flow (wet-mcp GDrive sync, uvx-installable apps) được Google chính thức coi là **public** — không phải credential thật. Quote Google docs (https://developers.google.com/identity/protocols/oauth2#installed): *"Installed applications are considered public clients and they cannot protect client secrets."* Hệ quả: (a) KHÔNG mark là "leaked secret" khi thấy `GOCSPX-...` hardcoded trong source của installed/desktop app, (b) KHÔNG propose rotation (vô nghĩa — user cài local luôn có secret trong binary), (c) secret scanner alert cho Desktop OAuth client = FALSE POSITIVE, dismiss với lý do "Google Desktop public client pattern". PHÂN BIỆT với **Web server OAuth client_secret** (Notion OAuth server-delegation, v.v.) — cái đó PRIVATE thật, LEAK = rotate ngay. Kiểm tra type qua GCP Console → OAuth 2.0 Client IDs → "Application type: Desktop app" (public) vs "Web application" (private). wet-mcp GDrive sync dùng Desktop type → public, mnemo-mcp KHÔNG hardcode secret (default empty, user tự cung) → không liên quan. Xem memory `feedback_google_oauth_desktop_public.md`.
- **SAST**: Private repos dùng **Semgrep**. Public repos dùng **CodeQL**. **KHÔNG BAO GIỜ** dùng ngược.
- **VM Deploy**: **KHÔNG BAO GIỜ** chạy `docker compose` trực tiếp trên VM. Luôn dùng `make up-<service>` / `make down-<service>` (inject secrets từ skret SSM qua RUN macro). **KHÔNG BAO GIỜ** `make up` / `make down` toàn bộ — chỉ thao tác từng service cụ thể. Dùng `make up-*` (không phải `restart-*`) khi thay đổi env vars.

## 3. E2E TESTING (MCP SERVERS)
- **MCP protocol**: Test qua `mcp.ClientSession` + `stdio_client` (initialize → tools/list → tools/call). **KHÔNG BAO GIỜ** import Python functions trực tiếp.
- **Source code**: Chạy server từ source (`uv run wet-mcp`, `uv run --directory . wet-mcp`). **KHÔNG** dùng PyPI/plugin đã install.
- **Relay flow**: Mỗi server PHẢI test relay — clean state (xóa config.enc, unset env vars) → start server → relay URL hiển thị ở stderr → user vào browser config → verify server nhận config.
- **Clean state**: Xóa `~/.config/mcp/config.enc` (hoặc platformdirs equivalent), unset env vars, xóa discovery files trước mỗi test.
- **TẤT CẢ tools**: Test mọi action/mode, không chỉ 1-2 demo. Test concurrent calls cho scenarios deadlock.
- **Real credentials**: Dùng credentials thật (từ skret SSM hoặc user cung cấp), không mock.
- **Trực tiếp 1-1**: Làm trực tiếp với user, KHÔNG chạy background rồi báo kết quả.
- **KHÔNG** dùng `/reload-plugins` để test — không liên quan đến MCP server testing.

- **AI Traces (.jules & superpower)**: Trước khi viết/commit spec/plan/roadmap hay scaffold AI traces vào BẤT KỲ repo nào, đọc skill `superpower-private-repo` (đã cover: gitignore patterns, private repo location `.superpower/<X>/`, rotation fallback, cleanup options A/B nếu lỡ commit vào public). Tóm tắt: spec/plan của public repo PHẢI lưu vào `~/projects/.superpower/<X>/`, KHÔNG vào `<X>/docs/superpowers/`.