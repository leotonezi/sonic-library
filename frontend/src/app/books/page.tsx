import Link from 'next/link';
import { getBooks } from '@/services/bookService';

export const revalidate = 60;

export default async function BooksPage() {
  const books = await getBooks();

  return (
    <main className="p-6 bg-[#0a1128] text-[#e0f0ff] min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-[#00aaff]">Books</h1>
      <ul className="space-y-4">
        {books.map((book) => (
          <li
            key={book.id}
            className="bg-[#001f3f] border border-[#0077cc] p-4 rounded-lg shadow-md transition duration-300 hover:shadow-xl hover:bg-[#003366]"
          >
            <Link href={`/books/${book.id}`}>
              <h2 className="text-xl font-semibold text-[#00aaff] hover:underline">
                {book.title}
              </h2>
            </Link>
            <p className="text-sm italic text-[#66ccff]">By {book.author}</p>
            {book.description && (
              <p className="mt-2 text-[#cceeff]">{book.description}</p>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}