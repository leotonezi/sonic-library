"use client";

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getBooks } from '@/services/bookService';
import { Search } from 'lucide-react';
import Book from '@/types/book';

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchBooks();
  }, []);
 
  const fetchBooks = async () => {
    const query = searchQuery.trim();
    const data = await getBooks(query ? `?title=${encodeURIComponent(query)}` : '');
    setBooks(data);
  };

  return (
    <main className="p-6 bg-[#0a1128] text-white min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <div className="relative flex">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search books..."
            className="pl-10 pr-4 py-2 rounded-md bg-blue-950 border border-blue-700 text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="button"
            onClick={fetchBooks}
            className="absolute left-1 top-1/2 -translate-y-1/2 p-1 cursor-pointer"
            aria-label="Search"
          >
            <Search className="text-blue-400 w-5 h-5" />
          </button>
        </div>

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