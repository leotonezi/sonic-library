import { useState, useEffect, useCallback } from 'react';
import { Book, PaginatedResponse, BookSearchParams } from '@/types';
import { apiClient } from '@/lib/api-client';

export const useBooks = (params: BookSearchParams = {}) => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState<PaginatedResponse<Book>['pagination'] | null>(null);

  const fetchBooks = useCallback(async (searchParams: BookSearchParams = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const queryParams = new URLSearchParams();
      
      if (searchParams.q) queryParams.append('q', searchParams.q);
      if (searchParams.page) queryParams.append('page', searchParams.page.toString());
      if (searchParams.page_size) queryParams.append('page_size', searchParams.page_size.toString());
      if (searchParams.author) queryParams.append('author', searchParams.author);
      if (searchParams.genre) queryParams.append('genre', searchParams.genre);
      if (searchParams.language) queryParams.append('language', searchParams.language);

      const response = await apiClient.get<PaginatedResponse<Book>>(
        `/books?${queryParams.toString()}`
      );
      
      if (response) {
        setBooks(response.data);
        setPagination(response.pagination);
      }
    } catch (err) {
      setError('Failed to fetch books');
      console.error('Error fetching books:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBooks(params);
  }, [fetchBooks, params]);

  return {
    books,
    loading,
    error,
    pagination,
    refetch: fetchBooks,
  };
};