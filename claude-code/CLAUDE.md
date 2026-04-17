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
<important if="dispatching subagent, Agent tool, Task tool sub-invocation, or executing plan via superpowers:subagent-driven-development">
- **VERIFY SUBAGENT OUTPUT**: Subagent summary là INTENT không phải RESULT. BẮT BUỘC verify thực tế trước khi mark task completed hoặc báo user: (1) Read lại file cho code edits (git diff so pre-dispatch), (2) Chạy lại test command trong session chính (không trust "tests pass" từ subagent), (3) `git log -1 --stat` confirm commit SHA + prefix `fix:`/`feat:` + file list, (4) `curl` endpoint + check logs cho deploy, (5) Spot-check citations cho research agent. Nếu verify fail → dispatch lại với corrective prompt, KHÔNG skip. Xem memory `feedback_verify_subagent_output.md`.
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
- **API**: REST + OpenAPI (Orval). **Test Coverage**: ≥ 95%.
- **Type-Safe SQL**: Python (SQLModel + Alembic), Go (sqlc + golang-migrate), TS (Drizzle).
- **DataFrames**: `polars` only. **Data Files**: JSONL format bắt buộc.
- **Security**: **KHÔNG BAO GIỜ** commit real credentials (phone, API keys, tokens, passwords). Luôn dùng placeholders. Dùng Doppler/Infisical.
- **Infisical CLI**: **KHÔNG BAO GIỜ** dùng `infisical login` interactive. Auth qua universal-auth API → `--token` flag. Phải get token VÀ dùng token trong CÙNG MỘT bash call (env vars mất giữa các calls).
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

- **Quy tắc bỏ qua AI Traces (.jules & superpower)**:
  - **Repo PUBLIC** (trong list https://github.com/stars/n24q02m/lists/productions): BẮT BUỘC liệt kê `.jules`, `.Jules`, `.superpower`, `superpowers`, `docs/superpowers` vào `.gitignore`. TUYỆT ĐỐI KHÔNG TẠO/TRACK CÁC THƯ MỤC NÀY TRONG REPO PUBLIC.
  - **Repo PRIVATE**: `.jules` vẫn phải liệt kê vào `.gitignore`. TUY NHIÊN, `superpower` (ví dụ `docs/superpowers`) ĐƯỢC PHÉP tồn tại và theo dõi trên repo.
  - Kế hoạch lưu trữ **Superpower** dài hạn nếu thực sự cần cho repo public: tạo/viết và commit vào trong các repo private như `oci-vm-infra`, `oci-vm-prod`, `virtual-company` HOẶC commit vào một repo riêng `n24q02m/.superpower`.
