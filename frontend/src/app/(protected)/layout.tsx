import { AuthHydrator } from '@/components/auth-hydrator';

export default function ProtectedLayout({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <main className="min-h-screen bg-blue-950">
      <AuthHydrator />
      {children}
    </main>
  );
}
