'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import LoadingScreen from '@/components/loading';

export default function Home() {
  const router = useRouter();
  const { isLoading, checkAuth } = useAuthStore();

  useEffect(() => {
    const initAuth = async () => {
      try {
        const isAuthenticated = await checkAuth();
        if (isAuthenticated) {
          // User is authenticated, redirect to books page
          router.replace('/books');
        } else {
          // User is not authenticated, redirect to login
          router.replace('/login');
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        router.replace('/login');
      }
    };

    initAuth();
  }, [checkAuth, router]);

  // Show loading screen while checking authentication
  if (isLoading) {
    return <LoadingScreen />;
  }

  // Don't render anything while redirecting
  return null;
}