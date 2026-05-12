# Frontend Audit — Sonic Library (Next.js 15 / React 19)

> Conducted: 2026-05-11 | Engineer: Claude Opus (Senior)

---

## Executive Summary

Frontend is functionally workable but ships substantial structural debt, security flaws around auth, and near-zero adoption of Next.js 15 / React 19 surface area. Behaves more like a Next.js 12 SPA bolted onto the App Router than an idiomatic Next.js 15 application.

---

## Critical — Fix Now

### 1. `force-cache` default risks cross-user data leakage

**Files:** `src/lib/api-client.ts:49`, `src/utils/api.ts:37`

Next SSR caches by URL only. With `force-cache` as default, User A could be served User B's cached `/users/me`. The auth cookie is part of the request but not the cache key.

**Fix:** Change default to `no-store`. Use explicit `next: { tags: [...] }` + `revalidateTag` for intentional caching.

```ts
// Before
cache: noCache ? "no-store" : "force-cache"

// After
cache: noCache ? "force-cache" : "no-store"
```

---

### 2. Token-refresh promise queue is logically broken

**Files:** `src/lib/auth.ts:57-75`, `src/utils/auth.ts:57-75`

Push-after-drain pattern: every caller pushes onto `failedQueue` *after* `processQueue` has already drained it. Under contention → hung promises. Without contention → first 401 simulates success but caller hangs.

**Fix:** Single shared inflight promise:

```ts
let inflight: Promise<boolean> | null = null;

export function handleTokenRefresh() {
  if (!inflight) inflight = refreshToken().finally(() => { inflight = null; });
  return inflight;
}
```

---

### 3. No `middleware.ts` — auth is client-only `useEffect`

**File:** `src/app/(protected)/layout.tsx:14-47`

Every protected route renders blank → `useEffect` fires → network call → redirect. Consequences:
- Visible blank flash on every protected navigation
- Unauthorized users receive HTML before redirect
- 8 server pages each repeat the same `cookies()` + `redirect('/login')` boilerplate

**Fix:** Add `src/middleware.ts`:

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

---

## High Priority

### 4. Three parallel drifted type/utility hierarchies

**`src/types/` vs `src/interfaces/`** — diverging shapes of same models:
- `BookStatus` in `src/types/book.ts:77` = `'want_to_read' | 'currently_reading' | 'read'`
- Actual values in code = `'TO_READ' | 'READING' | 'READ'`
- `UserBook.status` in `src/interfaces/book.ts:39` typed as plain `string`
- Two `User` types with different optional fields

**`src/lib/api-client.ts` vs `src/utils/api.ts`** — same HTTP semantics implemented twice.

**`src/lib/book-utils.ts` vs `src/utils/book.ts`** — identical Google Books mapping helpers.

**Action:** Choose `@/types/` (newer, barrel-exported). Migrate all `@/interfaces/*` imports. Delete `src/interfaces/`. Delete `src/utils/api.ts`, `src/utils/auth.ts`, `src/lib/book-utils.ts`.

---

### 5. Admin authorization is cosmetic, not a security boundary

**File:** `src/config.ts:1`

```ts
export const ADMIN_EMAILS = ["admin@sonic.com"];
```

Ships in public client bundle. Used in `navbar.tsx:121` and `admin/page.tsx:30,45` only to show/hide UI. Anyone who knows the `/admin` URL can navigate there. Leaks the admin email.

**Fix:** Add `is_admin: boolean` flag to `/users/me` response. Move check server-side. Remove `ADMIN_EMAILS` from `src/config.ts`.

---

### 6. 11 `console.log`s leak user data in production

`BookRecommendationGraph.tsx:116,120,133,138-150` — logs user and graph data on every mount with emoji prefixes (`🔄`, `📊`, `✅`, `❌`).

`books/external/[externalId]/page.tsx:33` — `console.log(data)` of raw API response.

**Fix:** Strip all. Add ESLint rule:
```json
"no-console": ["error", { "allow": ["error"] }]
```

---

### 7. Navbar layout-shift on every hard navigation

SSR pages fetch user server-side, but `NavBar` (`src/components/navbar.tsx:30-32`) reads from Zustand store which is empty at hydration. User sees navbar pop-in after `checkAuth` resolves.

Three concurrent `GET /users/me` calls racing on fresh visit to `/login` (root page + public layout + login page all call `checkAuth`).

**Fix:** Add thin client `AuthHydrator` component in `(protected)/layout.tsx`:

```tsx
// server component reads cookie, fetches user
const user = await serverSideApiFetch<User>('/users/me', token);

// passes to client hydrator
<AuthHydrator user={user}>{children}</AuthHydrator>
```

