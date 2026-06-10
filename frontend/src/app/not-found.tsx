import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-blue-950 flex items-center justify-center px-4">
      <div className="bg-blue-900 border border-blue-800 rounded-lg p-8 max-w-md w-full text-center shadow-lg">
        <h1 className="text-6xl font-bold text-blue-500 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-blue-200 mb-3">Page not found</h2>
        <p className="text-blue-400 mb-8">
          The page you are looking for does not exist or has been moved.
        </p>
        <Link
          href="/books"
          className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-2 rounded-lg transition-colors inline-block"
        >
          Go to Library
        </Link>
      </div>
    </div>
  );
}
