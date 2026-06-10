'use client';

export default function PublicError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen bg-blue-950 flex items-center justify-center px-4">
      <div className="bg-blue-900 border border-blue-800 rounded-lg p-8 max-w-md w-full text-center shadow-lg">
        <h2 className="text-2xl font-bold text-blue-200 mb-3">Something went wrong</h2>
        <p className="text-blue-400 mb-6">
          {error.message || 'An unexpected error occurred. Please try again.'}
        </p>
        <button
          onClick={reset}
          className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-2 rounded-lg transition-colors"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
