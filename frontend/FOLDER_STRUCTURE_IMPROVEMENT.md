# 📁 Folder Structure Improvement Plan

## Overview
This document outlines the plan to improve the Next.js frontend folder structure for better organization, maintainability, and developer experience.

## Current vs Proposed Structure

### Current Structure Issues
- ❌ All components in a single flat folder
- ❌ No feature-based organization
- ❌ Mixed UI and business logic components
- ❌ No dedicated place for custom hooks
- ❌ Utils scattered across different files
- ❌ No clear separation of concerns

### Proposed Structure Benefits
- ✅ Feature-based component organization
- ✅ Clear separation between UI and business logic
- ✅ Dedicated folders for hooks, types, and utilities
- ✅ Better scalability and maintainability
- ✅ Improved developer experience
- ✅ Easier testing and documentation

## Implementation Phases

### Phase 1: Foundation Setup (Low Risk)
Create new folder structure without moving existing files:

```bash
# Create new directories
mkdir -p src/lib
mkdir -p src/hooks
mkdir -p src/types
mkdir -p src/components/ui
mkdir -p src/components/features
mkdir -p src/components/layout
mkdir -p src/services/api
mkdir -p src/store/slices
mkdir -p src/assets/{icons,images,fonts}
mkdir -p src/styles
mkdir -p tests/{__mocks__,components,pages,utils}
mkdir -p docs
```

### Phase 2: Utilities Migration (Low Risk)
Move and organize utility functions:

```typescript
// Create src/lib/utils.ts
export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US').format(date);
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};

// Create src/lib/constants.ts
export const API_ENDPOINTS = {
  BOOKS: '/books',
  USER_BOOKS: '/user-books',
  AUTH: '/auth',
  RECOMMENDATIONS: '/recommendations',
} as const;

export const PAGINATION_DEFAULTS = {
  PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
} as const;

// Create src/lib/validations.ts
import { z } from 'zod';

export const bookSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  author: z.string().min(1, 'Author is required'),
  isbn: z.string().optional(),
});
```

### Phase 3: Types Reorganization (Medium Risk)
Rename and reorganize type definitions:

```typescript
// src/types/index.ts - Barrel exports
export * from './api';
export * from './auth';
export * from './book';
export * from './review';
export * from './user';

// src/types/api.ts - API-specific types
export interface ApiResponse<T> {
  data: T;
  message: string;
  status: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: PaginationMetadata;
}

export interface ApiError {
  message: string;
  status: number;
  details?: string;
}
```

### Phase 4: Component Organization (High Risk)
Restructure components by feature and purpose:

```typescript
// src/components/ui/pagination/index.ts
export { default as Pagination } from './pagination';
export { default as LibraryPagination } from './library-pagination';
export type { PaginationProps } from './pagination';

// src/components/features/books/index.ts
export { default as ExternalBookClient } from './external-book-client';
export { default as UserBookActions } from './user-book-actions';
export { default as BookList } from './book-list';

// src/components/features/navigation/index.ts
export { default as Navbar } from './navbar';
export { default as Sidebar } from './sidebar';
```

### Phase 5: Custom Hooks (Low Risk)
Extract and organize custom hooks:

```typescript
// src/hooks/useBooks.ts
import { useState, useEffect } from 'react';
import { booksService } from '@/services';
import type { Book, PaginatedResponse } from '@/types';

export const useBooks = (page = 1, pageSize = 10) => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBooks = async () => {
      setLoading(true);
      try {
        const response = await booksService.getBooksPaginated(page, pageSize);
        setBooks(response.data);
      } catch (err) {
        setError('Failed to fetch books');
      } finally {
        setLoading(false);
      }
    };

    fetchBooks();
  }, [page, pageSize]);

  return { books, loading, error };
};

// src/hooks/usePagination.ts
import { useState, useMemo } from 'react';

export const usePagination = (totalItems: number, itemsPerPage: number) => {
  const [currentPage, setCurrentPage] = useState(1);

  const paginationData = useMemo(() => {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, totalItems);

    return {
      currentPage,
      totalPages,
      startIndex,
      endIndex,
      hasNext: currentPage < totalPages,
      hasPrevious: currentPage > 1,
    };
  }, [currentPage, totalItems, itemsPerPage]);

  return {
    ...paginationData,
    setCurrentPage,
    nextPage: () => setCurrentPage(prev => Math.min(prev + 1, paginationData.totalPages)),
    previousPage: () => setCurrentPage(prev => Math.max(prev - 1, 1)),
  };
};
```

