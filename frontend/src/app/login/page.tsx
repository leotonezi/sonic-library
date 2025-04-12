'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiPost } from '@/utils/api';
import { ApiResponse, AuthResponse } from '@/types/auth';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
  
    const formData = new URLSearchParams({
      username: email,
      password,
    });
  
    const res = await apiPost<AuthResponse>(
      '/auth/token',
      formData.toString(),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
  
    if (!res || !res.access_token) {
      setError('Invalid credentials or unexpected error.');
      return;
    }
  
    const { access_token } = res;
    localStorage.setItem('access_token', access_token);
    router.push('/books');
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
            onChange={e => setEmail(e.target.value)}
            className="input-primary"
            required
          />
        </label>

        <label className="block mb-6">
          <span className="text-sm text-[#cceeff]">Password</span>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="input-primary"
            required
          />
        </label>

        <button
          type="submit"
          className="btn-primary w-full"
        >
          Sign In
        </button>
      </form>
    </main>
  );
}
