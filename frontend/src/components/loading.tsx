// components/LoadingScreen.tsx
export default function LoadingScreen() {
  return (
    <div className="min-h-screen bg-blue-950 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-200 mx-auto"></div>
        <p className="mt-4 text-blue-200">Loading...</p>
      </div>
    </div>
  );
}