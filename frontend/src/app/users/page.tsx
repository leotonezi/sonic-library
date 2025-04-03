import { notFound } from 'next/navigation';

interface User {
  id: number;
  name: string;
  email: string;
}

export const revalidate = 60

async function getUsers(): Promise<User[]> {
  const res = await fetch(`${process.env.BACKEND_URL}/users/`, {
    cache: 'force-cache',
  });
  

  if (!res.ok) {
    notFound();
  }

  const users = await res.json();

  if (!users || users.length === 0) {
    notFound();
  }

  return users;
}

export default async function usersPage() {
  const users = await getUsers();

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