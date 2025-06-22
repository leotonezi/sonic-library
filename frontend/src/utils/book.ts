import { Book, ExternalBook } from "@/interfaces/book";

export function mapGoogleBookToBookCreate(googleBook: ExternalBook): Book {
  const parsedId = googleBook.external_id
    ? Number(googleBook.external_id)
    : null;
  const id = parsedId && !isNaN(parsedId) ? parsedId : null;

  return {
    id,
    external_id: googleBook.external_id || null,
    title: googleBook.title,
    author: googleBook.authors ? googleBook.authors.join(", ") : "", // join authors array
    description: googleBook.description,
    page_count: googleBook.pageCount,
    published_date: googleBook.publishedDate,
    publisher: googleBook.publisher,
    isbn: googleBook.isbn || undefined,
    image_url: googleBook.thumbnail,
    language: googleBook.language,
    genres:
      googleBook.categories && googleBook.categories.length > 0
        ? googleBook.categories
        : [],
  };
}

export function convertExternalBookToBook(externalBook: ExternalBook): Book {
  return {
    id: null,
    external_id: externalBook.external_id,
    title: externalBook.title,
    author: externalBook.authors ? externalBook.authors.join(", ") : "", // join authors array to string
    description: externalBook.description ?? null,
    page_count: externalBook.pageCount ?? null,
    published_date: externalBook.publishedDate ?? null,
    publisher: externalBook.publisher ?? null,
    isbn: externalBook.isbn ?? null,
    image_url: externalBook.thumbnail ?? null,
    language: externalBook.language ?? null,
    genres: externalBook.categories ?? null,
  };
}

export function convertBookToExternalBook(book: Book): ExternalBook {
  if (!book.external_id) {
    throw new Error("Book.external_id is required to convert to ExternalBook");
  }

  return {
    external_id: book.external_id,
    title: book.title,
    authors: book.author
      ? book.author.split(",").map((a) => a.trim())
      : undefined,
    publishedDate: book.published_date ?? undefined,
    description: book.description ?? undefined,
    thumbnail: book.image_url ?? undefined,
    pageCount: book.page_count ?? undefined,
    categories: book.genres ?? undefined,
    language: book.language ?? undefined,
    publisher: book.publisher ?? undefined,
    isbn: book.isbn ?? undefined,
  };
}
