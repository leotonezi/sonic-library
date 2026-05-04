# Frontend Source (`src/`)

## Import Aliases

Use `@/` path mappings (configured in tsconfig.json):
```typescript
import { apiClient } from '@/lib/api-client'
import { Book } from '@/types'
import { useAuthStore } from '@/store/useAuthStore'
```

## Key Modules

### `lib/api-client.ts`
Centralized HTTP client with auth cookie handling:
```typescript
const books = await apiClient.get<Book[]>('/books')
await apiClient.post('/user-books', { book_id: 123 })
```

### `store/` — Zustand State Management
```typescript
const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isLoading: false,
  checkAuth: async () => { ... },
  logout: async () => { ... }
}))
```

Stores: `useAuthStore`, `useSearchBookStore`

### `app/` — App Router Pages
- `(public)/` — Login, signup (no auth required)
- `(protected)/layout.tsx` — Auth wrapper, redirects to `/login` if unauthorized

### `components/`
- `navbar.tsx` — Global navigation with search
- `pagination.tsx` — Reusable pagination
- `features/` — Feature-specific components (e.g., `BookRecommendationGraph.tsx`)

### `services/`
API communication layer (e.g., `bookService.ts`)

### `types/`
TypeScript interfaces for all data models

### `hooks/`
Custom React hooks

## Auth Flow (Frontend Side)

1. Login → `POST /auth/token` → cookie set → `useAuthStore.setUser()` → redirect to `/books`
2. Page load → `checkAuth()` → `GET /users/me` → 401? redirect to `/login`
3. Logout → `POST /auth/logout` → clear state → redirect to `/login`

## Graph Visualization

- Uses `@xyflow/react`
- Nodes: user's books + recommended books
- Edges: similarity relationships
- Interactive pan/zoom
