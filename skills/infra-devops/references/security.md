---
name: security-practices
description: "Bảo mật ứng dụng và infrastructure. Sử dụng khi quản lý secrets (skret + AWS SSM), bảo mật Docker, dependency scanning, Cloudflare Access, Firebase Auth security."
---

# Security Practices Guide

## Khi Nào Dùng

- Quản lý secrets với skret CLI → AWS SSM Parameter Store (infra + app + runtime)
- Bảo mật Docker containers và images
- Setup dependency scanning (Semgrep, Renovate)
- Cấu hình Cloudflare Access cho services
- Audit security cho ứng dụng và infrastructure

> **Test Coverage**: ≥ 95% cho tất cả security validations và auth logic.

### Bảng Bác Bỏ Lý Do Bỏ Qua Security

| Lý do | Thực tế |
|-------|---------|
| "Chỉ là internal service" | Internal services bị compromise → lateral movement toàn hệ thống. |
| "Biến môi trường an toàn mà" | `.env` commit lên git = leak vĩnh viễn (git history). |
| "Hardcode tạm, sửa sau" | "Tạm" biến thành permanent. Secret trong code = 1 git push là lộ. |
| "Service nhỏ, không ai hack đâu" | Automated scanners quét mọi IP. Nhỏ hay lớn đều bị scan. |
| "Docker image tin tưởng được" | Base image có thể chứa CVE. Luôn scan, luôn pin version. |
| "--no-verify nhanh hơn" | Pre-commit hooks tồn tại vì lý do. Bypass = đưa secret/vuln vào prod. |

## Secrets Management

### Hierarchy (post-2026-04-24 skret migration)

| Layer | Tool | Scope | Khi nào dùng |
|-------|------|-------|-------------|
| All secrets | `skret` CLI → AWS SSM Parameter Store (ap-southeast-1) | Infra + app + runtime | Source of truth cho mọi secret (VM, app, CI) |
| CI/CD | GitHub Actions secrets (synced from SSM via `skret sync --to-github`) | Workflow secrets | SSM `/<app>/prod/*` → GH Actions secrets |
| Runtime | Platform secrets (GCloud Secret Manager, Modal) | Container runtime | Bổ sung, không thay thế skret |
| Local Dev | `.secrets.dev.yaml` (skret local provider) | Developer machine | **KHÔNG commit vào git** |

> **BẮT BUỘC (2026-04-24+)**: Mọi project dùng skret làm source of truth. Doppler + Infisical đang trong soak window + decommission — KHÔNG dùng cho repo mới. SSM prod auto-sync sang GitHub Actions qua `skret sync`. Xem `skret-project.md` + `feedback_env_taxonomy.md` trong memory để hiểu migration status + secret-env vs runtime-env taxonomy.

### Env naming policy

**Distinguish secret-env from runtime-env — they're orthogonal.**

- **Secret-env (namespace in skret / Infisical / Doppler / SSM)** = **`dev` + `prod` ONLY**
  - `dev` — local laptop developer use only (`skret run -e dev -- <cmd>`)
  - `prod` — consumed by BOTH prod AND staging cloud runtimes
  - Never create a 3rd `staging` secret namespace. Import tooling that creates one by default (Infisical → skret migration observed 2026-04-24) must be configured to skip staging or the imported namespace pruned.
- **Runtime-env (GHCR tag, CD target, compose profile, URL auto-detect)** = `dev` + `staging` + `prod` (all real deploys, independent of secret-env)
  - Staging deploy reads from the `prod` secret-env with keys that differ under a `<PREFIX>_STAGING_<NAME>` suffix. Example from KP: `/KnowledgePrism/prod/KLPRISM_DB_PASSWORD` (prod default) vs `/KnowledgePrism/prod/KLPRISM_STAGING_DB_PASSWORD` (staging override). Docker-compose / CD workflow picks the right one at deploy time by runtime-env.
  - Test Mode / Live Mode credentials (Dodo, Stripe, Firebase test project) follow the same pattern: live keys under normal names in `prod`, test-mode keys under `_STAGING` suffix in `prod`.
- skret (tool) chấp nhận BẤT KỲ env string nào qua `--env=<name>` và `.skret.yaml` → tự do design-level. User policy (n24q02m repos): chỉ `prod` + `dev` secret-env. Rule áp dụng khi tạo namespace mới trong SSM hoặc thêm env trong `.skret.yaml`. Nếu thấy `--env=staging` hoặc `put-parameter --name /<project>/staging/*` trong any n24q02m repo → flag + correct.
- Xem memory `feedback_env_taxonomy.md` cho rationale đầy đủ.

