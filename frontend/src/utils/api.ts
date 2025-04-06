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

export async function apiPost<T>(
  endpoint: string,
  data: T | unknown,
  options?: RequestInit
): Promise<T | null> {
  const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

  if (!BASE_URL) {
    console.warn('⚠️ NEXT_PUBLIC_BACKEND_URL is not defined.');
    return null;
  }

  try {
    const headers = new Headers({
      'Content-Type': 'application/json',
    });

    // Add additional headers from options
    if (options?.headers) {
      Object.entries(options.headers).forEach(([key, value]) => {
        headers.set(key, value as string);
      });
    }

    const res = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body:
        headers.get('Content-Type') === 'application/x-www-form-urlencoded'
          ? data // already stringified
          : JSON.stringify(data),
      ...options,
    });

    if (!res.ok) {
      console.warn(`⚠️ API error ${res.status} on POST ${endpoint}`);
      return null;
    }

    const responseData = await res.json();
    return responseData;
  } catch (err) {
    console.error(`❌ Failed to POST to ${endpoint}:`, err);
    return null;
  }
}
