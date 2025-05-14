import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center text-3xl">
      <div>
        Hello, Sonic Library! 🚀
      </div>
      <div className="text-2xl mt-4">
        <Link href="/login" className="text-blue-500 hover:underline">
          Go to Login
        </Link>
      </div>
    </main>
  );
}