# CLI Auth State + Test Accounts Persist

Auth state của CLI tools DUY TRÌ ACROSS SESSIONS — KHÔNG hỏi user "đã login chưa".

## Service-specific check commands

| Service | Command |
|---------|---------|
| Firebase | `firebase login:list` |
| gh | `gh auth status` |
| gcloud | `gcloud auth list` |
| wrangler | `wrangler whoami` |
| aws | `aws sts get-caller-identity` |
| skret | reads `~/.aws/credentials` (boto3 chain) |
| npm | `npm whoami` |
| vercel | `vercel whoami` |
| dodo | `dodo auth status` |

## 4-step workflow

1. **Check CLI auth state** via command (above)
2. **Check memory** cho test account creds (e.g. `e2e-test-credentials.md`)
3. **Nếu thiếu** → tự register/create + LƯU NGAY vào memory cho session sau
4. **Chỉ ask user** khi service mới chưa có account (như Yoti SDK signup)

## Violation

2026-04-18: hỏi "Firebase user nào?" trong khi CLI đã login + e2e user đã tồn tại nhiều lần.

Memory: `feedback_cli_state_test_accounts_persist.md`.
