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
