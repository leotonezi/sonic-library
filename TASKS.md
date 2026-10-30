# Tasks

GitHub issues are the source of truth. This file is a snapshot; "needs issue" means no issue number could be confirmed (`gh` was unavailable, so open issues and PRs were not read).

## Now

- Remove the `postinstall` script that silently runs `next.build()` on every install (FRONTEND_AUDIT.md #20, still in `frontend/package.json:10`) — needs issue
- Stop `dev` script wiping `.next` on every start (FRONTEND_AUDIT.md #21, still in `frontend/package.json:6`) — needs issue
- Fix flaky "add book" e2e test: toast never appears after click in CI (TODO in `frontend/e2e/library/add-book.spec.ts:5`) — needs issue

## Next

- Use a private `BACKEND_INTERNAL_URL` instead of `NEXT_PUBLIC_BACKEND_URL` in server components (FRONTEND_AUDIT.md #22; still used in `books/external/[externalId]/page.tsx`, `books/[id]/review-list.tsx`, `profile/page.tsx`, `settings/page.tsx`) — needs issue
- Merge `components/pagination.tsx` and `components/library-pagination.tsx` (FRONTEND_AUDIT.md #24) — needs issue
- Add `optimizePackageImports` to `frontend/next.config.js` (FRONTEND_AUDIT.md #13) — needs issue

## Later

- Validate API responses with zod at the `api-client.ts` boundary; zod is not a dependency yet (FRONTEND_AUDIT.md #19) — needs issue

## Ideas

- Adopt Server Actions, `useActionState` and `useOptimistic` for forms and book status changes (FRONTEND_AUDIT.md, "React 19 / Next.js 15") (inferred) — needs issue

## Not checked

- Recommendation page double-fetch (FRONTEND_AUDIT.md #11) and `UserBook.status` typing (#16) were not re-verified against the code.