```tsx
// AuthHydrator.tsx
'use client';
export function AuthHydrator({ user, children }) {
  useLayoutEffect(() => {
    useAuthStore.setState({ user, isCheckingAuth: false });
  }, []);
  return children;
}
```

---

### 8. `app/page.tsx` is a client component just to redirect

Root route ships React, Zustand, `LoadingScreen`, and `useEffect` just to issue a redirect. Slowest possible path for the most visited route.

**Fix:** Convert to server component:

```tsx
// app/page.tsx
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default async function RootPage() {
  const token = (await cookies()).get('access_token');
  redirect(token ? '/library' : '/login');
}
```

---

## Performance

### 9. `@xyflow/react` loads statically — ~150KB gzipped

`BookRecommendationGraph.tsx` is statically imported into the `/recommendation` page chunk. ReactFlow loads for every user on that route even before the graph renders.

**Fix:**
```ts
const BookRecommendationGraph = dynamic(
  () => import('@/components/features/BookRecommendationGraph'),
  { ssr: false, loading: () => <GraphSkeleton /> }
);
```

---

### 10. `<Image>` sizing is wrong across the app

| File | Issue |
|---|---|
| `books/page.tsx:69-75` | `width={80} height={80}` but CSS `w-24 h-32` — CLS |
| `books/page.tsx:137-143` | Same issue for search results |
| `books/external/[externalId]/page.tsx:73-79` | `width={80} height={80}` with `w-full` CSS |
| `library/page.tsx:130-138` | `sizes="96px 144px"` is invalid syntax |

No `placeholder="blur"` anywhere. No `priority` on above-fold covers.

**Fix:** Match intrinsic dimensions to CSS. Add `priority` to book hero images. Add `placeholder="blur"` with a data URL.

---

### 11. Recommendation page double-fetches LLM endpoint

`recommendation/page.tsx:90-138` — on null data, issues a second `GET` to the same `/recommendations` endpoint just to read `json.message`. N+1 against an LLM-backed endpoint.

**Fix:** Surface `message` from the first response rather than dropping it.

---

### 12. Zero Suspense / streaming

`books/[id]/page.tsx:21-32` — `Promise.all` blocks full render on two sequential fetches. Reviews are the slow half.

**Fix:** Wrap reviews in `<Suspense>`, fetch via child server component:

```tsx
// books/[id]/page.tsx
<Suspense fallback={<ReviewsSkeleton />}>
  <ReviewsList bookId={id} token={token} />
</Suspense>
```

---

### 13. Missing `optimizePackageImports`

**File:** `next.config.ts`

```ts
experimental: {
  optimizePackageImports: ['lucide-react', '@headlessui/react', '@xyflow/react'],
}
```

---

### 14. `useBooks` hook has infinite-loop bug (currently unused)

`src/hooks/useBooks.ts:42`:
```ts
useEffect(() => { fetchBooks(params); }, [fetchBooks, params]);
```
`params` defaults to `{}` — new object reference every render → infinite refetch. Unused now but dangerous if wired up.

---

## React 19 / Next.js 15 — Completely Untouched

| Feature | Where it should be used |
|---|---|
| Server Actions (`'use server'`) | Login, signup, add-review, settings, book status changes |
| `useActionState` / `useFormStatus` | All forms — manual `isSubmitting` state everywhere |
| `useOptimistic` | `user-book-actions.tsx` — eliminates local state desync and `router.refresh()` hacks |
| `useTransition` | Admin tab switching, pagination |
| `error.tsx` | Zero exist in entire `app/` directory |
| `loading.tsx` | Zero exist in entire `app/` directory |
| `revalidateTag` / `revalidatePath` | No mutation invalidates any cache |
| Tagged fetches (`next: { tags }`) | All SSR fetches are uncached |
| Partial Prerendering | Books listing page is a prime candidate |

### Example: Replace `user-book-actions.tsx` with Server Action + `useOptimistic`

```tsx
// actions/book-status.ts
'use server';
import { revalidateTag } from 'next/cache';

export async function updateBookStatus(userBookId: number, status: BookStatus) {
  await apiClient.put(`/user-books/${userBookId}`, { status });
  revalidateTag('user-books');
}

// user-book-actions.tsx
const [optimisticStatus, setOptimisticStatus] = useOptimistic(currentStatus);

async function handleStatusChange(status: BookStatus) {
  setOptimisticStatus(status);
  await updateBookStatus(userBook.id, status);
}
```

---

## Type Safety Gaps

### 15. `ApiResponse<T>` unwrapping loses null safety

`src/lib/api-client.ts:74` returns `json.data` typed as `T` (not `T | null`). The `data?: T | null` in `src/interfaces/auth.ts:3-8` is ignored by callers in `books/[id]/page.tsx:33` and `books/external/[externalId]/page.tsx:27`.

### 16. `UserBook.status` typed as `string`