### Rules BẮT BUỘC

```
# .gitignore — LUÔN CÓ các patterns này
.env
.env.*
!.env.example
*.pem
*.key
**/secrets/
```

- **KHÔNG BAO GIỜ** hardcode secrets trong code
- **KHÔNG BAO GIỜ** log secrets (kể cả masked)
- **KHÔNG BAO GIỜ** commit `.env` files
- Dùng `os.environ` / `process.env` — truyền qua environment variables
- Rotate secrets định kỳ (90 ngày cho production)

### skret (CLI runtime injection)

```bash
# Setup (một lần per laptop / VM)
aws configure  # region: ap-southeast-1
skret list -e prod --path=/<namespace>/prod  # smoke test

# Inject vào Docker Compose
skret run -e prod -- docker compose up -d

# Inject vào script
skret run -e prod -- ./scripts/backup.sh

# Multi-namespace pattern (nhiều app trên cùng host)
COMBINED=$(mktemp); for app in app1 app2; do skret env -e prod --path=/$app/prod --format=dotenv >> $COMBINED; done; set -a; . $COMBINED; set +a; docker compose up -d
```

### skret (SDK fetch trong code — chỉ khi `skret run` không khả dụng)

```python
# Python — boto3 SSM SDK trực tiếp
import boto3
ssm = boto3.client("ssm", region_name="ap-southeast-1")
resp = ssm.get_parameters_by_path(
    Path="/<app>/prod/",
    Recursive=True,
    WithDecryption=True,
)
secrets = {p["Name"].rsplit("/", 1)[1]: p["Value"] for p in resp["Parameters"]}
```

```go
// Go — AWS SDK v2
import (
    "github.com/aws/aws-sdk-go-v2/config"
    "github.com/aws/aws-sdk-go-v2/service/ssm"
    "github.com/aws/aws-sdk-go-v2/service/ssm/types"
)

cfg, _ := config.LoadDefaultConfig(ctx, config.WithRegion("ap-southeast-1"))
client := ssm.NewFromConfig(cfg)
resp, _ := client.GetParametersByPath(ctx, &ssm.GetParametersByPathInput{
    Path:           aws.String("/<app>/prod/"),
    Recursive:      aws.Bool(true),
    WithDecryption: aws.Bool(true),
})
```

> **Ưu tiên `skret run --` luôn**, chỉ fall back sang SDK nếu container/runtime không cho phép spawn external process trước app start.

### CLI usage rules — `skret` exclusive, never raw `aws ssm`

**Rule** (added 2026-04-28): Mọi op secret (read/write/list) BẮT BUỘC đi qua `skret`:

| Use case | Đúng | SAI |
|---|---|---|
| Read 1 key | `skret env -e prod --path=/<ns>/prod \| grep ^KEY=` | `aws ssm get-parameter --name /<ns>/prod/KEY` |
| Write 1 key | `skret put -e prod --path=/<ns>/prod/KEY --value=...` | `aws ssm put-parameter --name /<ns>/prod/KEY ...` |
| List keys | `skret env -e prod --path=/<ns>/prod \| awk -F= '{print $1}'` | `aws ssm describe-parameters --parameter-filters Key=Name,Option=BeginsWith,Values=/<ns>/prod` |
| Inject vào cmd | `skret run -e prod -- <cmd>` | `eval $(aws ssm get-parameters-by-path ... \| jq ...)` |

**Why**:
- skret = abstraction; backend có thể migrate (Doppler → Infisical → SSM → Vault) mà không phải sửa scripts.
- skret enforce path policy + uniform `dotenv` formatting + audit log dưới tên `skret-vm-runtime` IAM user. Direct `aws ssm` xài raw API key + bypass policy.
- `aws ssm describe-parameters` có thể list keys ngoài scope sandbox đã grant.

**Git Bash trên Windows**: path `--path=/foo/bar` bị mangle thành `C:/Program Files/Git/foo/bar`. Dùng `MSYS_NO_PATHCONV=1 skret env -e prod --path=/foo/bar ...` hoặc chạy từ PowerShell. KHÔNG fallback `aws ssm` để tránh path quirk.

