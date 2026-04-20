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
<important if="running E2E test cho MCP server stack hoặc testing bất kỳ MCP server nào có flow relay/OAuth/credentials">
- **E2E CLEAN STATE MỌI SERVER**: BẮT BUỘC clean state TRƯỚC KHI test mỗi server, KHÔNG skip phase 1 (relay setup) dù server đã có credentials saved từ session trước. Clean state gồm: (1) xóa entry server trong `config.enc` (hoặc xóa cả file), (2) xóa OAuth/token cache server-specific (`~/.better-email-mcp/tokens.json`, `~/.mnemo-mcp/tokens/`, `~/.wet-mcp/tokens/`, `~/.better-telegram-mcp/*.session`, v.v.), (3) xóa session lock (`$LOCALAPPDATA/mcp/relay-session-<server>.lock`). Sau clean → launch server → relay URL PHẢI xuất hiện → user submit → monitor log `state=configured` → verify MCP protocol → phase 2 tool calls. **KHÔNG có exception nào cho "đã configured"** → mục đích E2E là verify full relay flow, không phải tool integration. Xem memory `feedback_e2e_clean_state_all_servers.md`.
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
<important if="chuẩn bị E2E / live / integration test cho MCP server hoặc bất kỳ service nào có OAuth/relay/credential flow">
- **E2E = RELAY FLOW THẬT, KHÔNG INJECT ENV VAR**: E2E test PHẢI đi qua relay URL/OAuth browser/device-code/paste form — KHÔNG shortcut bằng inject env var vào test script. Infisical/Doppler creds là cho SERVER-SIDE config (deployed server dùng để delegate OAuth, gọi provider API), KHÔNG phải cho test-side bypass. Workflow đúng: (1) clean state (config.enc, token cache, session lock), (2) start server với secret manager wrap (Doppler/Infisical), (3) server thấy no user-cred → print relay URL, (4) user browser OAuth/device-code/paste, (5) server nhận callback → save → state=configured, (6) test script connect MCP + call tools + verify. Anti-patterns cấm: `infisical run -- python test.py` với cred pre-injected skip relay, `os.environ["TOKEN"] = "..."` trong test, "có env var rồi không cần qua relay". Xem memory `feedback_full_live_test.md` + `feedback_e2e_clean_state_all_servers.md` + `feedback_relay_then_protocol.md`. Vi phạm 2026-04-18 session 4739cb45: user nhắc "có env var để test thì relay vô dụng hả???".
</important>
<important if="chuẩn bị mention/propose data store, database name, env var, relay field, URL, credential name cho bất kỳ MCP server nào (wet/mnemo/crg/notion/email/telegram/godot) hoặc đề xuất user paste/setup gì trong relay form">
- **KHÔNG TỰ CHẾ DATA STORE / ENV VAR / RELAY FIELD**: TUYỆT ĐỐI KHÔNG gán database (Qdrant/Falkor/Redis/Postgres), URL, env var, cred name cho MCP server khi chưa verify. Trước khi mention:
  1. Đọc memory `mcp-server-data-stores.md` (bảng chốt 7 server).
  2. Grep source: `grep -iE 'sqlite|qdrant|falkor|postgres|redis' <repo>/pyproject.toml <repo>/CLAUDE.md`.
  3. Đọc `<repo>/src/<repo>/relay_schema.py` để biết user được hỏi field gì thật sự.
  4. Đọc `<repo>/src/<repo>/config.py` để biết env vars thực tế.

