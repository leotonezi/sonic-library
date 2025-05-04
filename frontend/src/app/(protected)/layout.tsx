'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import LoadingScreen from '@/components/loading'; // Create this component

export default function ProtectedLayout({ 
  children 
}: { 
  children: React.ReactNode 
}) {
  const router = useRouter();
  const { user, isLoading, checkAuth, logout } = useAuthStore();

  useEffect(() => {
    const initAuth = async () => {
      try {
        const isAuthenticated = await checkAuth();
        if (!isAuthenticated) {
          await logout();
          router.replace('/login');
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        router.replace('/login');
      }
    };

    initAuth();
  }, [checkAuth, logout, router]);

  // Show loading screen while checking authentication
  if (isLoading) {
    return <LoadingScreen />;
  }

  // If not authenticated, don't render anything
  // (we're already redirecting in the useEffect)
  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-blue-950">
      <main>
        {children}
      </main>
    </div>
  );
}