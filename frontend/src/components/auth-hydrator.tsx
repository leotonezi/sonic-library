'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';

export function AuthHydrator() {
  const user = useAuthStore((state) => state.user);
  const isCheckingAuth = useAuthStore((state) => state.isCheckingAuth);
  const checkAuth = useAuthStore((state) => state.checkAuth);
  const router = useRouter();

  useEffect(() => {
    if (!user && !isCheckingAuth) {
      checkAuth().then((isAuth) => {
        if (!isAuth) {
          router.replace('/login');
        }
      });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return null;
}
