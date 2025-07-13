interface AuthError extends Error {
  status?: number;
  code?: string;
}

interface QueueItem {
  resolve: (token: string | null) => void;
  reject: (error: AuthError) => void;
}

let isRefreshing = false;
let failedQueue: QueueItem[] = [];

const processQueue = (error: AuthError | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

export class TokenRefreshError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'TokenRefreshError';
  }
}

export async function refreshToken(): Promise<boolean> {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/refresh`, {
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

export async function handleTokenRefresh(): Promise<string | null> {
  if (!isRefreshing) {
    isRefreshing = true;

    try {
      const success = await refreshToken();
      processQueue(null, success ? 'refreshed' : null);
    } catch (error) {
      const authError: AuthError = error instanceof Error ? error : new Error('Unknown error');
      processQueue(authError, null);
    } finally {
      isRefreshing = false;
    }
  }

  return new Promise<string | null>((resolve, reject) => {
    failedQueue.push({ resolve, reject });
  });
}