"use client";

import Link from 'next/link';
import { useEffect, useState, useCallback } from 'react';
import { getBooks, searchExternalBooks } from '@/services/bookService';
import { Search } from 'lucide-react';
import { Book, ExternalBook } from '@/types/book';
import { BOOK_GENRES } from '@/utils/enums';

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [externalBooks, setExternalBooks] = useState<ExternalBook[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [isSearchingExternal, setIsSearchingExternal] = useState(false);

  const fetchBooks = useCallback(async () => {
    const query = new URLSearchParams();
    if (searchQuery.trim()) query.append('search', searchQuery.trim());
    if (selectedGenre) query.append('genre', selectedGenre);
    const data = await getBooks(`?${query.toString()}`);
    setBooks(data);
  }, [searchQuery, selectedGenre]);

  const fetchExternalBooks = useCallback(async () => {
    if (!searchQuery.trim()) return;
    try {
      const data = await searchExternalBooks(searchQuery);
      setExternalBooks(data);
    } catch (error) {
      console.error('Error fetching external books:', error);
    }
  }, [searchQuery]);

  useEffect(() => {
    if (books.length === 0) {
      fetchBooks();
    }
  }, [books, fetchBooks]);

  const handleSearch = async () => {
    if (isSearchingExternal) {
      await fetchExternalBooks();
    } else {
      await fetchBooks();
    }
  };

  return (
    <main className="p-6 bg-[#0a1128] text-white min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <div className="relative flex">
          <select
            value={selectedGenre}
            onChange={(e) => setSelectedGenre(e.target.value)}
            className="mr-2 px-2 py-2 rounded-md bg-blue-950 border border-blue-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isSearchingExternal}
          >
            <option value="">All Genres</option>
            {BOOK_GENRES.map((bk) => (
              <option key={bk.value} value={bk.value}>
                {bk.label}
              </option>
            ))}
          </select>

          <div className="flex items-center bg-blue-950 border border-blue-700 rounded-md">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search books..."
              className="pl-2 pr-2 py-2 w-64 rounded-md bg-transparent text-white placeholder-blue-300 focus:outline-none"
            />
            <button
              onClick={() => setIsSearchingExternal(!isSearchingExternal)}
              className={`px-3 py-1 text-sm ${
                isSearchingExternal ? 'text-orange-300' : 'text-blue-300'
              }`}
            >
              {isSearchingExternal ? 'Google Books' : 'Local'}
            </button>
            <Search
              size={24}
              className="text-white hover:text-orange-300 transition duration-300 cursor-pointer my-2 mx-2"
              onClick={handleSearch}
            />
          </div>
        </div>

        <Link href="/books/new" className="btn-primary">
          Add New Book
        </Link>
      </div>

      <ul className="space-y-4">
        {isSearchingExternal
          ? externalBooks.map((book) => (
              <li
                key={book.external_id}
                className="bg-blue-900 border border-blue-600 p-4 rounded-lg shadow-md transition duration-300 hover:shadow-xl hover:bg-blue-800"
              >
                <div className="flex">
                  {book.thumbnail && (
                    <img
                      src={book.thumbnail}
                      alt={book.title}
                      className="w-24 h-32 object-cover rounded mr-4"
                    />
                  )}
                  <div>
                    <h2 className="text-xl font-semibold text-blue-500">
                      {book.title}
                    </h2>
                    <p className="text-sm italic text-white">
                      By {book.authors?.join(', ')}
                    </p>
                    {book.description && (
                      <p className="mt-2 text-blue-100 line-clamp-3">
                        {book.description}
                      </p>
                    )}
                    <div className="mt-2 text-sm text-blue-300">
                      <span>{book.pageCount} pages</span>
                      {book.categories && (
                        <span className="ml-2">
                          • {book.categories.join(', ')}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </li>
            ))
          : books.map((book) => (
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