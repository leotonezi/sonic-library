type ExtendedRequestInit = RequestInit & {
  noCache?: boolean;
};

export async function apiFetch<T>(endpoint: string, options?: ExtendedRequestInit): Promise<T | null> {
  const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

  if (!BASE_URL) {
    console.warn('⚠️ NEXT_PUBLIC_BACKEND_URL is not defined.');
    return null;
  }

  const noCache = options?.noCache;

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      cache: noCache ? "no-store" : "force-cache",
    });

    if (!res.ok) {
      console.warn(`⚠️ API error ${res.status} on ${endpoint}`);
      return null;
    }

    const data = await res.json();
    return data;
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
    throw new Error('NEXT_PUBLIC_BACKEND_URL is not defined.');
  }

  // Ensure headers are treated as a plain object for indexing
  const headers = {
    'Content-Type': 'application/json',
    ...(options?.headers || {}),
  } as Record<string, string>;

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body:
        headers['Content-Type'] === 'application/x-www-form-urlencoded'
          ? (data as string) // already stringified
          : JSON.stringify(data),
      ...options,
    });

    if (!res.ok) {
      throw new Error(`API error ${res.status} on POST ${endpoint}`);
    }

    return await res.json();
  } catch (error) {
    console.error(`Error in apiPost: ${error}`);
    throw error; // Re-throw the error after logging it
  }
}