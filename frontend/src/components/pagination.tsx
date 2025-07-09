import { PaginationMetadata } from "@/interfaces/book";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  pagination: PaginationMetadata;
  onPageChange: (page: number) => void;
  loading?: boolean;
}

export default function Pagination({ 
  pagination, 
  onPageChange, 
  loading = false 
}: PaginationProps) {
  const { current_page, total_pages, has_previous, has_next, total_count } = pagination;

  if (total_pages <= 1) return null;

  const handlePageChange = (page: number) => {
    if (loading || page === current_page) return;
    onPageChange(page);
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
        Showing {pagination.start_index + 1} to {pagination.end_index} of {total_count} results
      </div>
      
      <div className="flex items-center space-x-2">
        <button
          onClick={() => handlePageChange(current_page - 1)}
          disabled={!has_previous || loading}
          className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
            has_previous && !loading
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
              disabled={loading}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                page === current_page
                  ? 'bg-blue-600 text-white'
                  : loading
                  ? 'bg-blue-800/50 text-blue-400 cursor-not-allowed'
                  : 'bg-blue-800 text-blue-200 hover:bg-blue-700'
              }`}
            >
              {page}
            </button>
          ))}
        </div>
        
        <button
          onClick={() => handlePageChange(current_page + 1)}
          disabled={!has_next || loading}
          className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
            has_next && !loading
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