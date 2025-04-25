"use client";

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getBooks } from '@/services/bookService';
import { Search } from 'lucide-react';
import Book from '@/types/book';
import { BOOK_GENRES } from '@/utils/enums';

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');

  useEffect(() => {
    if(books.length === 0)
    fetchBooks();
  }, [books]);
 
  const fetchBooks = async () => {
    const query = new URLSearchParams();
    if (searchQuery.trim()) query.append('search', searchQuery.trim());
    if (selectedGenre) query.append('genre', selectedGenre);
    const data = await getBooks(`?${query.toString()}`);
    setBooks(data);
  };

  return (
    <main className="p-6 bg-[#0a1128] text-white min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <div className="relative flex">
          <select
            value={selectedGenre}
            onChange={(e) => setSelectedGenre(e.target.value)}
            className="mr-2 px-2 py-2 rounded-md bg-blue-950 border border-blue-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {BOOK_GENRES.map((bk) => (
              <option key={bk.value} value={bk.value}>
                {bk.label}
              </option>
            ))}
          </select>

          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Author or Title..."
            className="pl-2 pr-2 py-2 w-2xs rounded-md bg-blue-950 border border-blue-700 text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />          
            <Search size={24} className="text-white hover:text-orange-300 transition duration-300 cursor-pointer my-2 mx-2" onClick={fetchBooks}
            />
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