"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { PaginationMetadata } from "@/interfaces/book";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface LibraryPaginationProps {
  pagination: PaginationMetadata;
  statusFilter?: string;
}

export default function LibraryPagination({ 
  pagination, 
  statusFilter 
}: LibraryPaginationProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { current_page, total_pages, has_previous, has_next, total_count } = pagination;

  if (total_pages <= 1) return null;

  const handlePageChange = (page: number) => {
    if (page === current_page) return;
    
    const params = new URLSearchParams(searchParams);
    params.set("page", page.toString());
    
    if (statusFilter) {
      params.set("status", statusFilter);
    }
    
    router.push(`/library?${params.toString()}`);
  };

  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;
    
    let start = Math.max(1, current_page - Math.floor(maxVisible / 2));
    const end = Math.min(total_pages, start + maxVisible - 1);
    
    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }
    
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    
    return pages;
  };

  return (
    <div className="flex items-center justify-between bg-blue-900 border border-blue-600 rounded-lg p-4 mt-6">
      <div className="text-sm text-blue-300">
        Showing {pagination.start_index + 1} to {pagination.end_index} of {total_count} books
      </div>
      
      <div className="flex items-center space-x-2">
        <button
          onClick={() => handlePageChange(current_page - 1)}
          disabled={!has_previous}
          className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
            has_previous
              ? 'bg-blue-800 text-blue-200 hover:bg-blue-700'
              : 'bg-blue-800/50 text-blue-400 cursor-not-allowed'
          }`}
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          Previous
        </button>
        
        <div className="flex space-x-1">
          {getPageNumbers().map((page) => (
            <button
              key={page}
              onClick={() => handlePageChange(page)}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                page === current_page
                  ? 'bg-blue-600 text-white'
                  : 'bg-blue-800 text-blue-200 hover:bg-blue-700'
              }`}
            >
              {page}
            </button>
          ))}
        </div>
        
        <button
          onClick={() => handlePageChange(current_page + 1)}
          disabled={!has_next}
          className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
            has_next
              ? 'bg-blue-800 text-blue-200 hover:bg-blue-700'
              : 'bg-blue-800/50 text-blue-400 cursor-not-allowed'
          }`}
        >
          Next
          <ChevronRight className="w-4 h-4 ml-1" />
        </button>
      </div>
    </div>
  );
}