### Phase 6: Service Layer Enhancement (Medium Risk)
Restructure service layer for better organization:

```typescript
// src/services/api/client.ts
import { API_ENDPOINTS } from '@/lib/constants';

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export const apiClient = {
  get: async <T>(endpoint: string): Promise<T> => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      credentials: 'include',
    });
    if (!response.ok) throw new Error('API request failed');
    return response.json();
  },
  
  post: async <T>(endpoint: string, data: unknown): Promise<T> => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('API request failed');
    return response.json();
  },
};

// src/services/books.ts
import { apiClient } from './api/client';
import type { Book, ExternalBook, PaginatedResponse } from '@/types';

export const booksService = {
  getBooksPaginated: (page = 1, pageSize = 10) =>
    apiClient.get<PaginatedResponse<Book>>(`/books/?page=${page}&page_size=${pageSize}`),
    
  searchExternal: (query: string, page = 1, maxResults = 10) =>
    apiClient.get<PaginatedResponse<ExternalBook>>(
      `/books/search-external?q=${encodeURIComponent(query)}&page=${page}&max_results=${maxResults}`
    ),
    
  getPopular: (page = 1, maxResults = 12) =>
    apiClient.get<PaginatedResponse<ExternalBook>>(
      `/books/popular?page=${page}&max_results=${maxResults}`
    ),
};
```

### Phase 7: Update Configurations
Update configuration files to reflect new structure:

```typescript
// Update .cursorrules
const improvedFolderStructure = `
src/
├── app/                    # Next.js App Router
├── components/
│   ├── ui/                # Reusable UI components
│   ├── features/          # Feature-specific components
│   └── layout/            # Layout components
├── lib/                   # Shared utilities & config
├── hooks/                 # Custom hooks
├── types/                 # Type definitions
├── services/              # API services
├── store/                 # State management
├── assets/                # Static assets
└── styles/                # Style files
`;

// Update tsconfig.json paths
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/hooks/*": ["./src/hooks/*"],
      "@/types/*": ["./src/types/*"],
      "@/services/*": ["./src/services/*"],
      "@/store/*": ["./src/store/*"]
    }
  }
}
```

## Migration Steps

### Step 1: Backup and Branch
```bash
git checkout -b feature/folder-structure-improvement
git add .
git commit -m "Backup before folder structure changes"
```

### Step 2: Create New Structure
```bash
# Run the folder creation commands from Phase 1
# Move files gradually to avoid breaking imports
```

### Step 3: Update Imports Systematically
```bash
# Use find and replace to update import paths
# Test after each major change
```

### Step 4: Update Tests
```bash
# Move test files to new test structure
# Update test imports and paths
```

### Step 5: Documentation
```bash
# Update README.md
# Create component documentation
# Update CLAUDE.md with new structure
```

## Benefits After Implementation

### Developer Experience
- 🔍 **Easier to find files** - Logical organization by feature
- 🧩 **Better code reusability** - Clear separation of UI and business logic
- 🚀 **Faster development** - Consistent patterns and structure
- 🛡️ **Better type safety** - Centralized type definitions

### Maintainability
- 📦 **Modular architecture** - Easy to add/remove features
- 🔄 **Easier refactoring** - Clear boundaries between components
- 🧪 **Better testing** - Organized test structure
- 📚 **Improved documentation** - Clear folder purposes

### Performance
- ⚡ **Better tree-shaking** - Barrel exports enable better bundling
- 🎯 **Selective imports** - Import only what's needed
- 📱 **Faster builds** - Better organized dependencies

## Risk Mitigation

### Low Risk Changes (Do First)
- Creating new folders
- Adding utility functions to lib/
- Adding custom hooks
- Adding barrel exports

### Medium Risk Changes (Do Carefully)
- Moving type definitions
- Restructuring services
- Updating import paths

### High Risk Changes (Do Last)
- Moving components
- Updating component imports across pages
- Refactoring state management

## Success Metrics

- ✅ All existing functionality works without regression
- ✅ Import paths are shorter and more intuitive
- ✅ New components follow the established patterns
- ✅ Build and test times remain stable or improve
- ✅ Developer onboarding time decreases

## Rollback Plan

If issues arise:
1. Revert to backup branch
2. Identify specific problematic changes
3. Apply changes incrementally
4. Test thoroughly between each change

---

*This improvement plan focuses on enhancing code organization while maintaining stability and functionality.*