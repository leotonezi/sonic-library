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
    <main className="min-h-screen flex items-center justify-center">
      <form onSubmit={handleSubmit} className="w-full max-w-sm bg-white p-6 rounded shadow">
        <h1 className="text-2xl font-bold mb-4">Login</h1>

        {error && <p className="text-red-500 mb-2">{error}</p>}

        <label className="block mb-2">
          Email:
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full border p-2 mt-1 rounded"
            required
          />
        </label>

        <label className="block mb-4">
          Password:
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full border p-2 mt-1 rounded"
            required
          />
        </label>

        <button type="submit" className="bg-black text-white py-2 px-4 rounded w-full">
          Sign In
        </button>
      </form>
    </main>
  );
}