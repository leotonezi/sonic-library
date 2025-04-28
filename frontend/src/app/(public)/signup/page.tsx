import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Signup - Sonic Library',
  description: 'Create your account to start your journey in the Sonic Library!',
};

// Define props to match Next.js expectations for async resolution
interface PageProps {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

// Use async function since props are expected to be Promises
export default async function SignupPage({ searchParams }: PageProps) {
  // Resolve the searchParams Promise
  const resolvedSearchParams = await searchParams;
  const error = typeof resolvedSearchParams.error === 'string' ? resolvedSearchParams.error : undefined;

  return (
    <main className="min-h-screen bg-[#0a1128] text-[#e0f0ff] flex items-center justify-center px-4">
      <form
        action={`${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/signup`}
        method="POST"
        className="w-full max-w-md bg-[#001f3f] border border-[#0077cc] p-5 rounded-lg shadow-lg"
      >
        <h1 className="text-3xl font-bold text-[#00aaff] mb-6 text-center">Sign Up</h1>

        {error === 'email_registered' && (
          <p className="text-red-400 text-md px-4 py-1 rounded text-center">
            Email already registered. Please login or use another email.
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