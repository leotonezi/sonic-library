export async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T | null> {
  const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

  if (!BASE_URL) {
    console.warn('⚠️ NEXT_PUBLIC_BACKEND_URL is not defined.');
    return null;
  }

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      cache: 'force-cache',
      ...options,
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