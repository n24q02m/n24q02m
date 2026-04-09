# Dependency Update Notifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automatically create GitHub issues in downstream repos when a core library releases a new stable version.

**Architecture:** Centralized dispatcher in `n24q02m` repo. Core repos dispatch `core-update` event on stable release; `notify-downstream.yml` workflow reads `dependency-map.yml` and creates issues in each downstream repo via GitHub App token.

**Tech Stack:** GitHub Actions, `actions/create-github-app-token@v3`, `gh` CLI, YAML dependency map

**Spec:** `docs/specs/2026-04-03-dependency-update-notifier-design.md`

---

## File Structure

### `n24q02m` repo (centralized)
- **Create:** `dependency-map.yml` — core-to-downstream mapping
- **Create:** `.github/workflows/notify-downstream.yml` — dispatcher workflow

### Core repos (4 repos, same pattern)
- **Modify:** `qwen3-embed/.github/workflows/cd.yml` — add `notify-downstream` job
- **Modify:** `web-core/.github/workflows/cd.yml` — add `notify-downstream` job
- **Modify:** `mcp-relay-core/.github/workflows/cd.yml` — add `notify-downstream` job
- **Modify:** `knowledge-core/.github/workflows/cd.yml` — add `notify-downstream` job

---

### Task 1: Create dependency map in `n24q02m` repo

**Files:**
- Create: `dependency-map.yml`

- [ ] **Step 1: Create `dependency-map.yml`**

```yaml
# Core library → downstream repos that need update issues on stable release.
# Edit this file to add/remove downstream repos. Core repos need no changes.
cores:
  qwen3-embed:
    package: qwen3-embed
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
    package: mcp-relay-core
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

- [ ] **Step 2: Commit**

```bash
git add dependency-map.yml
git commit -m "feat: add dependency map for core-to-downstream tracking"
```

---

### Task 2: Create `notify-downstream.yml` workflow in `n24q02m` repo

**Files:**
- Create: `.github/workflows/notify-downstream.yml`

- [ ] **Step 1: Create workflow file**

```yaml
name: Notify Downstream

on:
  repository_dispatch:
    types: [core-update]

permissions:
  contents: read

jobs:
  notify:
    name: Create Update Issues
    runs-on: ubuntu-latest
    steps:
      - name: Harden Runner
        uses: step-security/harden-runner@fa2e9d605c4eeb9fcad4c99c224cee0c6c7f3594 # v2
        with:
          egress-policy: audit

      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6

      - name: Generate GitHub App Token
        id: app-token
        uses: actions/create-github-app-token@f8d387b68d61c58ab83c6c016672934102569859 # v3
        with:
          app-id: ${{ vars.CI_APP_ID }}
          private-key: ${{ secrets.CI_APP_KEY }}
          owner: n24q02m

      - name: Create issues in downstream repos
        env:
          GH_TOKEN: ${{ steps.app-token.outputs.token }}
          CORE: ${{ github.event.client_payload.core }}
          VERSION: ${{ github.event.client_payload.version }}
          TAG: ${{ github.event.client_payload.tag }}
          RELEASE_URL: ${{ github.event.client_payload.release_url }}
        run: |
          set -euo pipefail

          # Parse dependency map (python — available on ubuntu-latest, no yq needed)
          read -r PACKAGE DOWNSTREAM <<< "$(python3 -c "
          import yaml, json, sys
          with open('dependency-map.yml') as f:
              data = yaml.safe_load(f)
          core = data['cores'].get('${CORE}')
          if not core:
              print('null null')
              sys.exit(0)
          print(core['package'], json.dumps(core['downstream']))
          ")"

          if [ "$PACKAGE" = "null" ] || [ "$DOWNSTREAM" = "null" ]; then
            echo "No downstream repos found for core: ${CORE}"
            exit 0
          fi

          TITLE="Update ${PACKAGE} to ${VERSION}"

          echo "$DOWNSTREAM" | jq -c '.[]' | while read -r entry; do
            REPO=$(echo "$entry" | jq -r '.repo')
            FIELD=$(echo "$entry" | jq -r '.field')

            # Dedup: skip if open issue with same title exists
            EXISTING=$(gh issue list --repo "n24q02m/${REPO}" \
              --search "${TITLE} in:title" \
              --state open --json number --jq 'length' 2>/dev/null || echo "0")

            if [ "$EXISTING" -gt 0 ]; then
              echo "SKIP: ${REPO} -- issue already exists"
              continue
            fi

            gh issue create --repo "n24q02m/${REPO}" \
              --title "${TITLE}" \
              --label "dependencies,core-update" \
              --body "## Core Library Update

          **${PACKAGE}** has released **${VERSION}**.

          - Release: ${RELEASE_URL}

          ## Action Required

          - [ ] Review release notes for breaking changes
          - [ ] Update version constraint in \`${FIELD}\`
          - [ ] Run tests locally
          - [ ] Create PR with the update"

            echo "CREATED: ${REPO} -- ${TITLE}"
          done
```

