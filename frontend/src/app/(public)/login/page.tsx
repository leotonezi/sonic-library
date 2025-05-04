'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { toast } from "sonner";
import { useAuthStore } from '@/store/useAuthStore';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const setUser = useAuthStore((state) => state.setUser);

  const searchParams = useSearchParams();
  const signupSuccess = searchParams.get('signup_success');

  useEffect(() => {
    if (signupSuccess === 'true') {
      toast.success('Signup successful! Please check your email to activate your account.', { id: 'signup-success' });
    }
  }, [signupSuccess]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const formData = new URLSearchParams({
      username: email,
      password,
    });

    try {
      // Login request
      const loginRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
        credentials: 'include', // Important for cookies
      });

      if (!loginRes.ok) {
        const errorData = await loginRes.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const { data } = await loginRes.json();

      // Set user in store
      setUser(data.user);

      // Show success message
      toast.success('Login successful!');

      // Redirect to books page
      router.push('/books');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#0a1128] text-[#e0f0ff] flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-[#001f3f] border border-[#0077cc] p-6 rounded-lg shadow-lg"
      >
        <h1 className="text-3xl font-bold text-[#00aaff] mb-6 text-center">Login</h1>

        {error && (
          <p className="text-red-400 bg-red-950 px-4 py-2 rounded mb-4 text-center">
            {error}
          </p>
        )}

        <label className="block mb-4">
          <span className="text-sm text-[#cceeff]">Email</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input-primary"
            required
            disabled={isLoading}
          />
        </label>

        <label className="block mb-6">
          <span className="text-sm text-[#cceeff]">Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input-primary"
            required
            disabled={isLoading}
          />
        </label>

        <button 
          type="submit" 
          className="btn-primary w-full relative"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="opacity-0">Sign In</span>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-5 h-5 border-t-2 border-b-2 border-white rounded-full animate-spin"></div>
              </div>
            </>
          ) : (
            'Sign In'
          )}
        </button>

        <p className="text-center text-sm text-white mt-4">
          Don&apos;t have an account?{' '}
          <a href="/signup" className="text-[#00aaff] hover:underline">
            Sign up here
          </a>
        </p>
      </form>
    </main>
  );
}