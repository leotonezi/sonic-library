export default function ReviewsSkeleton() {
  return (
    <div className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full">
      <h2 className="text-2xl font-semibold text-blue-500 mb-4">Reviews</h2>
      <ul className="space-y-4">
        {[0, 1, 2].map((i) => (
          <li key={i} className="bg-blue-800 p-4 rounded shadow">
            {/* Avatar + name row */}
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded-full bg-blue-700 animate-pulse" />
              <div className="h-3 w-28 bg-blue-700 rounded animate-pulse" />
            </div>
            {/* Review text lines */}
            <div className="h-3 w-full bg-blue-700 rounded animate-pulse mb-2" />
            <div className="h-3 w-4/5 bg-blue-700 rounded animate-pulse mb-3" />
            {/* Star row */}
            <div className="flex gap-1">
              {[0, 1, 2, 3, 4].map((s) => (
                <div
                  key={s}
                  className="w-4 h-4 bg-blue-700 rounded animate-pulse"
                />
              ))}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
