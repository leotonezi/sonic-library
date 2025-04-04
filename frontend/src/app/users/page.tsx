import { apiFetch } from '@/utils/api';

interface User {
  id: number;
  name: string;
  email: string;
}

export const revalidate = 60;

async function getUsers(): Promise<User[]> {
  const users = await apiFetch<User[]>('/users/');
  return users ?? [];
}

export default async function UsersPage() {
  const users = await getUsers();

  if (!users || users.length === 0) {
    return (
      <main className="p-6">
        <h1 className="text-3xl font-bold mb-4">Users</h1>
        <p className="text-gray-500">No users found.</p>
      </main>
    );
  }

  return (
    <main className="p-6">
      <h1 className="text-3xl font-bold mb-4">Users</h1>
      <ul className="space-y-2">
        {users.map((user) => (
          <li key={user.id} className="border p-4 rounded">
            <h2 className="text-xl font-semibold">{user.name}</h2>
            <p className="text-sm">{user.email}</p>
          </li>
        ))}
      </ul>
    </main>
  );
}