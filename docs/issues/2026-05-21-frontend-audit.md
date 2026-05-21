# Frontend Audit — Sonic Library (2026-05-21)

## Issue 1 — Add middleware.ts for server-side auth gating

**Severity:** High
**File:** `frontend/src/middleware.ts`

Every protected route currently renders blank → `useEffect` fires → network call → redirect. Unauthorized users receive full HTML before redirect. 8 server pages each repeat the same `cookies()` + `redirect('/login')` boilerplate.

**Fix:** Create `src/middleware.ts`:

```ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');
  if (!token) return NextResponse.redirect(new URL('/login', request.url));
  return NextResponse.next();
}

export const config = {
  matcher: ['/(library|books|profile|settings|admin|recommendation)(.*)'],
};
```

## Issue 2 — Consolidate three drifted type/utility hierarchies

**Severity:** High
**File:** `frontend/src/types/`, `frontend/src/interfaces/`, `frontend/src/lib/`, `frontend/src/utils/`

- `BookStatus` in `src/types/book.ts` = `'want_to_read' | 'currently_reading' | 'read'` — actual runtime values are `'TO_READ' | 'READING' | 'READ'`
- `UserBook.status` in `src/interfaces/book.ts:39` typed as plain `string`
- Two `User` types with different optional fields
- `src/lib/api-client.ts` vs `src/utils/api.ts` — same HTTP semantics implemented twice
- `src/lib/book-utils.ts` vs `src/utils/book.ts` — identical Google Books mapping helpers

**Fix:** Choose `@/types/` (newer, barrel-exported). Migrate all `@/interfaces/*` imports. Delete `src/interfaces/`. Delete `src/utils/api.ts`, `src/utils/auth.ts`, `src/lib/book-utils.ts`.

## Issue 3 — Admin authorization is cosmetic, leaks email in bundle

**Severity:** High
**File:** `frontend/src/config.ts`

`ADMIN_EMAILS = ["admin@sonic.com"]` ships in the public client bundle. Used in `navbar.tsx:121` and `admin/page.tsx:30,45` only to show/hide UI. Anyone who knows the `/admin` URL can navigate there. Leaks the admin email address.

**Fix:** Add `is_admin: boolean` to `/users/me` response. Move check server-side. Remove `ADMIN_EMAILS` from `src/config.ts`.

## Issue 4 — Remove console.log statements leaking user/graph data

**Severity:** High
**File:** `frontend/src/components/features/BookRecommendationGraph.tsx`, `frontend/src/app/(protected)/books/external/[externalId]/page.tsx`

11 `console.log` calls leak user and graph data in production:
- `BookRecommendationGraph.tsx:116,120,133,138-150` — logs user and graph data on every mount with emoji prefixes
- `books/external/[externalId]/page.tsx:33` — `console.log(data)` of raw API response
- `books/page.tsx:210` — stray console.log

**Fix:** Strip all. Add ESLint rule:
```json
"no-console": ["error", { "allow": ["error"] }]
```

## Issue 5 — Fix navbar hydration layout-shift (AuthHydrator pattern)

**Severity:** Medium
**File:** `frontend/src/components/navbar.tsx`, `frontend/src/app/(protected)/layout.tsx`

`NavBar` reads from Zustand store which is empty at hydration. User sees navbar pop-in after `checkAuth` resolves. Three concurrent `GET /users/me` calls race on fresh visit.

**Fix:** Add thin client `AuthHydrator` component in `(protected)/layout.tsx` that hydrates Zustand from server-fetched user via `useLayoutEffect`.

## Issue 6 — Convert app/page.tsx root redirect to server component

**Severity:** Medium
**File:** `frontend/src/app/page.tsx`

Root route ships React, Zustand, `LoadingScreen`, and `useEffect` just to issue a redirect. Slowest path for most-visited route.

**Fix:**
```tsx
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default async function RootPage() {
  const token = (await cookies()).get('access_token');
  redirect(token ? '/library' : '/login');
}
```

## Issue 7 — Dynamic import @xyflow/react (~150KB gzipped)

**Severity:** Medium
**File:** `frontend/src/app/(protected)/recommendation/page.tsx`

`BookRecommendationGraph` is statically imported, loading ~150KB gzipped ReactFlow for every user on the route before the graph renders.

**Fix:**
```ts
const BookRecommendationGraph = dynamic(
  () => import('@/components/features/BookRecommendationGraph'),
  { ssr: false, loading: () => <GraphSkeleton /> }
);
```

## Issue 8 — Fix Next.js Image sizing across the app

**Severity:** Medium
**File:** `frontend/src/app/(protected)/books/page.tsx`, `frontend/src/app/(protected)/library/page.tsx`, `frontend/src/app/(protected)/books/external/[externalId]/page.tsx`

| File | Issue |
|---|---|
| `books/page.tsx:69-75` | `width={80} height={80}` but CSS `w-24 h-32` — causes CLS |
| `books/page.tsx:137-143` | Same issue for search results |
| `books/external/[externalId]/page.tsx:73-79` | `width={80} height={80}` with `w-full` CSS |
| `library/page.tsx:130-138` | `sizes="96px 144px"` is invalid syntax |

No `placeholder="blur"` anywhere. No `priority` on above-fold covers.

**Fix:** Match intrinsic dimensions to CSS. Add `priority` to hero images. Add `placeholder="blur"` with a data URL.

