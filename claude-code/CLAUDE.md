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
- **WORK ORDER BẤT BIẾN: CLEAR BACKLOG → E2E → RELEASE (CUỐI CÙNG CỦA CUỐI CÙNG)**: Trong session multi-step có fix + release, trình tự BẮT BUỘC: (1) Hoàn thành MỌI fix + **EMPTY BACKLOG toàn scope**: PRs=0 + issues=0 + Sentinel/Bolt/Daisy/Jules bot PRs=0 + dependabot=0 + codeql=0 + secret scan=0 + cred rotations pending=0 trên TẤT CẢ repo trong scope → (2) Chạy ONE comprehensive E2E full/real/live test → (3) CHỈ sau khi test pass toàn bộ mới dispatch release CD. TUYỆT ĐỐI KHÔNG "Phase X feature done = ready for E2E" khi còn 100+ open PRs. TUYỆT ĐỐI KHÔNG release giữa chừng rồi test sau. Vi phạm → broken releases + downstream pin drift + rework cascade. Verify backlog bằng: `gh pr list --limit 1000 --state open` + `gh issue list --limit 1000 --state open` + `gh api repos/<>/dependabot/alerts` (xem `feedback_gh_cli_pagination.md` — LUÔN --limit 1000). Xem memory `feedback_work_order_fix_test_release.md`.
</important>
<important if="merging, closing, or approving ANY pull request — đặc biệt bot PRs (Jules/Sentinel/Bolt/Daisy/Renovate/Dependabot)">
- **PR REVIEW PHẢI THẬT**: BẮT BUỘC đọc **FULL diff** toàn bộ file changes TRƯỚC KHI merge/close/approve, KHÔNG dừng ở title/description. Từng file, từng hunk, cross-check scope với PR title. Diff chứa changes NGOÀI scope title → REJECT + request tách PR. Bot PRs (đặc biệt Jules/Sentinel/Bolt) thường rebase trên old main hoặc kèm collateral damage (xoá file, revert feature, đổi default). CI green = chỉ verify build+test, KHÔNG verify scope. "Backlog cleanup quick merge" = ANTI-PATTERN. Vi phạm 2026-04-19: Jules PR #517 title `[FIX] Missing Cache` nhưng diff thực tế revert remote-oauth mode + xoá `src/auth/notion-token-store.ts` + revert `config.ts→setup.ts` → phá mode matrix notion → phát hiện ở E2E staging. Xem memory `feedback_pr_review_must_be_real.md` (kèm liên kết 4 feedback gốc về PR review).
</important>
<important if="releasing a core/shared/dependency repo (mcp-core, web-core, qwen3-embed, hoặc package khác mà repo khác pin/depend vào)">
- **CORE RELEASE → AUTO-ISSUE DOWNSTREAM**: Mỗi khi core/shared repo cut stable release mới, CD pipeline BẮT BUỘC auto-create tracking issue ở MỌI downstream repo với title dạng `chore: bump <core-pkg> to <new-version>` + body chứa changelog link + current pin detection. Prevents drift khi downstream pin `^1.0.0` nhưng core đã `1.1.1` (manual bump hay bị miss). Implementation: CD workflow step dùng `gh api repos/<downstream>/issues` hoặc `gh issue create -R <downstream>`. Phải cover tất cả consumers (VD mcp-core: 7 MCPs; web-core: KP + downstream apps). Xem memory `feedback_core_release_auto_issue.md`.
</important>
<important if="writing spec, plan, roadmap, architecture document, migration plan, or implementation plan">
- **SPEC/PLAN/ROADMAP → SUPERPOWER**: BẮT BUỘC invoke `Skill` tool với `superpowers:writing-plans` (hoặc `superpowers:brainstorming` cho ideation, `superpowers:executing-plans` cho execution) **TRƯỚC KHI** gõ bất kỳ nội dung spec/plan/roadmap/architecture/migration nào. KHÔNG freehand. Skill enforce structured thinking, verify-before-claim, test-first mindset, review checkpoint. Xem memory `feedback_spec_plan_superpower.md`. Trigger keywords: "viết spec/plan/roadmap/migration/architecture", "rewrite spec", "execution plan", "implementation plan".
</important>
<important if="receiving user feedback that changes scope, overrides a spec decision, adds/removes requirements, or corrects a misunderstanding">
- **FEEDBACK → UPDATE SPEC + PLAN**: Khi user đưa feedback quan trọng (thay đổi scope, override spec decision, thêm/bỏ requirement), PHẢI cập nhật cả spec + plan document TRƯỚC, KHÔNG chỉ ghi memory. Memory là ghi chú bổ sung, spec + plan là source of truth. Nếu chỉ update memory mà không update spec/plan, agent sẽ tiếp tục follow spec cũ (sai). Quy trình: feedback → (1) update spec/plan → (2) ghi memory → (3) implement. **KHÔNG BAO GIỜ** implement dựa trên memory mà contradict spec chưa được update.
</important>
<important if="producing spec, plan, model artifact, dataset, eval result, or any deliverable that might be released publicly">
- **PROD-LEVEL / INDUSTRY-LEVEL / PUBLIC-READY**: Mọi deliverable viết từ đầu với giả định sẽ release public (HuggingFace Hub, GitHub, arXiv) — industry best practice, fully consolidated, reproducible. **KHÔNG** expose: Infisical project ID, Modal workspace name, personal email, internal infra hostnames, API keys, MLflow internal URLs, private CF Tunnel hostnames. Luôn dùng placeholder `<workspace>`, `<project-id>`, `<your-email>`. License clear (MIT/Apache-2.0 cho code, CC-BY-4.0/ODC-BY cho datasets). Model card + dataset card theo HF template. Eval phải reproducible với public benchmarks (BEIR, MMEB, MIRACL, MMDocIR, ViDoRe, AudioCaps, CMTEB). Không bao giờ hardcode secrets vào spec/plan/artifact.
</important>
<important if="reading screenshots, dashboard images, rate limit tables, pricing tables, leaderboard images, or any dense-text image from user">
- **IMAGE → OCR, KHÔNG raw vision**: Claude vision tệ với dense text/tables/số liệu. BẮT BUỘC chạy OCR (`tesseract` sau khi upscale 3x LANCZOS + grayscale) trước khi claim bất kỳ số/text nào từ ảnh. Nếu chưa cài: `winget install UB-Mannheim.TesseractOCR` (Windows) hoặc `apt install tesseract-ocr` (Linux). Khi `imagine-mcp` (WS-7) ready → ưu tiên dùng (Gemini/OpenAI/Grok vision mạnh hơn). Chỉ bỏ OCR khi ảnh đơn giản 1-2 elements UI. Xem memory `feedback_image_ocr_vision.md`.
</important>
<important if="user share file HTML/htm/.part >200KB, folder 'save as complete page' có CSS+JS+images companion, Arena/lmarena.ai chat export, AI Studio conversation export, hoặc browser archive">
- **WEB EXPORT → INVOKE SKILL `reading-web-exports`**: KHÔNG `Read` HTML >1MB trực tiếp (token limit fail). KHÔNG cố `grep -oE '<p>...'` (miss multi-line, nested, entities). KHÔNG tải folder companion (CSS/JS/PNG = asset offline, zero content value). BẮT BUỘC invoke skill → strip `<script>`/`<style>` → `html.parser` extract → dedupe → save `extracted.txt` → Read bình thường. Windows PHẢI `PYTHONIOENCODING=utf-8` tránh crash cp1252 với Vietnamese. Xem skill `reading-web-exports` cho template script + anti-patterns.
</important>
<important if="dispatching subagent, Agent tool, Task tool sub-invocation, or executing plan via superpowers:subagent-driven-development">
- **VERIFY SUBAGENT OUTPUT**: Subagent summary là INTENT không phải RESULT. BẮT BUỘC verify thực tế trước khi mark task completed hoặc báo user: (1) Read lại file cho code edits (git diff so pre-dispatch), (2) Chạy lại test command trong session chính (không trust "tests pass" từ subagent), (3) `git log -1 --stat` confirm commit SHA + prefix `fix:`/`feat:` + file list, (4) `curl` endpoint + check logs cho deploy, (5) Spot-check citations cho research agent. Nếu verify fail → dispatch lại với corrective prompt, KHÔNG skip. Xem memory `feedback_verify_subagent_output.md`.
</important>
<important if="fixing bug phát sinh trong E2E test, deployment, hoặc hệ thống đang chạy">
- **FIX ROOT CAUSE + VERIFY SCENARIO**: BẮT BUỘC đủ 3 bước (1) xác định root cause, (2) fix root cause trong code (KHÔNG workaround hay "bảo user close tab"), (3) **RE-RUN chính xác scenario đã gây bug** để verify fix thật sự hoạt động → TRƯỚC KHI move on hoặc test phần khác. Ví dụ: nếu fix là timing race trong relay → re-run full relay flow + check browser UI update, không "probably works, move on". Anti-pattern cấm: "Fixed timing, tiếp server khác", "Close tab đi, config đã saved", "Test tương tự rồi, probably OK". Xem memory `feedback_fix_root_cause_verify.md`.
</important>
<important if="editing ANY file under ~/.claude/ (CLAUDE.md, agents/*, skills/*, commands/*, hooks/*, settings.json) OR writing rule/skill content">
- **~/.claude/ SYNC LÊN REPO PUBLIC `n24q02m/n24q02m`**: TUYỆT ĐỐI KHÔNG ghi credential, secret, API key, token, real email cá nhân, IP cụ thể (Tailscale, public, internal), hostname nội bộ, machine identity ID prefix, CF/GCP account ID, project ID Infisical, database URL có host, OAuth client ID, hay bất kỳ value cụ thể nào của infra/cred vào BẤT KỲ file nào trong `~/.claude/`. Tất cả đồng bộ public lên GitHub → leak permanent vào git history. Khi rule cần reference cred/infra → CHỈ trỏ đến memory entry name (`xem memory feedback_xxx.md`), KHÔNG inline value. Memory file ở `<project>/memory/*.md` (local, KHÔNG sync) mới được chứa value cụ thể. Anti-pattern cấm trong `~/.claude/`: ghi prefix Client ID, IP `100.x.y.z`, email `<user>@<domain>`, URL `https://*.staging.xxx.com`, account ID. Trước khi save bất kỳ edit nào tới `~/.claude/`, tự audit: file này có chứa value cụ thể không? Nếu có → REPLACE bằng placeholder + reference memory. Xem memory `feedback_claude_md_public_sync.md`.
</important>
<important if="sắp hỏi user về credential, API token, secret, machine identity, account ID, IP, hostname, SSH access, deploy access, staging/prod URL, test user, hoặc bất kỳ infra detail nào">
- **MEMORY-FIRST: ĐỌC MEMORY TRƯỚC KHI HỎI**: BẮT BUỘC scan MEMORY.md (luôn load ở context system prompt) + read entry liên quan TRƯỚC KHI hỏi user về bất kỳ cred/secret/infra detail nào. Workflow: keyword trong câu hỏi (Infisical/CF/Firebase/Tailscale/SSH/staging/prod/e2e/deploy/Yoti/Doppler/...) → grep MEMORY.md index → read tương ứng `feedback_*.md` hoặc `*-credentials.md` hoặc Infrastructure section → chỉ hỏi nếu thật sự thiếu hoặc cred MỚI. Memory đã có sẵn nhiều entries cho infra (Infisical machine identity, CF tokens, Firebase test creds, Tailscale hostnames, Doppler config, …) — DÙNG NGAY, không hỏi xác nhận. Vi phạm khi user phải nhắc "đã có ở memory rồi" → tự kiểm điểm + nếu memory stale thì update. Xem memory `feedback_memory_first_before_ask.md`.
</important>
<important if="user references prior session by name, mentions previous conversation, says 'session trước', 'đã nói', 'đề xuất đã được nói', 'như đã chốt', hoặc cần recall điều gì đã trao đổi ở session khác">
- **SESSION LOG LOOKUP**: Invoke skill `session-transcript-extraction` (đã cover: tìm session JSONL, parse, extract user+assistant đầy đủ, output transcript+history). KHÔNG hỏi user "session nào?" trước khi tự tìm. Check MEMORY.md `session-*-transcript.md` index trước — có thể đã summary sẵn. Memory `feedback_session_log_lookup.md`.
</important>
<important if="cần CLI auth state hoặc test account (Firebase, gh, gcloud, wrangler, Doppler, Infisical, npm, vercel, dodo, ...) hoặc sắp hỏi user 'đã login chưa?' / 'cần creds gì?'">
- **CLI ALREADY LOGGED IN + TEST ACCOUNTS PERSIST**: Auth state của CLI tools (Firebase `firebase login`, gh `gh auth status`, gcloud `gcloud auth list`, wrangler `wrangler whoami`, Doppler `doppler configure`, Infisical universal-auth) DUY TRÌ ACROSS SESSIONS — KHÔNG hỏi user "đã login chưa". Tự kiểm tra trước qua command (`<cli> auth status` / `whoami` / `login:list`). Test accounts (Firebase test users, Stripe/Dodo test customers, e2e accounts) đã được đăng ký/đăng nhập sẵn — credentials lưu ở memory entry tương ứng (e.g. `e2e-test-credentials.md`). Nếu chưa có entry: tự register/create + LƯU NGAY vào memory để session sau dùng lại, KHÔNG ask user mỗi lần. Workflow: (1) check CLI auth state via command; (2) check memory cho test account creds; (3) nếu thiếu → create + save memory + use; (4) chỉ ask user khi service mới chưa có account (như Yoti SDK signup). Vi phạm 2026-04-18 — hỏi "Firebase user nào?" trong khi CLI đã login + e2e user đã tồn tại nhiều lần. Xem memory `feedback_cli_state_test_accounts_persist.md`.
</important>
<important if="có PR sẵn sàng merge (CI green) VÀ session có release/E2E trong scope VÀ repo là private cá nhân KHÔNG có auto-CD">
- **MERGE TRƯỚC, E2E TRÊN MAIN, RELEASE CUỐI**: Private repos cá nhân (n24q02m/*) có CD là `workflow_dispatch` thủ công → KHÔNG auto-deploy. Thứ tự BẮT BUỘC: (1) CI green → MERGE PR NGAY, (2) E2E chạy TRÊN main (pull main), (3) CD stable dispatch CUỐI session. Anti-pattern cấm: "E2E với file: pin trên branch trước khi merge", "merge + release incrementally", "test 1 repo release 1 repo". Lý do: merge main an toàn 100% (không auto-release), test trên `file:` pin không reflect thực tế. Với dep bump (vd mcp-core v1.3.0 → downstream ^1.3.0), bump version TRƯỚC khi merge (tránh commit file: pin vào main). Xem memory `feedback_test_before_release.md` + `feedback_work_order_fix_test_release.md`. Vi phạm 2026-04-18 session 4739cb45.
</important>
<important if="phát hiện bug/security issue trong session hiện tại (E2E test, code review, deployment)">
- **CẤM "ĐỂ FIX SAU"**: Khi phát hiện bug hoặc security issue trong session đang chạy, BẮT BUỘC fix NGAY trong session đó, KHÔNG được note "fix sau", "Phase M.2", "next cycle", "tracking issue cho later". Anti-patterns cấm: "em note vào CLAUDE.md để fix sau", "file issue + move on", "upstream bug, not blocking", "note memory for future session". Rule áp dụng cho: (a) security issues (credential leak, SSRF, injection), (b) broken user flows (relay bug, OAuth flow, auth flow), (c) data loss risks, (d) bugs đã xác định root cause. Chỉ được defer khi fix cần coordination >= 2 engineers hoặc cần infra change (user explicitly approve). Memory `feedback_never_defer_tasks.md` đã có, rule này strengthen + expand scope. Vi phạm 2026-04-18 khi note core-ts relay bug + bot token leak + telegram OTP broken "để fix sau".
</important>
<important if="editing, auditing, testing, releasing, or developing ANY của 12 repo MCP stack (mcp-core / better-notion-mcp / better-email-mcp / better-telegram-mcp / wet-mcp / mnemo-mcp / better-code-review-graph / better-godot-mcp / qwen3-embed / web-core / claude-plugins / n24q02m) — HOẶC multi-repo backlog+E2E+release cascade">
- **MCP WORK → BẮT BUỘC INVOKE `Skill mcp-dev` TRƯỚC KHI HÀNH ĐỘNG**: Skill `~/.claude/skills/mcp-dev/` là canonical source cho MCP workflow. 14 reference files cover: scope-and-repos, mode-matrix, tool-layout (N+2), config-parity, relay-flow, reuse-mcp-core, audit-commands (`--limit 1000`), backlog-allowlist, backlog-clearance, clean-state, e2e-full-matrix (24 configs: 20 MCP + 4 non-MCP), release-cascade, non-mcp-repos, readme-parity. KHÔNG freehand, KHÔNG guess mode/config/data-store, KHÔNG shortcut E2E qua env var, KHÔNG release giữa chừng, KHÔNG skip backlog gate, KHÔNG bulk-close PRs. Memory `feedback_mcp_*` + `scope-12-repos` + `mcp-server-data-stores` = incident log (why); skill = how-to-apply (authoritative). Vi phạm → rework cascade. Xem memory `feedback_mcp_dev_skill.md`.
</important>
<important if="cần tìm scope repo (MCP stack, cross-repo audit, backlog cleanup, README rollout, release cascade, dogfood) hoặc sắp hardcode list tên repo vào spec/plan/rule">
- **REPO SCOPE = 2 GITHUB STARS LISTS**: Canonical source cho "repo nào thuộc scope" luôn là 2 lists của `n24q02m`: **Productions** (`https://github.com/stars/n24q02m/lists/productions`) — user-facing OSS + private apps; **Scripts** (`https://github.com/stars/n24q02m/lists/scripts`) — infra + tooling + profile. KHÔNG hardcode "17 repos" / "12 repos" / "15 repos" vào spec/plan/rule — scope drift theo thời gian. Fetch qua `gh api graphql -f query='query { viewer { lists(first:10) { nodes { name items(first:100) { nodes { ... on Repository { nameWithOwner isPrivate isArchived } } } } } } }'` (REST + web đều trả 404 cho Stars lists, phải GraphQL với `viewer.lists`). Khi viết spec/plan/rule multi-repo: (1) fetch lists ngay đầu, (2) snapshot scope kèm ngày, (3) reference lists thay vì hardcode. Xem skill `infra-devops/references/repo-structure.md` "Tier 1/Tier 2" + `mcp-dev/references/readme-parity.md` cho breakdown. Memory `scope-12-repos.md` vẫn valid cho MCP stack con của Productions; lists là superset.
</important>
<important if="bắt đầu task mới hoặc trước khi hỏi user clarifying question khi đang làm việc trên domain có sẵn skill">
- **SKILL-FIRST — INVOKE SKILL TRƯỚC KHI ASK / CODE**: Task thuộc domain có skill tương ứng thì PHẢI invoke `Skill` tool TRƯỚC KHI ask user clarifying question hoặc bắt đầu code. KHÔNG hỏi user điều đã được document trong skill references. Skill list in system prompt mỗi session. Common mappings:
  - MCP servers / web / mobile / desktop / API / game dev → `fullstack-dev`
  - Infra / CI/CD / Docker / PSR / repo structure / secrets / security → `infra-devops`
  - RAG / embedding / reranker / training / MLflow → `ai-ml`
  - UI/UX design → `ui-ux-pro-max`
  - Claude API / Anthropic SDK / prompt caching → `claude-api`
  - Product / pricing / marketing / growth → `product-growth`
  - Spec / plan / roadmap / brainstorm → `superpowers:writing-plans` / `superpowers:brainstorming`

**Why:** 18/04/2026 em định thêm rule mới về MCP tool standard vào CLAUDE.md + memory mà không check skill `fullstack-dev/references/mcp-server.md` đã có section "Standard Tool Set" (chỉ cần UPDATE, không phải tạo rule mới). User phải nhắc 2 lần. Rule bloat + skill stale = antipattern cost long-term context.

**How to apply:**
1. Bắt đầu task → scan system prompt skill list → match domain → invoke skill NGAY.
2. Skill reference đã cover topic → đọc reference file, KHÔNG freehand lại hay duplicate vào rule.
3. Content đã có trong skill nhưng outdated → UPDATE skill reference file, KHÔNG tạo rule mới bypass.
4. Rule trong CLAUDE.md CHỈ là short trigger + pointer đến skill reference, KHÔNG inline content dài.
5. Trước khi định thêm rule mới: tự hỏi "content này thuộc skill nào? Skill đó đã có section tương ứng chưa?" → default answer là **SKILL**, rule chỉ là pointer.
</important>

## 1.5. NGUYÊN TẮC CODING (KARPATHY)
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
- **Security**: **KHÔNG BAO GIỜ** commit real credentials (phone, API keys, tokens, passwords). Luôn dùng placeholders. Dùng Doppler/Infisical.
- **Infisical CLI**: **KHÔNG BAO GIỜ** dùng `infisical login` interactive. Auth qua universal-auth API → `--token` flag. Phải get token VÀ dùng token trong CÙNG MỘT bash call (env vars mất giữa các calls).
- **gh CLI list commands**: **LUÔN** pass `--limit 1000` cho `gh pr list`, `gh issue list`, `gh run list`, `gh release list`. Default 30/20 → miss items → sai metric. Với audit/security/release gates → dùng default = BUG. Xem memory `feedback_gh_cli_pagination.md`.
- **Google OAuth "Desktop/Installed app" client_secret = PUBLIC secret**: Client secret `GOCSPX-...` dùng trong Desktop OAuth flow (wet-mcp GDrive sync, uvx-installable apps) được Google chính thức coi là **public** — không phải credential thật. Quote Google docs (https://developers.google.com/identity/protocols/oauth2#installed): *"Installed applications are considered public clients and they cannot protect client secrets."* Hệ quả: (a) KHÔNG mark là "leaked secret" khi thấy `GOCSPX-...` hardcoded trong source của installed/desktop app, (b) KHÔNG propose rotation (vô nghĩa — user cài local luôn có secret trong binary), (c) secret scanner alert cho Desktop OAuth client = FALSE POSITIVE, dismiss với lý do "Google Desktop public client pattern". PHÂN BIỆT với **Web server OAuth client_secret** (Notion OAuth server-delegation, v.v.) — cái đó PRIVATE thật, LEAK = rotate ngay. Kiểm tra type qua GCP Console → OAuth 2.0 Client IDs → "Application type: Desktop app" (public) vs "Web application" (private). wet-mcp GDrive sync dùng Desktop type → public, mnemo-mcp KHÔNG hardcode secret (default empty, user tự cung) → không liên quan. Xem memory `feedback_google_oauth_desktop_public.md`.
- **SAST**: Private repos dùng **Semgrep**. Public repos dùng **CodeQL**. **KHÔNG BAO GIỜ** dùng ngược.
- **VM Deploy**: **KHÔNG BAO GIỜ** chạy `docker compose` trực tiếp trên VM. Luôn dùng `make up-<service>` / `make down-<service>` (inject secrets từ Doppler + Infisical). **KHÔNG BAO GIỜ** `make up` / `make down` toàn bộ — chỉ thao tác từng service cụ thể. Dùng `make up-*` (không phải `restart-*`) khi thay đổi env vars.

## 3. E2E TESTING (MCP SERVERS)
- **MCP protocol**: Test qua `mcp.ClientSession` + `stdio_client` (initialize → tools/list → tools/call). **KHÔNG BAO GIỜ** import Python functions trực tiếp.
- **Source code**: Chạy server từ source (`uv run wet-mcp`, `uv run --directory . wet-mcp`). **KHÔNG** dùng PyPI/plugin đã install.
- **Relay flow**: Mỗi server PHẢI test relay — clean state (xóa config.enc, unset env vars) → start server → relay URL hiển thị ở stderr → user vào browser config → verify server nhận config.
- **Clean state**: Xóa `~/.config/mcp/config.enc` (hoặc platformdirs equivalent), unset env vars, xóa discovery files trước mỗi test.
- **TẤT CẢ tools**: Test mọi action/mode, không chỉ 1-2 demo. Test concurrent calls cho scenarios deadlock.
- **Real credentials**: Dùng credentials thật (từ Infisical hoặc user cung cấp), không mock.
- **Trực tiếp 1-1**: Làm trực tiếp với user, KHÔNG chạy background rồi báo kết quả.
- **KHÔNG** dùng `/reload-plugins` để test — không liên quan đến MCP server testing.

- **AI Traces (.jules & superpower)**: Trước khi viết/commit spec/plan/roadmap hay scaffold AI traces vào BẤT KỲ repo nào, đọc skill `superpower-private-repo` (đã cover: gitignore patterns, private repo location `.superpower/<X>/`, rotation fallback, cleanup options A/B nếu lỡ commit vào public). Tóm tắt: spec/plan của public repo PHẢI lưu vào `~/projects/.superpower/<X>/`, KHÔNG vào `<X>/docs/superpowers/`.
