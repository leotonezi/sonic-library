'use client';

import { useLayoutEffect } from 'react';
import { useAuthStore } from '@/store/useAuthStore';

export function AuthHydrator() {
  const isCheckingAuth = useAuthStore((state) => state.isCheckingAuth);
  const hasHydrated = useAuthStore((state) => state.hasHydrated);
  const checkAuth = useAuthStore((state) => state.checkAuth);

  useLayoutEffect(() => {
    if (!hasHydrated && !isCheckingAuth) {
      checkAuth();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return null;
}
