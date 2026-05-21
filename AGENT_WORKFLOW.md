# Agent Workflow

Standard process for taking a GitHub issue from backlog to merged PR.

---

## Steps

### 1. Pick issue
Choose highest-priority open issue. Note the issue number and title.

### 2. Create feature branch
```bash
git checkout development
git pull origin development
git checkout -b feat/issue-<N>-<short-slug>
```

### 3. Plan with project-planner
Invoke the `project-planner` agent. Give it:
- Issue title + body
- Affected files identified during audit

Agent outputs: **Goal**, **Tasks** (with done-criteria), **Risks**, **Open questions**.
Resolve open questions before proceeding.

### 4. Implement
Route to the correct worker agent based on what's changing:
- Frontend-only → `frontend-worker`
- Backend-only → `backend-worker`
- Both → run both agents (sequentially if dependent, parallel if independent)

Each worker receives the plan output from step 3 as context.

### 5. Evaluate with feature-evaluator
Invoke `feature-evaluator`. It checks:
- Implementation matches acceptance criteria
- Tests pass (typecheck, lint, unit)
- No regressions introduced
- Code follows project conventions

If evaluation fails → fix issues, re-evaluate.

### 6. Validate build with build-validator
Invoke `build-validator`. It runs the full pre-flight check that mirrors Vercel CI:
- `npx tsc --noEmit` — TypeScript
- ESLint on `src/` — lint errors only
- `npm run build` — production build (catches SSR/prerender errors dev mode misses)
- Architecture pattern scan — `useSearchParams` without Suspense, orphaned `'use client'`, `console.log`, etc.
- Backend `pytest` suite

If build-validator fails → route to the correct worker to fix, then re-run build-validator.

### 7. Open PR with pr-creator
Invoke `pr-creator`. It will:
- Verify branch is not `master`
- Target `development` (feature branch → development, development → master)
- Derive title + body from `git log` and `git diff`
- Push branch and open PR via `gh pr create`

---

## Agent Map

| Agent | When to use |
|---|---|
| `project-planner` | Step 3 — always |
| `frontend-worker` | Step 4 — frontend changes |
| `backend-worker` | Step 4 — backend changes |
| `feature-evaluator` | Step 5 — always |
| `build-validator` | Step 6 — always (before PR) |
| `pr-creator` | Step 7 — always |

---

## Branch Naming

```
feat/issue-<N>-<short-slug>    # new feature or improvement
fix/issue-<N>-<short-slug>     # bug fix
chore/issue-<N>-<short-slug>   # cleanup, tooling
```

---

## Example

```
Issue #132 — Add middleware.ts for server-side auth gating

1. git checkout -b feat/issue-132-middleware-auth
2. project-planner   → plan tasks + acceptance criteria
3. frontend-worker   → implement middleware.ts
4. feature-evaluator → verify implementation quality
5. build-validator   → next build + tsc + lint + pytest
6. pr-creator        → open PR to development
```