- [ ] **Step 2: Verify YAML syntax**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/notify-downstream.yml'))"`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/notify-downstream.yml
git commit -m "feat: add notify-downstream workflow for core update issues"
```

---

### Task 3: Add `notify-downstream` job to `qwen3-embed` CD

**Files:**
- Modify: `qwen3-embed/.github/workflows/cd.yml`

- [ ] **Step 1: Add `notify-downstream` job at the end of `cd.yml`**

Append after the last job (`publish-pypi`):

```yaml
  # =================== Notify Downstream ===================
  notify-downstream:
    name: Notify Downstream
    needs: [release, publish-pypi]
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
            -f 'client_payload[core]=qwen3-embed' \
            -f 'client_payload[version]=${{ needs.release.outputs.version }}' \
            -f 'client_payload[tag]=${{ needs.release.outputs.tag }}' \
            -f 'client_payload[release_url]=https://github.com/${{ github.repository }}/releases/tag/${{ needs.release.outputs.tag }}'
```

- [ ] **Step 2: Verify YAML syntax**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/cd.yml'))"`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/cd.yml
git commit -m "feat: notify downstream repos on stable release"
```

---

### Task 4: Add `notify-downstream` job to `web-core` CD

**Files:**
- Modify: `web-core/.github/workflows/cd.yml`

- [ ] **Step 1: Add `notify-downstream` job at the end of `cd.yml`**

Append after the last job (`publish-pypi`):

```yaml
  # =================== Notify Downstream ===================
  notify-downstream:
    name: Notify Downstream
    needs: [release, publish-pypi]
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
            -f 'client_payload[core]=web-core' \
            -f 'client_payload[version]=${{ needs.release.outputs.version }}' \
            -f 'client_payload[tag]=${{ needs.release.outputs.tag }}' \
            -f 'client_payload[release_url]=https://github.com/${{ github.repository }}/releases/tag/${{ needs.release.outputs.tag }}'
```

- [ ] **Step 2: Verify YAML syntax**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/cd.yml'))"`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/cd.yml
git commit -m "feat: notify downstream repos on stable release"
```

---

### Task 5: Add `notify-downstream` job to `mcp-relay-core` CD

**Files:**
- Modify: `mcp-relay-core/.github/workflows/cd.yml`

- [ ] **Step 1: Add `notify-downstream` job at the end of `cd.yml`**

Append after the last job (`merge-docker`):

```yaml
  # =================== Notify Downstream ===================
  notify-downstream:
    name: Notify Downstream
    needs: [release, publish-npm, publish-pypi]
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
            -f 'client_payload[core]=mcp-relay-core' \
            -f 'client_payload[version]=${{ needs.release.outputs.version }}' \
            -f 'client_payload[tag]=${{ needs.release.outputs.tag }}' \
            -f 'client_payload[release_url]=https://github.com/${{ github.repository }}/releases/tag/${{ needs.release.outputs.tag }}'
```

- [ ] **Step 2: Verify YAML syntax**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/cd.yml'))"`
Expected: No errors

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/cd.yml
git commit -m "feat: notify downstream repos on stable release"
```

---

### Task 6: Add `notify-downstream` job to `knowledge-core` CD

**Files:**
- Modify: `knowledge-core/.github/workflows/cd.yml`

Note: knowledge-core is a private library consumed via `git+ssh://git@github.com/n24q02m/knowledge-core.git@v{tag}` (not PyPI). It runs on `self-hosted` ARM64 and has only a `release` job. The `notify-downstream` job runs on `ubuntu-latest` since it only calls the GitHub API.

- [ ] **Step 1: Add `notify-downstream` job at the end of `cd.yml`**

Append after the `release` job:

```yaml
  # =================== Notify Downstream ===================
  notify-downstream:
    name: Notify Downstream
    needs: [release]
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
            -f 'client_payload[core]=knowledge-core' \
            -f 'client_payload[version]=${{ needs.release.outputs.version }}' \
            -f 'client_payload[tag]=${{ needs.release.outputs.tag }}' \
            -f 'client_payload[release_url]=https://github.com/${{ github.repository }}/releases/tag/${{ needs.release.outputs.tag }}'
```

- [ ] **Step 2: Add `outputs` to `release` job**

The knowledge-core `release` job is missing outputs (confirmed — only has `steps`, no `outputs` block). Add after `runs-on`:

```yaml
    outputs:
      released: ${{ steps.release.outputs.released }}
      tag: ${{ steps.release.outputs.tag }}
      version: ${{ steps.release.outputs.version }}
      is_prerelease: ${{ steps.release.outputs.is_prerelease }}
```

- [ ] **Step 3: Verify YAML syntax**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/cd.yml'))"`
Expected: No errors

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/cd.yml
git commit -m "feat: notify downstream repos on stable release"
```

---

### Task 7: Ensure `core-update` labels exist in downstream repos

**Files:** None (GitHub API only)

- [ ] **Step 1: Create labels in all downstream repos**

Run for each downstream repo that doesn't already have these labels:

```bash
REPOS=(wet-mcp mnemo-mcp better-code-review-graph knowledge-core better-telegram-mcp better-email-mcp better-notion-mcp KnowledgePrism Aiora)

