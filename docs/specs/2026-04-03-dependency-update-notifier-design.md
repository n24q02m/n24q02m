# Centralized Dependency Update Notifier

## Problem

When a core library (qwen3-embed, web-core, mcp-relay-core, knowledge-core) releases a new stable version, downstream repos that depend on it have no automatic notification. Updates are discovered manually or when Renovate eventually creates a PR, but there is no actionable issue prompting immediate review.

## Solution

A centralized dispatcher hosted in the `n24q02m` repo. Core repos dispatch an event on stable release; a workflow in `n24q02m` reads a dependency map and creates issues in each downstream repo.

## Dependency Map

File: `dependency-map.yml` at repo root.

```yaml
cores:
  qwen3-embed:
    package: qwen3-embed          # PyPI package name
    downstream:
      - repo: wet-mcp
        field: pyproject.toml
      - repo: mnemo-mcp
        field: pyproject.toml
      - repo: better-code-review-graph
        field: pyproject.toml

  web-core:
    package: n24q02m-web-core
    downstream:
      - repo: wet-mcp
        field: pyproject.toml
      - repo: knowledge-core
        field: pyproject.toml

  mcp-relay-core:
    package: mcp-relay-core        # PyPI + npm as @n24q02m/mcp-relay-core
    downstream:
      - repo: wet-mcp
        field: pyproject.toml
      - repo: mnemo-mcp
        field: pyproject.toml
      - repo: better-telegram-mcp
        field: pyproject.toml
      - repo: better-code-review-graph
        field: pyproject.toml
      - repo: better-email-mcp
        field: package.json
      - repo: better-notion-mcp
        field: package.json

  knowledge-core:
    package: knowledge-core
    downstream:
      - repo: KnowledgePrism
        field: apps/ai-worker/pyproject.toml
      - repo: Aiora
        field: apps/ai-worker/pyproject.toml
```

## Workflow: `notify-downstream.yml`

Location: `n24q02m/.github/workflows/notify-downstream.yml`

### Trigger

```yaml
on:
  repository_dispatch:
    types: [core-update]
```

### Payload Schema

```json
{
  "core": "qwen3-embed",
  "version": "1.6.0",
  "tag": "v1.6.0",
  "release_url": "https://github.com/n24q02m/qwen3-embed/releases/tag/v1.6.0"
}
```

### Logic

1. Parse `client_payload` for `core`, `version`, `tag`, `release_url`.
2. Read `dependency-map.yml`, extract `downstream` list for the given `core`.
3. For each downstream entry:
   a. **Dedup check**: search open issues in that repo with title `Update {package} to {version}`. If found, skip.
   b. **Create issue** with template (see below).
4. Output summary of created/skipped issues.

### Authentication

GitHub App `n24q02m-ci` (ID: 3200052) via `actions/create-github-app-token` with `owner: n24q02m` to generate a token scoped to all repos the app is installed on (required for cross-repo issue creation).

## Issue Template

Title: `Update {package} to {version}`

```markdown
## Core Library Update

**{package}** has released **{version}**.

- Release: {release_url}

## Action Required

- [ ] Review release notes for breaking changes
- [ ] Update version constraint in `{field}`
- [ ] Run tests locally
- [ ] Create PR with the update

Labels: dependencies, core-update
```

## Core Repo CD Changes

Each of the 4 core repos adds one step at the end of CD, after all publish jobs succeed. Only for stable releases (not beta).

### Step Template (Python cores: qwen3-embed, web-core, knowledge-core)

Added as a new job `notify-downstream` in `cd.yml`:

```yaml
  notify-downstream:
    name: Notify Downstream
    needs: [release, publish-pypi]  # adjust per repo
    if: needs.release.outputs.released == 'true' && needs.release.outputs.is_prerelease != 'true'
    runs-on: ubuntu-latest
    steps:
      - name: Harden Runner
        uses: step-security/harden-runner@fa2e9d605c4eeb9fcad4c99c224cee0c6c7f3594 # v2
        with:
          egress-policy: audit

      - name: Generate GitHub App Token
        id: app-token
        uses: actions/create-github-app-token@f8d387b68d61c58ab83c6c016672934102569859 # v3
        with:
          app-id: ${{ vars.CI_APP_ID }}
          private-key: ${{ secrets.CI_APP_KEY }}

      - name: Dispatch core-update
        env:
          GH_TOKEN: ${{ steps.app-token.outputs.token }}
        run: |
          gh api repos/n24q02m/n24q02m/dispatches \
            -f event_type=core-update \
            -f 'client_payload[core]=CORE_NAME' \
            -f 'client_payload[version]=${{ needs.release.outputs.version }}' \
            -f 'client_payload[tag]=${{ needs.release.outputs.tag }}' \
            -f 'client_payload[release_url]=https://github.com/${{ github.repository }}/releases/tag/${{ needs.release.outputs.tag }}'
```

Where `CORE_NAME` is replaced per repo: `qwen3-embed`, `web-core`, `knowledge-core`.

### Step Template (mcp-relay-core — Bun monorepo)

Same pattern, but `needs` depends on its specific publish jobs and `CORE_NAME=mcp-relay-core`.

## Repos Changed

| Repo | Change |
|------|--------|
| `n24q02m` | Add `dependency-map.yml` + `.github/workflows/notify-downstream.yml` |
| `qwen3-embed` | Add `notify-downstream` job to `cd.yml` |
| `web-core` | Add `notify-downstream` job to `cd.yml` |
| `mcp-relay-core` | Add `notify-downstream` job to `cd.yml` |
| `knowledge-core` | Add `notify-downstream` job to `cd.yml` |
| Downstream repos (12) | No changes |

## Dedup Strategy

Before creating an issue, the workflow searches:

```bash
gh issue list --repo n24q02m/{repo} \
  --search "Update {package} to {version} in:title" \
  --state open --json number --jq 'length'
```

If count > 0, skip. This prevents duplicate issues if the workflow runs multiple times.

## Edge Cases

- **Beta releases**: Excluded via `is_prerelease != 'true'` condition. No issues for beta.
- **Transitive updates**: When `web-core` releases → issues in `wet-mcp` and `knowledge-core`. When `knowledge-core` later releases → issues in `KnowledgePrism` and `Aiora`. The chain is handled naturally by each core dispatching independently.
- **New downstream repo added**: Edit `dependency-map.yml` only. No changes to core repos.
- **Core repo removed**: Remove entry from `dependency-map.yml`.
- **Workflow failure**: GitHub Actions retry. Dedup prevents duplicates on retry.
