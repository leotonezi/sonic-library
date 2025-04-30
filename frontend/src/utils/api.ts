type ExtendedRequestInit = RequestInit & {
  noCache?: boolean;
};

type ApiResponse<T> = {
  data: T;
  status: string;
  message: string;
};

export function getAuthHeader(): Record<string, string> {
  if (typeof window === 'undefined') return {};

  const persistedAuth = localStorage.getItem('auth-storage');
  if (!persistedAuth) return {};

  try {
    const parsed = JSON.parse(persistedAuth);
    const token = parsed.state?.accessToken;

    if (!token) return {};

    return { Authorization: `Bearer ${token}` };
  } catch (err) {
    console.error('Failed to parse auth-storage:', err);
    return {};
  }
}

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

  const headers = {
    ...getAuthHeader(),
    ...(options?.headers instanceof Headers
      ? Object.fromEntries(options.headers.entries())
      : (options?.headers || {})),
  };

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
      cache: noCache ? "no-store" : "force-cache",
    });

    if (!res.ok) {
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
    ...getAuthHeader(),
    ...(options?.headers instanceof Headers
      ? Object.fromEntries(options.headers.entries())
      : (options?.headers as Record<string, string> || {})),
  };

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: "POST",
      headers,
      body:
        contentType === "application/x-www-form-urlencoded"
          ? (data as string)
          : JSON.stringify(data),
      ...options,
    });

    if (!res.ok) {
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

  const headers = {
    ...getAuthHeader(),
    ...(options?.headers || {}),
  };

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: "DELETE",
      headers,
      ...options,
    });

    if (!res.ok) {
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

  const headers = {
    "Content-Type": "application/json",
    ...getAuthHeader(),
    ...(options?.headers || {}),
  };

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: "PUT",
      headers,
      body: JSON.stringify(body),
      ...options,
    });

    if (!res.ok) {
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