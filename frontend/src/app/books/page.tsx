import Link from 'next/link';
import { getBooks } from '@/services/bookService';

export const revalidate = 60;

export default async function BooksPage() {
  const books = await getBooks();

  return (
    <main className="p-6 bg-[#0a1128] text-white min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-blue-500">Books</h1>
        <Link href="/books/new" className="btn-primary">
          Add New Book
        </Link>
      </div>
      <ul className="space-y-4">
        {books.map((book) => (
          <li
            key={book.id}
            className="bg-blue-900 border border-blue-600 p-4 rounded-lg shadow-md transition duration-300 hover:shadow-xl hover:bg-blue-800"
          >
            <Link href={`/books/${book.id}`}>
              <h2 className="text-xl font-semibold text-blue-500 hover:underline">
                {book.title}
              </h2>
            </Link>
            <p className="text-sm italic text-white">By {book.author}</p>
            {book.description && (
              <p className="mt-2 text-blue-100">{book.description}</p>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}