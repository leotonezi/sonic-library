import { apiFetch, apiPut, apiDelete, apiPost, getBackendUrl } from "@/lib/api-client";
import { handleTokenRefresh } from "@/lib/auth";
import type {
  AdminUser,
  AdminUserDetail,
  AdminReview,
  AdminUserBook,
  AdminStats,
  PaginationResponse,
} from "@/types";

const ADMIN_PREFIX = "/api/v1/admin";

/**
 * Fetch a paginated admin endpoint. These return PaginationResponse directly
 * (not wrapped in ApiResponse), so we can't use apiFetch which extracts .data.
 */
async function adminPaginatedFetch<T>(
  endpoint: string
): Promise<PaginationResponse<T> | null> {
  const BASE_URL = getBackendUrl();

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      credentials: "include",
      cache: "no-store",
    });

    if (!res.ok) {
      if (res.status === 401) {
        const refreshed = await handleTokenRefresh();
        if (refreshed) {
          return adminPaginatedFetch<T>(endpoint);
        }
      }
      console.warn(`⚠️ API error ${res.status} on ${endpoint}`);
      return null;
    }

    return (await res.json()) as PaginationResponse<T>;
  } catch (err) {
    console.error(`❌ Failed to fetch ${endpoint}:`, err);
    return null;
  }
}

export async function getUsers(
  page: number,
  search?: string
): Promise<PaginationResponse<AdminUser> | null> {
  const params = new URLSearchParams({ page: String(page) });
  if (search) params.set("search", search);
  return adminPaginatedFetch<AdminUser>(
    `${ADMIN_PREFIX}/users?${params.toString()}`
  );
}

export async function getUser(id: number): Promise<AdminUserDetail | null> {
  return apiFetch<AdminUserDetail>(`${ADMIN_PREFIX}/users/${id}`, {
    noCache: true,
  });
}

export async function getReviews(
  page: number,
  search?: string
): Promise<PaginationResponse<AdminReview> | null> {
  const params = new URLSearchParams({ page: String(page) });
  if (search) params.set("search", search);
  return adminPaginatedFetch<AdminReview>(
    `${ADMIN_PREFIX}/reviews?${params.toString()}`
  );
}

export async function getUserBooks(
  page: number,
  search?: string
): Promise<PaginationResponse<AdminUserBook> | null> {
  const params = new URLSearchParams({ page: String(page) });
  if (search) params.set("search", search);
  return adminPaginatedFetch<AdminUserBook>(
    `${ADMIN_PREFIX}/user-books?${params.toString()}`
  );
}

export async function getStats(): Promise<AdminStats | null> {
  return apiFetch<AdminStats>(`${ADMIN_PREFIX}/stats`, { noCache: true });
}

export async function updateUser(
  id: number,
  data: { name?: string; email?: string; is_active?: boolean }
): Promise<AdminUser | null> {
  return apiPut<AdminUser>(`${ADMIN_PREFIX}/users/${id}`, data);
}

export async function deleteUser(id: number): Promise<unknown> {
  return apiDelete(`${ADMIN_PREFIX}/users/${id}`);
}

export async function resetUserPassword(
  id: number
): Promise<{ message: string; new_password: string } | null> {
  return apiPost<{ message: string; new_password: string }, Record<string, never>>(
    `${ADMIN_PREFIX}/users/${id}/reset-password`,
    {}
  );
}

export async function updateReview(
  id: number,
  data: { content?: string; rate?: number }
): Promise<AdminReview | null> {
  return apiPut<AdminReview>(`${ADMIN_PREFIX}/reviews/${id}`, data);
}

export async function deleteReview(id: number): Promise<unknown> {
  return apiDelete(`${ADMIN_PREFIX}/reviews/${id}`);
}

export async function deleteUserBook(id: number): Promise<unknown> {
  return apiDelete(`${ADMIN_PREFIX}/user-books/${id}`);
}
