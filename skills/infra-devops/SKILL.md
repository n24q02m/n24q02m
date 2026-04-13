---
name: infra-devops
description: "Infrastructure, DevOps, CI/CD, security. OCI VM, Docker, Caddy, monitoring (Grafana, Alloy, Loki, Vector), MLflow, Doppler, Infisical, GitHub Actions, pre-commit, mise, PSR, Renovate, security audit."
---

# Infrastructure & DevOps

## Khi nao dung

- Deploy service len OCI VM (Infrastructure hoac Production)
- Cau hinh Docker Compose, Caddy reverse proxy, Cloudflare Access
- Allocate resources (Dragonfly DB, Qdrant collection, FalkorDB)
- Monitoring: Grafana Selfhost, Alloy, Loki, Vector, Node Exporter
- MLflow tracing (AI/LLM) va experiment tracking
- Secrets management: Doppler (infra), Infisical (app)
- Docker security: multi-stage build, BuildKit cache, non-root user
- Dependency scanning: Semgrep, Renovate, Trivy
- CI/CD: GitHub Actions, PSR v10, pre-commit hooks
- Repository structure: mise, linting, CODEOWNERS
- Cloudflare Access, Firebase Auth security, rate limiting

## Infrastructure

```
EDGE: Cloudflare Pages (Static Next.js)
         | CF Tunnel
VM 2 (Prod): FastAPI + Echo, Docker Compose (3 OCPU, 16GB, 50GB)
         |   Repo: https://github.com/n24q02m/oci-vm-prod
VM 1 (Infra): PostgreSQL, Qdrant, FalkorDB, Dragonfly, Infisical, MLflow (3 OCPU, 16GB, 150GB)
              Repo: https://github.com/n24q02m/oci-vm-infra

MONITORING: Grafana + Loki selfhost (Alloy, Node Exporter, Vector) tren VM Infra
```

- **Ingress**: CF Tunnel + Caddy. **CF Access**: Chi bao ve selfhost services (KHONG bao ve API).
- **Secrets**: Doppler (Infra), Infisical (App). **Auth**: Firebase Auth.

## Storage (Polyglot Persistence)

| Loai | Service | Muc dich |
|------|---------|----------|
| Relational | PostgreSQL | User Data, Auth, Transactions, Logging |
| Vector | Qdrant | Embeddings, Semantic Search |
| Graph | FalkorDB | Knowledge Graph, GraphRAG |
| Cache | Dragonfly | Caching, Semantic Cache |
| Object | R2 (primary), GDrive (backup) | Files, Media |

## Dev Tools (Mise)

Terraform, uv, ruff, ty, pnpm, biome, golangci-lint, gofumpt, Infisical, Doppler, GitHub, Wrangler.

**Fixed Versions**: Python 3.13, Node 24, Java 21. Cac tool khac: latest.

## References (doc on demand)

- `references/oci-vm.md` -- VM architecture, deploy workflow, memory limits, resource allocation scripts, backup
- `references/observability.md` -- Grafana Selfhost, Alloy, Vector, Loki, MLflow tracing/tracking, alerting
- `references/security.md` -- Secrets management (Doppler/Infisical), Docker security, dependency scanning, auth, rate limiting
- `references/repo-structure.md` -- Repository standards, mise tasks, pre-commit, Git branching, README format, Renovate, Docker build
- `references/ci-cd.md` -- CI/CD workflow templates (Python/TS/Go/Rust), PR title check, Semgrep, Qodo Merge, email notify
- `references/semantic-release.md` -- PSR v10 config (Python/TS/Rust/Go), monorepo, beta/stable, troubleshooting

Doc reference file tuong ung TRUOC KHI bat dau lam viec tren topic do.

## Spec / Plan / Migration / Architecture writeup

**BAT BUOC**: Khi user yeu cau viet spec/plan/roadmap cho bat ky infra/devops task nao (VM deploy plan, CI/CD redesign, monitoring rollout, secrets migration, disaster recovery, PSR config, GCP/AWS migration plan, cost optimization plan), invoke `Skill` tool voi `superpowers:writing-plans` (hoac `superpowers:brainstorming` cho ideation, `superpowers:executing-plans` cho execution) TRUOC KHI viet noi dung. KHONG freehand. Skill enforce verify-before-claim, test-first, bite-sized tasks, review checkpoint. Xem global rule `~/.claude/CLAUDE.md` section 1 va memory `feedback_spec_plan_superpower.md`.

**FEEDBACK → SPEC + PLAN**: Khi user dua feedback thay doi scope/requirements/decisions, PHAI cap nhat spec + plan document TRUOC, KHONG chi ghi memory. Memory la ghi chu bo sung, spec + plan la source of truth. Thu tu: feedback → (1) update spec/plan → (2) ghi memory → (3) implement.

**Public-ready artifacts**: Khi viet docs/plans/terraform modules/dockerfiles voi kha nang release public (OS repo, blog post, conference talk), BAT BUOC:
- Khong hardcode hostname noi bo hay tailscale IPs — dung placeholder `<infra-host>`, `<prod-host>`
- Khong expose Infisical project ID, Doppler config names, CF account ID
- Khong leak secret paths hay API key format tu environment
- Terraform/Dockerfile: tach module public-safe voi module co secrets
- License: Apache-2.0 mac dinh cho code + docs
- README phai co quick-start KHONG can credentials noi bo
