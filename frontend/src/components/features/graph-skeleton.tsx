import React from 'react';

export default function GraphSkeleton(): React.ReactElement {
  return (
    <div className="w-full">
      <div
        className="relative w-full animate-pulse rounded-xl border border-[#3F8EF3]"
        style={{ height: '70vh', minHeight: 400, background: '#0a1128' }}
      >
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-[#0e2050]" />
            <div className="h-3 w-48 rounded bg-[#0e2050]" />
          </div>
        </div>
        <div className="absolute bottom-4 left-4 flex flex-col gap-2">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-8 w-8 rounded bg-[#0e2050]" />
          ))}
        </div>
      </div>
    </div>
  );
}
