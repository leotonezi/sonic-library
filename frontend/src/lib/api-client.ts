import { handleTokenRefresh } from "./auth";

export interface ApiResponse<T> {
  data: T;
  status: string;
  message: string;
}

export interface ExtendedRequestInit extends RequestInit {
  noCache?: boolean;
}

// Base fetch configuration that includes credentials
const baseFetchConfig: RequestInit = {
  credentials: 'include',
};

function getBaseUrl(): string {
  const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!baseUrl) {
    throw new Error("NEXT_PUBLIC_BACKEND_URL is not defined");
  }
  return baseUrl;
}

export class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = getBaseUrl();
  }

  async get<T>(endpoint: string, options?: ExtendedRequestInit): Promise<T | null> {
    const noCache = options?.noCache;

    try {
      const res = await fetch(`${this.baseUrl}${endpoint}`, {
        ...baseFetchConfig,
        ...options,
        headers: {
          ...(options?.headers instanceof Headers
            ? Object.fromEntries(options.headers.entries())
            : (options?.headers || {})),
        },
        cache: noCache ? "no-store" : "force-cache",
      });

      if (!res.ok) {
        if (res.status === 401) {
          try {
            const refreshed = await handleTokenRefresh();
            if (refreshed) {
              return await this.get(endpoint, options);
            }
          } catch (error) {
            console.error("Token refresh failed:", error);
            window.location.href = '/login';
            return null;
          }
        }

        console.warn(`⚠️ API error ${res.status} on ${endpoint}`);
        return null;
      }

      const json: ApiResponse<T> = await res.json();
      return json.data;
    } catch (err) {
      console.error(`❌ Failed to fetch ${endpoint}:`, err);
      return null;
    }
  }

  async post<T, D = unknown>(
    endpoint: string,
    data: D,
    options?: RequestInit
  ): Promise<T> {
    const rawContentType = options?.headers instanceof Headers
      ? options.headers.get("Content-Type")
      : (options?.headers as Record<string, string> || {})["Content-Type"];

    const contentType = rawContentType || "application/json";

    const headers: Record<string, string> = {
      "Content-Type": contentType,
      ...(options?.headers instanceof Headers
        ? Object.fromEntries(options.headers.entries())
        : (options?.headers as Record<string, string> || {})),
    };

    try {
      const res = await fetch(`${this.baseUrl}${endpoint}`, {
        ...baseFetchConfig,
        method: "POST",
        headers,
        body:
          contentType === "application/x-www-form-urlencoded"
            ? (data as string)
            : JSON.stringify(data),
        ...options,
      });

      if (!res.ok) {
        if (res.status === 401) {
          window.location.href = '/login';
          throw new Error('Session expired. Please login again.');
        }

        let errorMessage = `API error ${res.status} on POST ${endpoint}`;

        try {
          const errorData = await res.json();
          if (errorData?.detail) {
            errorMessage = errorData.detail;
          }
        } catch (parseError) {
          console.warn('Failed to parse error JSON:', parseError);
        }

        throw new Error(errorMessage);
      }

      const json: ApiResponse<T> = await res.json();
      return json.data;
    } catch (error) {
      console.error(`Error in POST ${endpoint}:`, error);
      throw error;
    }
  }

  async put<T = unknown>(
    endpoint: string,
    body: unknown,
    options?: RequestInit
  ): Promise<T | null> {
    try {
      const res = await fetch(`${this.baseUrl}${endpoint}`, {
        ...baseFetchConfig,
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...(options?.headers || {}),
        },
        body: JSON.stringify(body),
        ...options,
      });

      if (!res.ok) {
        if (res.status === 401) {
          try {
            const refreshed = await handleTokenRefresh();
            if (refreshed) {
              return await this.put(endpoint, body, options);
            }
          } catch (error) {
            console.error("Token refresh failed:", error);
            window.location.href = '/login';
            return null;
          }
        }
        console.warn(`⚠️ API error ${res.status} on PUT ${endpoint}`);
        return null;
      }

      if (res.status === 204) {
        return null;
      }

      const json = await res.json();
      return (json as ApiResponse<T>).data;
    } catch (err) {
      console.error(`❌ Failed to PUT ${endpoint}:`, err);
      return null;
    }
  }

  async delete<T = unknown>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T | null> {
    try {
      const res = await fetch(`${this.baseUrl}${endpoint}`, {
        ...baseFetchConfig,
        method: "DELETE",
        headers: {
          ...(options?.headers || {}),
        },
        ...options,
      });

      if (!res.ok) {
        if (res.status === 401) {
          try {
            const refreshed = await handleTokenRefresh();
            if (refreshed) {
              return await this.delete(endpoint, options);
            }
          } catch (error) {
            console.error("Token refresh failed:", error);
            window.location.href = '/login';
            return null;
          }
        }
        console.warn(`⚠️ API error ${res.status} on DELETE ${endpoint}`);
        return null;
      }

      if (res.status === 204) {
        return null;
      }

      const json = await res.json();
      return (json as ApiResponse<T>).data;
    } catch (err) {
      console.error(`❌ Failed to DELETE ${endpoint}:`, err);
      return null;
    }
  }
}

// Server-side API fetch for Next.js server components
export async function serverSideApiFetch(
  url: string,
  accessToken: string,
  options: RequestInit & { next?: { revalidate?: number } } = {}
) {
  const mergedHeaders = {
    Cookie: `access_token=${accessToken}`,
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers: mergedHeaders,
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

// Export singleton instance
export const apiClient = new ApiClient();