type ExtendedRequestInit = RequestInit & {
  noCache?: boolean;
};

export async function apiFetch<T>(
  endpoint: string,
  options?: ExtendedRequestInit
): Promise<T | null> {
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