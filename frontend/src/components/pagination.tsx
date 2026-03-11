"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, totalPages, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-center gap-2 mt-4">
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        className="p-2 rounded bg-blue-800 border border-blue-600 text-blue-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors"
      >
        <ChevronLeft size={16} />
      </button>
      <span className="text-sm text-blue-300 px-3">
        Page {page} of {totalPages}
      </span>
      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        className="p-2 rounded bg-blue-800 border border-blue-600 text-blue-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors"
      >
        <ChevronRight size={16} />
      </button>
    </div>
  );
}
