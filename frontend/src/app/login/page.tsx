'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');

    const res = await fetch('http://127.0.0.1:8000/auth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username: email,
        password,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      setError('Invalid credentials');
      return;
    }

    localStorage.setItem('access_token', data.access_token);
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
            className="mt-1 w-full bg-white text-black p-2 rounded focus:outline-none focus:ring-2 focus:ring-[#00aaff]"
            required
          />
        </label>

        <label className="block mb-6">
          <span className="text-sm text-[#cceeff]">Password</span>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="mt-1 w-full bg-white text-black p-2 rounded focus:outline-none focus:ring-2 focus:ring-[#00aaff]"
            required
          />
        </label>

        <button
          type="submit"
          className="bg-[#00aaff] hover:bg-[#0077cc] transition duration-300 text-white font-semibold py-2 px-4 w-full rounded"
        >
          Sign In
        </button>
      </form>
    </main>
  );
}