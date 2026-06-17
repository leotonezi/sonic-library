---
description: "Analyze differences between development and master, then open a release PR. Use when asked to 'create a release', 'open release PR', 'release to master', 'ship development to master', or '/release'."
triggers:
  - create a release
  - open release PR
  - release to master
  - ship to master
  - ship development
  - release
---

# Release Skill

Compares `development` → `master`, summarizes all changes, opens a PR.

## Steps

### 1. Verify branch state

```bash
git fetch origin
git log origin/master..origin/development --oneline
```

If output is empty → nothing to release. Stop and tell user.

### 2. Gather diff data (run in parallel)

```bash
# All commits not yet in master
git log origin/master..origin/development --oneline --no-merges

# Files changed
git diff --stat origin/master...origin/development

# Full diff (for PR body summary)
git diff --name-only origin/master...origin/development
```

### 3. Categorize changes

Group changed files by area:
- `backend/` → Backend
- `frontend/` → Frontend
- `.github/` → CI/CD
- `docker*` / `*.yml` at root → Infrastructure
- `*.md` → Docs

### 4. Draft PR title and body

**Title format:** `release: development → master (YYYY-MM-DD)`

**Body format:**

```markdown
## What's included

### Backend
- bullet per meaningful change

### Frontend  
- bullet per meaningful change

### CI/CD / Infrastructure
- bullet per meaningful change

## PRs merged
- #NNN Title
- #NNN Title

## Checklist
- [ ] All CI checks pass on `development`
- [ ] No `.env` or secrets committed
- [ ] Migrations included if schema changed
```

Derive bullets from commit messages and changed file list. List merged PRs by scanning merge commits (`git log --merges --oneline origin/master..origin/development`).

### 5. Ensure on correct branch

```bash
git checkout development
git pull origin development
```

### 6. Open PR

```bash
gh pr create \
  --base master \
  --head development \
  --title "release: development → master ($(date +%Y-%m-%d))" \
  --body "$(cat <<'EOF'
<body from step 4>
EOF
)"
```

Return the PR URL to the user.

### 7. Assign and label the PR

Use the REST API directly (avoid `gh pr edit` which has GraphQL issues with deprecated Projects classic):

```bash
# Get the PR number from step 6 output
gh api repos/{owner}/{repo}/issues/{PR_NUMBER}/assignees \
  -X POST -f 'assignees[]={github_username}'

gh api repos/{owner}/{repo}/issues/{PR_NUMBER}/labels \
  -X POST -f 'labels[]=release'
```

- `{github_username}` = the authenticated user (`gh api user --jq .login`)
- Create the `release` label first if it doesn't exist: `gh label create "release" --color "0075ca" --description "Release PR"`

## Edge cases

- **Already open PR** → `gh pr list --base master --head development` — if one exists, link to it instead of creating a new one.
- **No commits ahead** → stop early, nothing to release.
- **Conflicts** → warn user: "development has conflicts with master — resolve before releasing."
