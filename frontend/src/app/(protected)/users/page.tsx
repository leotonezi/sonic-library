'use client';

import { useEffect, useState } from 'react';
import { apiFetch } from '@/utils/api';
import User from '@/interfaces/user';

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUsers() {
      const data = await apiFetch<User[]>('/users/');
      setUsers(data ?? []);
      setLoading(false);
    }

    loadUsers();
  }, []);

  return (
    <main className="p-6">
      <h1 className="text-3xl font-bold mb-4">Users</h1>
      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : users.length === 0 ? (
        <p className="text-gray-500">No users found.</p>
      ) : (
        <ul className="space-y-2">
          {users.map((user) => (
            <li key={user.id} className="border p-4 rounded">
              <h2 className="text-xl font-semibold">{user.name}</h2>
              <p className="text-sm">{user.email}</p>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}