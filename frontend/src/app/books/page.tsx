'use client';

import { useEffect, useState } from 'react';

type Book = {
  id: number;
  title: string;
  author: string;
  description?: string;
};

export default function Books() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/books')
      .then((res) => res.json())
      .then((data) => {
        console.log(data)
        setBooks(data);
        setLoading(false);
      });
  }, []);

  return (
    <main className="p-6">
      <h1 className="text-3xl font-bold mb-4">Books</h1>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul className="space-y-2">
          {books.map((book) => (
            <li key={book.id} className="border p-4 rounded">
              <h2 className="text-xl font-semibold">{book.title}</h2>
              <p className="text-sm text-gray-500">By {book.author}</p>
              {book.description && <p>{book.description}</p>}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}