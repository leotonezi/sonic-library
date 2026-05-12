import { getBackendUrl } from '@/lib/api-client';

export class TokenRefreshError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'TokenRefreshError';
  }
}

export async function refreshToken(): Promise<boolean> {
  try {
    const response = await fetch(`${getBackendUrl()}/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
    });

    if (!response.ok) {
      throw new TokenRefreshError('Token refresh failed', response.status);
    }

    return true;
  } catch (error) {
    if (error instanceof TokenRefreshError) {
      console.error('Error refreshing token:', error.message, 'Status:', error.status);
    } else {
      console.error('Error refreshing token:', error);
    }
    return false;
  }
}

let inflight: Promise<boolean> | null = null;

export function handleTokenRefresh(): Promise<boolean> {
  if (!inflight) {
    inflight = refreshToken().finally(() => {
      inflight = null;
    });
  }
  return inflight;
}