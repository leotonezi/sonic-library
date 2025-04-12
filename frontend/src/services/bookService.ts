import Book from "@/types/book";
import { apiFetch } from "@/utils/api";
import { notFound } from "next/navigation";

export async function getBooks(): Promise<Book[]> {
  const books = await apiFetch<Book[]>('/books');

  if (!books || books.length === 0) {
    notFound();
  }

  return books;
}