`src/interfaces/book.ts:39` — should be:
```ts
status: 'TO_READ' | 'READING' | 'READ';
```

### 17. `BookRecommendation` cast without validation

`recommendation/page.tsx:25-87` — regex-parses LLM text then `as BookRecommendation` casts without checking `title`/`authors`/`description`. `book.authors.join(", ")` will throw at runtime if parsing fails.

### 18. Admin tab cast is unsafe

`admin/page.tsx:27`:
```ts
(searchParams.get("tab") as TabKey) || "users"
```
`?tab=hax` passes through. Validate against `TABS.map(t => t.key)`.

### 19. No runtime validation at API boundaries

Zero use of `zod` or any schema validator. Every API response is implicitly trusted. Add zod schemas in `src/types/`, validate in `api-client.ts` before returning.

---

## Dev Hygiene

### 20. `postinstall` script runs hidden `next.build()`

`package.json:10`:
```json
"postinstall": "node -e \"try{require('next')?.build?.()}catch(e){}\""
```
Runs (silently fails) on every `npm install`. Slows CI. Remove.

### 21. `dev` script wipes incremental cache every start

```json
"dev": "rm -rf .next && next dev"
```
Defeats Next's incremental compilation. Remove the `rm -rf .next`. Use `next dev --turbopack`.

### 22. `NEXT_PUBLIC_BACKEND_URL` used in server components

`library/page.tsx:24`, `profile/page.tsx:17`, `books/[id]/page.tsx:23,27`, `books/external/[externalId]/page.tsx:22` — server components should use a private `BACKEND_INTERNAL_URL` env var. `NEXT_PUBLIC_*` exposes the upstream URL in the client bundle unnecessarily.

### 23. Font variable typo

`layout.tsx:19,40` — `merriwether` should be `merriweather`. Doesn't match CSS variable `--font-merriweather`.

### 24. Duplicate pagination components

`src/components/pagination.tsx` and `src/components/library-pagination.tsx` implement the same thing. Merge into one component parameterized by an `onPageChange` strategy.

### 25. `<a href>` instead of `<Link>` causes full page reloads

`library/page.tsx:94-115` — status filter tabs use `<a href="?status=...">`. Replace with `<Link>` to preserve scroll and skip full reload.

### 26. No `error.tsx` / `not-found.tsx`

Server component errors in `books/[id]/page.tsx:108-120` and `books/external/[externalId]/page.tsx:141-154` are caught inline as JSX, which defeats Next's error boundary recovery and drops the navbar from error states.

**Fix:** Add at minimum:
- `src/app/(protected)/error.tsx`
- `src/app/(protected)/loading.tsx`
- `src/app/not-found.tsx`

---

## Risk Summary

| Severity | Issue | File(s) |
|---|---|---|
| **Critical** | `force-cache` default risks cross-user cache leakage | `api-client.ts:49`, `utils/api.ts:37` |
| **Critical** | Token-refresh promise queue is broken | `lib/auth.ts:57-75` |
| **High** | No middleware auth gating — client `useEffect` only | `(protected)/layout.tsx:14-47` |
| **High** | Admin auth is cosmetic, email leaked in bundle | `src/config.ts:1` |
| **High** | Three drifted type/util hierarchies | `src/types/` vs `src/interfaces/` |
| **High** | `console.log` of user/graph data in production | `BookRecommendationGraph.tsx:116-150` |
| **Medium** | Navbar layout-shift on hydration | `navbar.tsx:30-32` |
| **Medium** | `<Image>` mis-sized, no priority/blur | `books/page.tsx:69-75` |
| **Medium** | Zero Server Actions / `useOptimistic` / `useActionState` | entire `app/` |
| **Medium** | No `error.tsx` / `loading.tsx` anywhere | `app/` |
| **Medium** | Recommendation page double-fetches LLM endpoint | `recommendation/page.tsx:90-138` |
| **Low** | `useBooks` hook has infinite-loop bug (unused) | `hooks/useBooks.ts:42` |
| **Low** | `postinstall` runs hidden build on npm install | `package.json:10` |
| **Low** | Dev script wipes incremental cache | `package.json:7` |

---

## Suggested Fix Order

1. ~~Fix token-refresh queue (`src/lib/auth.ts`) + change `force-cache` default~~ ✅ Done (branch: fix/token-queue)
2. ~~Add `src/middleware.ts`~~ ✅ Done (branch: fix/middleware)
3. Consolidate type/util hierarchies (pick one tree, delete the other)
4. Strip all `console.log`s, add ESLint `no-console`
5. Dynamic import ReactFlow
6. Fix `<Image>` sizing
7. Add `error.tsx` + `loading.tsx`
8. Adopt Server Actions on forms (login → signup → reviews → book status)
9. Add zod validation at API boundaries
10. Move admin auth check server-side
