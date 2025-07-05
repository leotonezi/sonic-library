'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import Link from 'next/link';

export default function SignupPage() {
  const router = useRouter();
  const { checkAuth } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  // Check if user is already authenticated
  useEffect(() => {
    const checkIfAuthenticated = async () => {
      try {
        const isAuthenticated = await checkAuth();
        if (isAuthenticated) {
          // User is already authenticated, redirect to books page
          router.replace('/books');
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      }
    };

    checkIfAuthenticated();
  }, [checkAuth, router]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/signup`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        // Redirect to login with success message
        router.push('/login?signup_success=true');
      } else {
        const data = await response.json();
        if (data.detail === 'Email already registered') {
          setError('email_registered');
        } else {
          setError(data.detail || 'Signup failed');
        }
      }
    } catch (_error) {
      console.error('Error during signup:', _error);
      setError('An error occurred during signup');
    }
  };

  return (
    <main className="min-h-screen bg-[#0a1128] text-[#e0f0ff] flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-[#001f3f] border border-[#0077cc] p-5 rounded-lg shadow-lg"
      >
        <h1 className="text-3xl font-bold text-[#00aaff] mb-6 text-center">Sign Up</h1>

        {error === 'email_registered' && (
          <p className="text-red-400 text-md px-4 py-1 rounded text-center">
            Email already registered. Please login or use another email.
          </p>
        )}

        {error && error !== 'email_registered' && (
          <p className="text-red-400 text-md px-4 py-1 rounded text-center">
            {error}
          </p>
        )}

        <label className="block mb-4">
          <span className="text-sm text-[#cceeff]">Name</span>
          <input
            type="text"
            name="name"
            required
            className="input-primary"
          />
        </label>

        <label className="block mb-4">
          <span className="text-sm text-[#cceeff]">Email</span>
          <input
            type="email"
            name="email"
            required
            className="input-primary"
          />
        </label>

        <label className="block mb-6">
          <span className="text-sm text-[#cceeff]">Password</span>
          <input
            type="password"
            name="password"
            required
            className="input-primary"
          />
        </label>

        <button type="submit" className="btn-primary w-full mb-4">
          Create Account
        </button>

        <p className="text-center text-sm text-[#cceeff]">
          Already have an account?{' '}
          <Link href="/login" className="text-[#00aaff] hover:underline">
            Login here
          </Link>
        </p>
      </form>
    </main>
  );
}