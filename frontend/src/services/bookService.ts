import { Book } from "@/types/book";
import { apiFetch } from "@/utils/api";
import { notFound } from "next/navigation";

export async function getBooks(p0: string): Promise<Book[]> {
  const books = await apiFetch<Book[]>(`/books${p0}`);

  if (!books || books.length === 0) {
    notFound();
  }

  return books;
}