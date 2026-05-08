# Auto-Launch Dependencies

When detect missing-dep error, BẮT BUỘC tự execute recovery command + retry. KHÔNG dừng để user chạy thủ công.

## Recovery map

| Error signal | Recovery command (Windows / Mac) | Verify |
|--------------|----------------------------------|--------|
| Docker daemon offline (`docker compose ... non-zero exit`, `daemon socket`, 500 errors) | Win: `"/c/Program Files/Docker/Docker/Docker Desktop.exe" &` / Mac: `open -a Docker` | `docker ps` OK |
| AWS SSO expired (`LoginRefreshRequired`, `Please reauthenticate using 'aws login'`) | `aws login` (browser auto-opens, user 1-click) | `aws sts get-caller-identity` |
| gh auth expired | `gh auth login --web` (browser 1-click) | `gh auth status` |
| npm login expired | `npm whoami` check → `npm login` (CHỈ exception nếu cần OTP) | `npm whoami` |

## Why

User L3009 session 2d88d796: *"tự mở docker, tự chạy cli login để tự bump trên màn hình nhắc tôi mà đỡ phải yêu cầu tôi chạy xong lại chờ mất thời gian"*. Mỗi lần dừng-nhắc-chờ = idle 5-15 phút. 1 session E2E + release dễ cần 3-5 lần re-auth → 30+ phút wasted nếu manual.

## Anti-patterns CẤM

- "Docker chưa chạy, anh launch giúp"
- "AWS SSO expired, anh `aws login` giúp"
- "Em không cancel mid-run được"

## Distinction

Browser-flow tools (aws/gh login --web) VẪN count là auto-launch — em launch CLI, browser tự mở, user effort = 1 click. Khác với `feedback_dont_defer_to_user.md` (defer = không làm gì, chờ user); auto-launch = chủ động launch dùm rồi continue.

Memory: `feedback_auto_launch_dependencies.md` + `feedback_auto_launch_violation_2026-05-01.md`.
