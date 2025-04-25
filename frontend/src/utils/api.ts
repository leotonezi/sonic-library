type ExtendedRequestInit = RequestInit & {
  noCache?: boolean;
};

type ApiResponse<T> = {
  data: T;
  status: string;
  message: string;
};

function getAuthHeader(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
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

  const headers: Record<string, string> = {
    ...(options?.headers instanceof Headers
      ? Object.fromEntries(options.headers.entries())
      : (options?.headers as Record<string, string> || {})),
    ...getAuthHeader(),
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
      throw new Error(`API error ${res.status} on POST ${endpoint}`);
    }

    const json: ApiResponse<T> = await res.json();
    return json.data;
  } catch (error) {
    console.error(`Error in apiPost: ${error}`);
    throw error;
  }
}