**Sự thật chốt (2026-04-18)**:
- **wet-mcp**: SearXNG **auto-start Docker trên Windows/macOS** (web-core PR #753). User KHÔNG paste URL. Default pure local ONNX. Relay form = 4 cloud API keys OPTIONAL (Jina/Gemini/OpenAI/Cohere), để trống vẫn chạy.
- **mnemo-mcp**: **SQLite + sqlite-vec** (FTS5 + vector). KHÔNG Qdrant, KHÔNG Falkor.
- **crg**: **SQLite GraphStore** (WAL, NetworkX cache). KHÔNG Qdrant, KHÔNG Falkor.
- **Qdrant + FalkorDB + SearXNG server** = **infra-vnic OCI VM cho Paperclip VC + KP**, KHÔNG cho MCP server.

Vi phạm 2026-04-18 session 4739cb45: propose user "paste SearXNG URL from Infisical", "mnemo cần Qdrant + Falkor URLs", "crg cần Qdrant URL" → tất cả SAI + lại bypass relay qua Infisical env. User scold lần thứ n. Xem memory `feedback_data_store_no_guessing.md` + `mcp-server-data-stores.md`.
</important>
<important if="phát hiện bug/security issue trong session hiện tại (E2E test, code review, deployment)">
- **CẤM "ĐỂ FIX SAU"**: Khi phát hiện bug hoặc security issue trong session đang chạy, BẮT BUỘC fix NGAY trong session đó, KHÔNG được note "fix sau", "Phase M.2", "next cycle", "tracking issue cho later". Anti-patterns cấm: "em note vào CLAUDE.md để fix sau", "file issue + move on", "upstream bug, not blocking", "note memory for future session". Rule áp dụng cho: (a) security issues (credential leak, SSRF, injection), (b) broken user flows (relay bug, OAuth flow, auth flow), (c) data loss risks, (d) bugs đã xác định root cause. Chỉ được defer khi fix cần coordination >= 2 engineers hoặc cần infra change (user explicitly approve). Memory `feedback_never_defer_tasks.md` đã có, rule này strengthen + expand scope. Vi phạm 2026-04-18 khi note core-ts relay bug + bot token leak + telegram OTP broken "để fix sau".
</important>
<important if="developing MCP servers (wet/mnemo/notion/email/telegram/godot/crg/...) hoặc thêm feature auth/relay/config vào bất kỳ MCP server nào">
- **TỐI ĐA HÓA REUSE mcp-core**: BẮT BUỘC dùng lại primitives từ `@n24q02m/mcp-core` (TypeScript) hoặc `n24q02m-mcp-core` (Python) thay vì tự implement logic tương đương trong từng MCP server. Scope:
  1. **Config storage**: dùng `write_config/read_config/delete_config` từ `mcp_core.storage.config_file` (Python) hoặc `@n24q02m/mcp-core/storage` (TS). KHÔNG duplicate logic encrypt/decrypt, platformdirs path, session lock.
  2. **Relay client**: dùng `mcp_core.relay.client.{create_session,poll_for_result,send_message}` (Python) + parity TS. KHÔNG viết HTTP POST thủ công đến relay server.
  3. **OAuth 2.1 AS**: dùng `runLocalServer` / `run_local_server` với `relay_schema`. KHÔNG tự chạy Starlette/uvicorn riêng cho OAuth form.
  4. **Browser open**: dùng `try_open_browser` / `tryOpenBrowser` từ mcp-core. KHÔNG duplicate (`execFile('rundll32'...)`, `webbrowser.open`).
  5. **Session lock**: dùng `acquire_session_lock` / `write_session_lock` / `release_session_lock` cho parallel-process safety.
  6. **Credential state machine**: dùng `CredentialState` enum, `resolve_credential_state` pattern. Multi-step flows (OTP, 2FA, Device Code) → đóng góp lên mcp-core primitives thay vì reinvent per-server.

**Why:** Phát hiện 2026-04-18: (a) better-notion-mcp + better-email-mcp code "Setup complete" fail khác với Python counterparts vì TS không dùng core-ts parity; (b) config storage path khác giữa core-py ($LOCALAPPDATA) vs core-ts ($APPDATA) vì mỗi bên tự dùng env-paths/platformdirs khác; (c) `relay-setup.ts` + `credential-state.ts` trong email-mcp duplicate OAuth device trigger.

**How to apply:**
1. Trước khi viết code trong MCP server, check xem mcp-core có primitive tương ứng chưa. Nếu có → import + reuse.
2. Nếu mcp-core THIẾU primitive → **đóng góp lên mcp-core TRƯỚC** (add to `packages/core-py` + `packages/core-ts` với parity tests), release mcp-core version, rồi dùng từ MCP server. KHÔNG copy-paste logic vào MCP server.
3. Parity bắt buộc: mọi primitive phải có cả Python (core-py) và TypeScript (core-ts) implementation + test vectors cross-check. Vi phạm parity → bug cross-language (e.g. config storage path).
4. Khi fix bug trong 1 primitive → fix parallel trong cả core-py + core-ts. Never fix 1 side only.</important>
<important if="developing, testing, releasing, or auditing MCP servers (notion/email/telegram/wet/mnemo/crg/godot) — transport mode selection và default">
- **MCP MODE MATRIX (chuẩn đã chốt ở session trước, KHÔNG thay đổi, KHÔNG bịa mode mới)**: Mỗi MCP server có tập mode cố định + default mode cố định. Không server nào được có mode ngoài list. Không được "tự nhiên thêm mode" hay "rename mode". Source of truth:

| Server | Default (auto-install / recommended manual) | Các mode khác hỗ trợ |
|---|---|---|
| **better-notion-mcp** | `http remote oauth` | `http local relay`, `stdio proxy` |
| **better-telegram-mcp** | `http remote relay` | `http local relay`, `stdio proxy` |
| **better-email-mcp** | `http remote relay` | `http local relay`, `stdio proxy` |
| **wet-mcp** | `http local relay` | `http remote relay` (self-host), `stdio proxy` |
| **mnemo-mcp** | `http local relay` | `http remote relay` (self-host), `stdio proxy` |
| **better-code-review-graph** | `http local relay` | `http remote relay` (self-host), `stdio proxy` |
| **better-godot-mcp** | `http local non-relay` | `stdio proxy` |

**Ý nghĩa "default"**: mode được kích hoạt tự động khi user cài plugin (auto-install flow), và là mode được recommend khi user cài thủ công. KHÔNG phải codepath duy nhất được phép chạy. Các mode khác = explicit opt-in qua env var / flag.

**Định nghĩa mode**:
- `http remote oauth`: MCP server được deploy remote (tại `https://<server>.n24q02m.com` trên OCI, hoặc self-host URL). Server act như OAuth 2.1 Resource Server + delegate authentication tới OAuth provider chính (vd Notion OAuth app). User cài plugin → auto redirect tới provider OAuth login → callback lưu token per-user → plugin connect qua Bearer. **Multi-user thật sự**. CHỈ áp dụng khi provider support OAuth 2.1 proper (Notion).
- `http remote relay`: MCP server deploy remote tại `https://<server>.n24q02m.com` (hoặc self-host) + credential submit qua browser tại URL relay remote, ECDH encrypt, server poll `poll_for_result` từ mcp-core. Dùng khi provider KHÔNG có OAuth 2.1 (Telegram phone/OTP, Email IMAP/OAuth device code, v.v.).
- `http local relay`: MCP server chạy LOCAL (127.0.0.1) qua `runLocalServer`/`run_local_server` từ mcp-core, serve credential form ở `/authorize`. User paste cred ở browser local. **Không gọi ra internet** cho flow setup. Dùng cho wet/mnemo/crg (cred đơn giản là API key).
- `http local non-relay`: giống `http local relay` nhưng KHÔNG có relaySchema (không cần credential). CHỈ godot (game tools không cần API key).
- `stdio proxy`: server expose stdio transport qua `mcp-stdio-proxy` (hoặc entry point `--stdio` / `MCP_TRANSPORT=stdio`). Backward compat cho agent không support HTTP. BẮT BUỘC mọi server support.

**Về "remote"**: remote = deployed trên OCI (`https://<server>.n24q02m.com`) HOẶC self-host trên hạ tầng user tự quản lý. Self-host dùng cùng code, chỉ khác `MCP_RELAY_URL` env var.

**How to apply**:
1. Mỗi entry point PHẢI có **ONE default mode** được kích hoạt rõ ràng theo matrix. KHÔNG được có dual-codepath parallel (vd: vừa serve `/authorize` local form + vừa lazy-trigger remote relay → user thấy 2 URL không biết dùng cái nào = **BUG**).
2. Switching giữa các mode qua `MCP_MODE` env var (giá trị: `remote-oauth` / `remote-relay` / `local-relay` / `local-non-relay` / `stdio-proxy`) HOẶC CLI flag. Default tự động nếu không set. KHÔNG activate mode khác khi default đã chạy.
3. Trước khi edit transport/init: check matrix, xác định default + modes hỗ trợ. KHÔNG tự thêm mode mới (vd "remote oauth" cho telegram — không có OAuth provider → không hỗ trợ). KHÔNG rename mode.
4. E2E test: default mode TRƯỚC (UX thực), modes khác sau nếu spec yêu cầu. Default KHÔNG test = test invalid.
5. Audit: verify (a) entry point chọn default đúng theo matrix, (b) mode khác route đến primitive mcp-core đúng, (c) mode ngoài matrix = divergence, (d) KHÔNG có dual-codepath parallel.
6. Fix bug 1 mode → verify modes khác cùng server không regress.
7. User report "mode X không work" → fix mode X hoặc giải thích rõ X không thuộc matrix. KHÔNG đề xuất "dùng Y thay".

**Why**: Session trước đã chốt kiến trúc này. Vi phạm 2026-04-18: (a) đề xuất "migrate relay-server+pages sang mcp-core rồi mới ship" thay vì verify matrix, (b) audit phát hiện cả 7 repo có dual-codepath parallel (runLocalServer local + remote relay lazy) → user thấy 2 URL simultaneously. Memory `feedback_mcp_mode_matrix.md`.</important>
<important if="implementing, editing, or auditing http local-relay + http remote-relay trong CÙNG MCP server (email/telegram/wet/mnemo/crg) — bất kể transport http.ts/http.py hay credential form renderer">
- **LOCAL-RELAY ≡ REMOTE-RELAY UI/FLOW PARITY**: Trong 1 server support cả local-relay + remote-relay, UI + luồng credential PHẢI **identical**. Khác biệt duy nhất cho phép: storage scope (local = single-user `config.enc`, remote = multi-user per-`JWT sub`) + OAuth 2.1 AS endpoints + Bearer middleware cho `/mcp`. Nếu local-relay có paste form multi-provider → remote-relay PHẢI có đúng form đó; nếu local-relay support N providers → remote-relay PHẢI support đúng N providers, KHÔNG được subset. Anti-pattern cấm: remote-relay dùng `delegatedOAuth` code path khác hẳn local-relay cho cùng provider set; remote-relay ép 1 provider (Outlook only) khi local-relay có paste form multi-provider; duplicate credential form renderer với drift. Code layout chuẩn: 1 shared `renderXxxCredentialForm` + 1 shared core validator + mode chỉ khác `onCredentialsSaved` callback (local: `writeConfig(server, creds)`; remote: `perUserStore.save(sub, creds)` + JWT issuance). Vi phạm 2026-04-19 session 80d829f6: `better-email-mcp/src/transports/http.ts` có 2 code path phân biệt — `remote-relay` → `delegatedOAuth device_code Outlook only`, `local-relay` → `relaySchema` paste form Gmail+Yahoo+iCloud+Outlook. User mở remote URL chỉ thấy Outlook device code, scold "sao lại chỉ có outlook, multi-acc đâu, thiết kế cũ đâu?". Xem memory `feedback_relay_mode_ui_parity.md`.
</important>
<important if="editing config.py, relay_schema.py, credential_state.py, sync.py của bất kỳ MCP server nào; hoặc thêm field mới vào relay form">
- **MCP CONFIG PARITY BẮT BUỘC**: MCP servers trong CÙNG CATEGORY (theo mode matrix) PHẢI có **thiết kế config giống hệt nhau** — defaults, relay_schema fields, credential flow, OAuth hardcoding. TUYỆT ĐỐI KHÔNG tự quyết "design choice khác nhau" khi server cùng category đã có pattern. Category: `http local relay` = wet/mnemo/crg; `http remote relay` = telegram/email; `http remote oauth` = notion; `http local non-relay` = godot. Trước khi edit 1 server → đọc file tương ứng của ÍT NHẤT 1 server cùng category, compare field-by-field. Thêm field mới → add ở TẤT CẢ servers cùng category (batch commit/PR). Fix bug → apply cùng sang servers cùng category. Chi tiết + case study: `~/.claude/skills/fullstack-dev/references/mcp-server.md` section "Category Config Parity" + memory `feedback_mcp_config_parity.md`. Vi phạm 2026-04-19 session 80d829f6: wet hardcode GDrive Desktop OAuth, mnemo empty → user scold "phải đảm bảo thiết kế cấu hình giống nhau chứ, có lúc nào tôi bảo làm khác hả".
</important>
<important if="developing, testing, releasing, auditing any MCP server — kể cả new repo, backport, audit">
- **MCP TOOL LAYOUT CHUẨN (2026-04-18+)**: Mỗi MCP server expose CHÍNH XÁC **N domain tools + `help` + `config`**. Tool `config` GỘP credential/relay setup actions (`open_relay|relay_status|relay_skip|relay_reset|relay_complete|warmup`) + runtime actions (`status|set|cache_clear|...`). **KHÔNG có tool `setup` RIÊNG** từ nay — phân biệt với chuẩn cũ 3-helper (config+setup+help). Chi tiết + template code Python/TS: `~/.claude/skills/fullstack-dev/references/mcp-server.md` section "Standard Tool Set".

**Why:** 7 reference repo hiện drift 3 patterns khác nhau (`config+setup+help` / `config+help` / `setup+help`). User chốt chuẩn hoá 18/04/2026. Session khác đang backport 5 repo drift → KHÔNG touch trong session khác để tránh conflict.

**How to apply:**
1. Server mới (imagine-mcp, future repos): bắt đầu từ N+2 pattern, đọc skill reference TRƯỚC khi code.
2. `help(topic?)` validate topic list = domain tool names + `config`, reject invalid.
3. `config(action, ...)` validate action list, reject invalid, list valid options trong error.
4. Cấm tạo tool `setup` mới trong MỌI repo. Setup actions PHẢI nằm trong `config`.
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
