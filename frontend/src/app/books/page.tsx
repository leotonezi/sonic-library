import { notFound } from 'next/navigation';

interface Book {
  id: number;
  title: string;
  author: string;
  description?: string;
}

export const revalidate = 60

async function getBooks(): Promise<Book[]> {
  const res = await fetch('http://localhost:8000/books', {
    cache: 'force-cache',
  });
  

  if (!res.ok) {
    notFound();
  }

  const books = await res.json();

  if (!books || books.length === 0) {
    notFound();
  }

  return books;
}

export default async function BooksPage() {
  const books = await getBooks();

  return (
    <main className="p-6">
      <h1 className="text-3xl font-bold mb-4">Books</h1>
      <ul className="space-y-2">
        {books.map((book) => (
          <li key={book.id} className="border p-4 rounded">
            <h2 className="text-xl font-semibold">{book.title}</h2>
            <p className="text-sm text-gray-500">By {book.author}</p>
            {book.description && <p>{book.description}</p>}
          </li>
        ))}
      </ul>
    </main>
  );
}