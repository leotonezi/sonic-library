// components/AuthGuard.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { checkAuth, isLoading } = useAuthStore();

  useEffect(() => {
    checkAuth().then(isAuthenticated => {
      if (!isAuthenticated) {
        router.push('/login');
      }
    });
  }, [checkAuth, router]);

  if (isLoading) {
    return <div>Loading...</div>; // or your loading component
  }

  return <>{children}</>;
}