import { Book, ExternalBook, PaginatedResponse } from "@/interfaces/book";
import { apiFetch } from "@/utils/api";
import { notFound } from "next/navigation";

export async function getBooks(p0: string): Promise<Book[]> {
  const books = await apiFetch<Book[]>(`/books${p0}`);

  if (!books || books.length === 0) {
    notFound();
  }

  return books;
}

export async function getBooksPaginated(
  page: number = 1,
  pageSize: number = 10,
  search?: string,
  genre?: string
): Promise<PaginatedResponse<Book> | null> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });
  
  if (search) params.append('search', search);
  if (genre) params.append('genre', genre);

  const response = await apiFetch<PaginatedResponse<Book>>(`/books/?${params.toString()}`);
  return response;
}

export const searchExternalBooks = async (
  query: string,
  page: number = 1,
  maxResults: number = 10
): Promise<PaginatedResponse<ExternalBook> | null> => {
  try {
    const params = new URLSearchParams({
      q: query,
      page: page.toString(),
      max_results: maxResults.toString(),
    });
    
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/books/search-external?${params.toString()}`);
    if (!response.ok) throw new Error('Failed to fetch external books');
    const data = await response.json();
    return data as PaginatedResponse<ExternalBook>;
  } catch (error) {
    console.error('Error searching external books:', error);
    throw error;
  }
};

export const getPopularBooks = async (
  page: number = 1,
  maxResults: number = 12
): Promise<PaginatedResponse<ExternalBook> | null> => {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      max_results: maxResults.toString(),
    });
    
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/books/popular?${params.toString()}`);
    if (!response.ok) throw new Error('Failed to fetch popular books');
    const data = await response.json();
    return data as PaginatedResponse<ExternalBook>;
  } catch (error) {
    console.error('Error fetching popular books:', error);
    throw error;
  }
};

export const getUserBooksPaginated = async (
  page: number = 1,
  pageSize: number = 10,
  status?: string
): Promise<PaginatedResponse<import("@/interfaces/book").UserBook> | null> => {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });
  
  if (status) params.append('status', status);

  const response = await apiFetch<PaginatedResponse<import("@/interfaces/book").UserBook>>(`/user-books/my-books/paginated?${params.toString()}`);
  return response;
};

// Legacy functions for backward compatibility
export const searchExternalBooksLegacy = async (query: string): Promise<ExternalBook[]> => {
  const response = await searchExternalBooks(query, 1, 20);
  return response?.data || [];
};

export const getPopularBooksLegacy = async (): Promise<ExternalBook[]> => {
  const response = await getPopularBooks(1, 20);
  return response?.data || [];
};