for REPO in "${REPOS[@]}"; do
  gh label create "core-update" \
    --repo "n24q02m/${REPO}" \
    --description "Core library update notification" \
    --color "0052CC" \
    --force 2>/dev/null && echo "CREATED: ${REPO}/core-update" || echo "EXISTS: ${REPO}/core-update"

  gh label create "dependencies" \
    --repo "n24q02m/${REPO}" \
    --description "Dependency updates" \
    --color "0075CA" \
    --force 2>/dev/null && echo "CREATED: ${REPO}/dependencies" || echo "EXISTS: ${REPO}/dependencies"
done
```

Expected: Labels created (or already exist) in all 9 downstream repos.

---

### Task 8: Ensure `n24q02m` repo has CI_APP_ID variable and CI_APP_KEY secret

**Files:** None (GitHub API only)

- [ ] **Step 1: Check if `CI_APP_ID` and `CI_APP_KEY` exist on `n24q02m` repo**

```bash
gh api repos/n24q02m/n24q02m/actions/variables --jq '.variables[].name'
gh api repos/n24q02m/n24q02m/actions/secrets --jq '.secrets[].name'
```

Expected: `CI_APP_ID` in variables, `CI_APP_KEY` in secrets.

- [ ] **Step 2: If missing, add them**

```bash
# Variable (if missing)
gh variable set CI_APP_ID --repo n24q02m/n24q02m --body "3200052"

# Secret (if missing — user must provide the private key)
gh secret set CI_APP_KEY --repo n24q02m/n24q02m < /path/to/app-private-key.pem
```

---

### Task 9: End-to-end test via manual dispatch

- [ ] **Step 1: Trigger `notify-downstream.yml` manually via `repository_dispatch`**

```bash
gh api repos/n24q02m/n24q02m/dispatches \
  -f event_type=core-update \
  -f 'client_payload[core]=qwen3-embed' \
  -f 'client_payload[version]=99.0.0-test' \
  -f 'client_payload[tag]=v99.0.0-test' \
  -f 'client_payload[release_url]=https://github.com/n24q02m/qwen3-embed/releases'
```

- [ ] **Step 2: Verify workflow ran**

```bash
gh run list --repo n24q02m/n24q02m --workflow=notify-downstream.yml --limit 1
```

Expected: One run with status `completed`.

- [ ] **Step 3: Verify issues were created**

```bash
gh issue list --repo n24q02m/wet-mcp --search "Update qwen3-embed to 99.0.0-test" --state open
gh issue list --repo n24q02m/mnemo-mcp --search "Update qwen3-embed to 99.0.0-test" --state open
gh issue list --repo n24q02m/better-code-review-graph --search "Update qwen3-embed to 99.0.0-test" --state open
```

Expected: One issue in each of the 3 repos with correct title, body, and labels.

- [ ] **Step 4: Verify dedup — run dispatch again**

```bash
gh api repos/n24q02m/n24q02m/dispatches \
  -f event_type=core-update \
  -f 'client_payload[core]=qwen3-embed' \
  -f 'client_payload[version]=99.0.0-test' \
  -f 'client_payload[tag]=v99.0.0-test' \
  -f 'client_payload[release_url]=https://github.com/n24q02m/qwen3-embed/releases'
```

Wait for workflow to complete, then verify no duplicate issues were created:

```bash
gh issue list --repo n24q02m/wet-mcp --search "Update qwen3-embed to 99.0.0-test" --json number --jq 'length'
```

Expected: Still `1` (not `2`).

- [ ] **Step 5: Clean up test issues**

```bash
for REPO in wet-mcp mnemo-mcp better-code-review-graph; do
  ISSUE_NUM=$(gh issue list --repo "n24q02m/${REPO}" --search "Update qwen3-embed to 99.0.0-test" --json number --jq '.[0].number')
  if [ -n "$ISSUE_NUM" ]; then
    gh issue close --repo "n24q02m/${REPO}" "$ISSUE_NUM" --reason "not planned"
    echo "CLOSED: ${REPO}#${ISSUE_NUM}"
  fi
done
```

---

### Task 10: Push all changes

- [ ] **Step 1: Push `n24q02m` repo**

```bash
cd n24q02m && git push origin main
```

- [ ] **Step 2: Push core repos (each in its own branch + PR)**

For each core repo (qwen3-embed, web-core, mcp-relay-core, knowledge-core):

```bash
cd {repo}
git checkout -b feat/notify-downstream
git push -u origin feat/notify-downstream
gh pr create --title "Add downstream notification on stable release" --body "$(cat <<'EOF'
## Summary
- Add `notify-downstream` job to CD workflow
- On stable release, dispatches `core-update` event to `n24q02m` repo
- Centralized workflow creates update issues in downstream repos

## Test plan
- [ ] Verify YAML syntax passes
- [ ] Verify CD workflow runs without errors on next release
EOF
)"
```