**Empty namespace = empty backend**: `skret env --path=/global/prod --format=dotenv` trả 0 dòng → namespace thật sự trống. KHÔNG cross-check qua `aws ssm describe-parameters` (skret đọc cùng SSM, kết quả giống nhau).

### App namespace boundary — runtime-only

**Rule** (added 2026-04-28): `/<app>/prod` chứa chỉ secret app code đọc lúc runtime.

| Loại credential | Có ở `/<app>/prod`? | Nơi đúng |
|---|---|---|
| DB DSN, OAuth client secret app exchange, API key app gọi upstream, R2 keys app upload | ✅ | `/<app>/prod` |
| DNS zone:edit (CF/Route53/etc) | ❌ | User dashboard (one-off) hoặc admin namespace `/admin-cf-zones/prod/CLOUDFLARE_ZONE_EDIT_<ZONE>` (recurring) |
| CF account-wide token | ❌ | Admin only — never store account-wide token; mint scoped tokens per-zone/per-project |
| GitHub org-admin PAT | ❌ | Admin namespace, IAM gated |
| Cloud root keys (AWS root, GCP super-admin) | ❌ | Never stored, MFA-protected only |
| Domain registrar API, billing API | ❌ | Admin namespace |

**Why**: app namespace IAM grants ANY runtime container the right to read those keys. Runtime exploit (SSRF, RCE, stolen env dump) → DNS hijack / org-admin escalation if zone:edit / org PAT live there. Strict least-privilege boundary protects blast radius.

**Hunt protocol**: trước khi grep skret cho 1 credential, tự hỏi: **"App runtime code có CALL credential này không?"**. Nếu KHÔNG → không hunt app namespace, chọn 1 trong:
1. User edit dashboard 30 giây (one-off DNS edit, custom domain attach to branch alias).
2. User mint scoped token paste 1 lần cho command.
3. Tạo dedicated admin namespace `/admin-<scope>/prod/<KEY>` nếu thao tác recurring (CD pipeline edits DNS) — IAM grant scoped đến đó.

### Public vs Private OAuth Client Secrets — Google "Desktop/Installed app" pattern

**Nguyên tắc**: không phải mọi chuỗi trông-như-secret trong source code đều là secret cần rotate.

**Google OAuth 2.0 Client Types**:
| Application type | Client secret | Rotation cần thiết khi leak? |
|---|---|---|
| **Web application** | PRIVATE — server-side only | YES — rotate ngay |
| **Desktop app / Installed app** | PUBLIC — Google coi là public | NO — rotation vô nghĩa |
| **iOS/Android** | Không có client secret | N/A |
| **Service account key** | PRIVATE | YES — rotate ngay |

