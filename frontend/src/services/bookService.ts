import { Book, ExternalBook } from "@/interfaces/book";
import { apiFetch } from "@/utils/api";
import { notFound } from "next/navigation";

export async function getBooks(p0: string): Promise<Book[]> {
  const books = await apiFetch<Book[]>(`/books${p0}`);

  if (!books || books.length === 0) {
    notFound();
  }

  return books;
}

export const searchExternalBooks = async (query: string): Promise<ExternalBook[]> => {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/books/search-external?q=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error('Failed to fetch external books');
    const data = await response.json();
    return data.data as ExternalBook[];
  } catch (error) {
    console.error('Error searching external books:', error);
    throw error;
  }
};