## Issue 9 — Fix recommendation page double-fetch of LLM endpoint

**Severity:** Medium
**File:** `frontend/src/app/(protected)/recommendation/page.tsx`

On null data, issues a second `GET` to the same `/recommendations` endpoint just to read `json.message`. N+1 against an LLM-backed endpoint.

**Fix:** Surface `message` from the first response instead of dropping it.

## Issue 10 — Add Suspense / streaming to book detail page

**Severity:** Medium
**File:** `frontend/src/app/(protected)/books/[id]/page.tsx`

`Promise.all` blocks full render on two sequential fetches. Reviews are the slow half.

**Fix:**
```tsx
<Suspense fallback={<ReviewsSkeleton />}>
  <ReviewsList bookId={id} token={token} />
</Suspense>
```

## Issue 11 — Add error.tsx and loading.tsx route segments

**Severity:** Medium
**File:** `frontend/src/app/(protected)/`

Zero `error.tsx` or `loading.tsx` files in the entire `app/` directory. Server component errors in `books/[id]/page.tsx` and `books/external/[externalId]/page.tsx` are caught inline as JSX, which defeats Next's error boundary recovery and drops the navbar from error states.

**Fix:** Add at minimum:
- `src/app/(protected)/error.tsx`
- `src/app/(protected)/loading.tsx`
- `src/app/not-found.tsx`

## Issue 12 — Fix UserBook.status typed as string

**Severity:** Medium
**File:** `frontend/src/interfaces/book.ts`

`UserBook.status` at line 39 is typed as plain `string` instead of the union type.

**Fix:**
```ts
status: 'TO_READ' | 'READING' | 'READ';
```

## Issue 13 — Fix unsafe BookRecommendation cast from LLM text

**Severity:** High
**File:** `frontend/src/app/(protected)/recommendation/page.tsx`

Regex-parses LLM text then casts `as BookRecommendation` without checking `title`/`authors`/`description`. `book.authors.join(", ")` will throw at runtime if parsing fails.

**Fix:** Validate parsed fields before cast. Guard `authors` access with nullish coalescing.

## Issue 14 — Fix unsafe admin tab cast from URL param

**Severity:** Medium
**File:** `frontend/src/app/(protected)/admin/page.tsx`

```ts
(searchParams.get("tab") as TabKey) || "users"
```
`?tab=hax` passes through. Validate against `TABS.map(t => t.key)` before casting.

## Issue 15 — Remove postinstall hidden build script

**Severity:** Low
**File:** `frontend/package.json`

`"postinstall": "node -e \"try{require('next')?.build?.()}catch(e){}\""` runs (silently fails) on every `npm install`, slowing CI.

**Fix:** Remove the `postinstall` entry from `package.json`.

## Issue 16 — Fix dev script wiping incremental Next.js cache

**Severity:** Low
**File:** `frontend/package.json`

`"dev": "rm -rf .next && next dev"` defeats Next's incremental compilation on every dev start.

**Fix:** Remove `rm -rf .next`. Use `next dev --turbopack`.

## Issue 17 — Use BACKEND_INTERNAL_URL in server components

**Severity:** Low
**File:** `frontend/src/app/(protected)/library/page.tsx`, `frontend/src/app/(protected)/profile/page.tsx`, `frontend/src/app/(protected)/books/[id]/page.tsx`, `frontend/src/app/(protected)/books/external/[externalId]/page.tsx`

Server components use `NEXT_PUBLIC_BACKEND_URL`, which exposes the upstream URL in the client bundle unnecessarily.

**Fix:** Add private `BACKEND_INTERNAL_URL` env var. Use it in all server-side fetch calls.

## Issue 18 — Fix font variable typo merriweather

**Severity:** Low
**File:** `frontend/src/app/layout.tsx`

`merriwether` at lines 19 and 40 doesn't match CSS variable `--font-merriweather`.

**Fix:** Rename `merriwether` → `merriweather` in `layout.tsx`.

## Issue 19 — Merge duplicate pagination components

**Severity:** Low
**File:** `frontend/src/components/pagination.tsx`, `frontend/src/components/library-pagination.tsx`

Two components implement the same pagination UI. 

**Fix:** Merge into one component parameterized by `onPageChange` strategy. Delete the redundant file.

## Issue 20 — Replace anchor tags with Next.js Link in library page

**Severity:** Low
**File:** `frontend/src/app/(protected)/library/page.tsx`

Status filter tabs at lines 94-115 use `<a href="?status=...">`, causing full page reloads instead of client-side navigation.

**Fix:** Replace `<a href>` with `<Link>` to preserve scroll and skip full reload.

## Issue 21 — Fix useBooks hook infinite refetch loop

**Severity:** Low
**File:** `frontend/src/hooks/useBooks.ts`

```ts
useEffect(() => { fetchBooks(params); }, [fetchBooks, params]);
```
`params` defaults to `{}` — new object reference every render → infinite refetch. Currently unused but dangerous if wired up.

**Fix:** Stabilize `params` with `useMemo` or move default inside the hook.

## Issue 22 — Add optimizePackageImports to next.config.ts

**Severity:** Low
**File:** `frontend/next.config.ts`

Missing bundle optimization for large icon/UI libraries.

**Fix:**
```ts
experimental: {
  optimizePackageImports: ['lucide-react', '@headlessui/react', '@xyflow/react'],
}
```
