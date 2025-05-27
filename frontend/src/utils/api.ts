import { handleTokenRefresh } from "./auth";

type ExtendedRequestInit = RequestInit & {
  noCache?: boolean;
};

type ApiResponse<T> = {
  data: T;
  status: string;
  message: string;
};

// Base fetch configuration that includes credentials
const baseFetchConfig: RequestInit = {
  credentials: 'include', // This ensures cookies are sent with requests
};

export async function apiFetch<T>(
  endpoint: string,
  options?: ExtendedRequestInit
): Promise<T | null> {
  const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!BASE_URL) {
    console.warn("⚠️ NEXT_PUBLIC_BACKEND_URL is not defined.");
    return null;
  }

  const noCache = options?.noCache;

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
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
            return await apiFetch(endpoint, options);
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

export async function apiPost<T, D = unknown>(
  endpoint: string,
  data: D,
  options?: RequestInit
): Promise<T> {
  const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!BASE_URL) {
    throw new Error("NEXT_PUBLIC_BACKEND_URL is not defined.");
  }

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
    const res = await fetch(`${BASE_URL}${endpoint}`, {
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
    console.error(`Error in apiPost:`, error);
    throw error;
  }
}

export async function apiDelete<T = unknown>(
  endpoint: string,
  options?: RequestInit
): Promise<T | null> {
  const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

  if (!BASE_URL) {
    console.warn("⚠️ NEXT_PUBLIC_BACKEND_URL is not defined.");
    return null;
  }

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
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
            // Retry the original request
            return await apiFetch(endpoint, options);
          }
        } catch (error) {
          console.error("Error on apiDelete:", error);
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

export async function apiPut<T = unknown>(
  endpoint: string,
  body: unknown,
  options?: RequestInit
): Promise<T | null> {
  const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

  if (!BASE_URL) {
    console.warn("⚠️ NEXT_PUBLIC_BACKEND_URL is not defined.");
    return null;
  }

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
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
            return await apiFetch(endpoint, options);
          }
        } catch (error) {
          console.error("Error on apiPut:", error);
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