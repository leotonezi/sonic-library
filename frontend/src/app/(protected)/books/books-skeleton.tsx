export default function BooksSkeleton() {
  return (
    <>
      <div className="h-7 w-48 bg-blue-700 rounded animate-pulse mb-6" />
      <ul className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <li
            key={i}
            className="bg-blue-900 border border-blue-600 p-4 rounded-lg shadow-md"
          >
            <div className="flex">
              <div className="w-24 h-32 bg-blue-700 rounded mr-4 shrink-0 animate-pulse" />
              <div className="flex-1">
                <div className="h-5 w-3/4 bg-blue-700 rounded animate-pulse" />
                <div className="h-3 w-1/2 bg-blue-700 rounded animate-pulse mt-2" />
                <div className="mt-2">
                  <div className="h-3 w-full bg-blue-700 rounded animate-pulse mb-2" />
                  <div className="h-3 w-full bg-blue-700 rounded animate-pulse mb-2" />
                  <div className="h-3 w-4/5 bg-blue-700 rounded animate-pulse" />
                </div>
                <div className="mt-2 flex gap-2">
                  <div className="h-3 w-16 bg-blue-700 rounded animate-pulse" />
                  <div className="h-3 w-24 bg-blue-700 rounded animate-pulse" />
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </>
  );
}