Quote official Google docs ([OAuth 2.0 for Installed Applications](https://developers.google.com/identity/protocols/oauth2#installed)):
> *"Installed applications are considered public clients and they cannot protect client secrets. Therefore, the secret is not treated as a secret..."*

**Pattern nhận biết Desktop/Installed client**:
- App distributed to end-users (CLI, uvx-installable, desktop binary)
- Client secret hardcoded default trong source / config
- Flow dùng `urn:ietf:wg:oauth:2.0:oob` hoặc `localhost:PORT` redirect
- `GOCSPX-...` prefix (dùng cho cả Web và Desktop — phân biệt qua app type ở GCP Console)

**Hệ quả cho security audit**:
1. Secret scanner alert (GitGuardian/Gitleaks/TruffleHog) match `GOCSPX-...` trong source Desktop app → FALSE POSITIVE. Dismiss với lý do "Google Desktop OAuth public client — acknowledged per Google policy".
2. KHÔNG propose rotation — user cài binary sẽ luôn có secret, rotate không giải quyết gì.
3. Pentesters/auditors phải hỏi GCP Console app type trước khi kêu "leak".
4. Code review thấy hardcoded `GOCSPX-...` + flow là Installed → OK, không block.

**Ví dụ thực tế trong monorepo**:
- `wet-mcp` (uvx-installable, GDrive sync cho local storage): hardcoded `google_drive_client_secret = "GOCSPX-..."` trong `config.py` = PUBLIC pattern, OK.
- `mnemo-mcp` (same distribution): default empty, user set env = conservative, OK.
- `better-notion-mcp` (server-side deployed OAuth relay): `NOTION_OAUTH_CLIENT_SECRET` qua skret SSM = PRIVATE, leak = rotate.

**Phân biệt wet vs mnemo**: cả 2 repo đều có GDrive sync code, NHƯNG chỉ wet-mcp hardcoded secret default (ship as zero-config UX). mnemo-mcp chọn pattern an toàn hơn: default empty + user cung cấp. Khác nhau là design choice, KHÔNG phải bug.

**Flag thật sự cần rotate**:
- Web app client secret (flow redirect về `https://example.com/callback`) leak → rotate
- Service account `.json` key leak → rotate + audit usage
- OAuth access/refresh tokens của user (không phải client secret) leak → revoke session

Ghi memory mỗi khi xác định false positive để giảm audit noise: `feedback_google_oauth_desktop_public.md`.

---

## Docker Security

### Image Best Practices

```dockerfile
# syntax=docker/dockerfile:1

# 1. BuildKit syntax directive — BẮT BUỘC dòng đầu tiên
# Đảm bảo BuildKit features hoạt động nhất quán (mount cache, bind mounts)

# 2. Dùng specific version tags (KHÔNG dùng :latest)
FROM python:3.13-slim-bookworm AS base

# 3. Non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser -m appuser

# 4. Multi-stage build (giảm attack surface)
FROM base AS builder
COPY . .
RUN uv sync --frozen --no-dev

FROM base AS runtime
COPY --from=builder /app/.venv /app/.venv
USER appuser

# 5. Read-only filesystem khi có thể
# docker run --read-only --tmpfs /tmp myapp

# 6. Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1
```

### .dockerignore (BẮT BUỘC)

Mỗi Dockerfile **PHẢI** có `.dockerignore` tương ứng để giảm build context size và tránh leak thông tin nhạy cảm:

```dockerignore
# Git
.git
.github

# IDE
.vscode
.idea

# Cache
.ruff_cache
.pytest_cache
__pycache__

# Development
tests/
temp/
docs/
*.md
!README.md

# Docker
Dockerfile
docker-compose.yml
.dockerignore

# Config (không cần trong runtime)
.pre-commit-config.yaml
.editorconfig
.mise.toml

# Environment
.env
.env.*
```

### BuildKit Cache Patterns

> **Nguyên tắc**: Tách dependency install và project install để tối ưu Docker layer cache.
> Dùng `--mount=type=cache` cho package manager cache và `--mount=type=bind` cho lock files.

#### Python (uv)

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Bước 1: Cài dependencies (cached khi deps không đổi)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Bước 2: Copy code và cài project
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
```

#### Node.js (bun)

```dockerfile
FROM oven/bun:alpine AS builder
WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . .
RUN bun run build
```

#### Go

```dockerfile
FROM golang:1-alpine AS builder
WORKDIR /build

COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

COPY . .
ARG TARGETARCH
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux GOARCH=$TARGETARCH go build -o /out/app ./cmd/server
```

### Docker Compose Security

```yaml
services:
  api:
    image: myapp:v1.2.3
    restart: unless-stopped
    read_only: true
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true
    mem_limit: 512m
    cpus: 0.5
    networks:
      - oci-network
    # KHÔNG expose ports trực tiếp — dùng Caddy reverse proxy
```

### Container Scanning

```yaml
# CI: Scan Docker images
- name: Build image
  run: docker build -t myapp:${{ github.sha }} .

- name: Scan with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: myapp:${{ github.sha }}
    format: table
    exit-code: 1
    severity: CRITICAL,HIGH
```

---

## Dependency Security

### Automated Scanning

```yaml
# .github/workflows/ci.yml — dependency-review job
dependency-review:
  name: Dependency Review
  if: github.event_name == 'pull_request'
  runs-on: ubuntu-latest
  continue-on-error: true  # cho private repos
  steps:
    - uses: actions/checkout@v6
    - uses: actions/dependency-review-action@v4
      with:
        fail-on-severity: moderate
        comment-summary-in-pr: always
```

### Language-Specific Audits

```bash
# Python
uv pip audit

# Node.js
bun pm audit

# Go
govulncheck ./...

# Rust
cargo audit
```

### Dependabot (GitHub native)

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      minor-and-patch:
        update-types: ["minor", "patch"]

  - package-ecosystem: "npm"
    directory: "/apps/web"
    schedule:
      interval: "weekly"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## Authentication & Authorization

### Firebase Auth Security Rules

```javascript
// Firestore Security Rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Authenticated users only
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null && request.auth.uid == userId;
    }

    // Admin-only
    match /admin/{document=**} {
      allow read, write: if request.auth != null
        && request.auth.token.admin == true;
    }

    // Default deny
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

### Backend Token Validation

```python
# FastAPI middleware pattern
from firebase_admin import auth

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    try:
        decoded = auth.verify_id_token(credentials.credentials)
        # Kiểm tra token expiration
        if decoded.get("exp", 0) < time.time():
            raise HTTPException(status_code=401, detail="Token expired")
        return decoded
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token expired")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")
```

---

## Cloudflare Access

### Bảo vệ Selfhost Services

Dùng CF Access để bảo vệ **selfhost admin UIs** (DBGate, Qdrant UI, Falkor browser, MLflow). **KHÔNG** bảo vệ API endpoints (API dùng Firebase Auth). MLflow built-in auth + CF Access OTP cho external.

| Service | Auth Method | Policy |
|---------|-------------|--------|
| Selfhost admin UIs | OTP (email) | Allowed emails |
| API (app) | Service Token | Machine-to-machine |

> **MLflow**: Built-in authentication (username/password). Apps trên VM access qua internal IP (`http://mlflow:5000`), không cần CF Access headers. External access (local dev) qua `https://mlflow.n24q02m.com` với basic auth (`MLFLOW_TRACKING_USERNAME` / `MLFLOW_TRACKING_PASSWORD`).

### Service Token (Machine-to-Machine)

```python
import os
import httpx

# Headers cho CF Access
headers = {
    "CF-Access-Client-Id": os.environ["CF_ACCESS_CLIENT_ID"],
    "CF-Access-Client-Secret": os.environ["CF_ACCESS_CLIENT_SECRET"],
}

# Request qua CF Access
response = httpx.get("https://mlflow.n24q02m.com/api/...", headers=headers)
```

---

## Network Security

### Docker Network Isolation

```yaml
# docker-compose.yml
networks:
  oci-network:
    driver: bridge
    ipam:
      config:
        - subnet: 10.0.0.0/24

# Services chỉ giao tiếp trong internal network
# Caddy là duy nhất expose port ra ngoài
```

### Caddy (TLS + Reverse Proxy)

```caddyfile
# Auto HTTPS via CF Tunnel — TLS terminated at Cloudflare
{$SERVICE_DOMAIN} {
    reverse_proxy oci-{service}:{port}

    # Security headers
    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        Referrer-Policy strict-origin-when-cross-origin
        -Server
    }
}
```

### Rate Limiting (API)

```python
# FastAPI với slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login(request: Request):
    ...
```

```go
// Echo với rate limiter middleware
import "github.com/labstack/echo/v4/middleware"

e.Use(middleware.RateLimiter(middleware.NewRateLimiterMemoryStore(20)))
```

---

## Security Audit Checklist

### Secrets
- [ ] Không có hardcoded secrets trong code?
- [ ] `.env` files trong `.gitignore`?
- [ ] Secrets được quản lý bởi Doppler/Infisical?
- [ ] CI/CD secrets trong GitHub Secrets?
- [ ] Secret rotation policy (90 ngày)?

### Docker
- [ ] BuildKit syntax directive (`# syntax=docker/dockerfile:1`) ở dòng đầu?
- [ ] `.dockerignore` có mặt và đầy đủ?
- [ ] Dùng specific image tags (không `:latest`)?
- [ ] Non-root user trong Dockerfile?
- [ ] Multi-stage builds?
- [ ] BuildKit `--mount=type=cache` cho package managers?
- [ ] Tách dependency install và project install (cache optimization)?
- [ ] `mem_limit` và `cpus` set cho mọi service?
- [ ] `no-new-privileges:true`?
- [ ] Container scanning trong CI?

### Dependencies
- [ ] `dependency-review-action` trong CI?
- [ ] Language-specific audit commands chạy định kỳ?
- [ ] Dependabot configured?

### Authentication
- [ ] Firebase Auth security rules configured?
- [ ] Token validation ở backend (verify + expiration check)?
- [ ] Rate limiting ở auth endpoints?

### Network
- [ ] Services chỉ giao tiếp qua internal Docker network?
- [ ] Chỉ Caddy expose port ra ngoài?
- [ ] CF Access bảo vệ selfhost UIs?
- [ ] Security headers set trong Caddy?
