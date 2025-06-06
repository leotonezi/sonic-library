// components/BooksPage.tsx
"use client";

import Link from "next/link";
import Image from "next/image";
import { useSearchBookStore } from "@/store/useSearchBookStore";

export default function BooksPage() {
  const searchResults = useSearchBookStore((state) => state.searchResults);

  return (
    <main className="p-6 bg-[#0a1128] text-white min-h-screen">
      <div className="flex justify-end items-center mb-6">
        <Link href="/books/new" className="btn-primary">
          Add New Book
        </Link>
      </div>

      <ul className="space-y-4">
        {searchResults && searchResults.length > 0 ? (
          searchResults.map((book) => (
            <li
              key={book.external_id}
              className="bg-blue-900 border border-blue-600 p-4 rounded-lg shadow-md transition duration-300 hover:shadow-xl hover:bg-blue-800"
            >
              <Link
                href={`/books/external/${book.external_id}`}
                className="block"
              >
                <div className="flex">
                  {book.thumbnail && (
                    <Image
                      src={book?.thumbnail}
                      alt={book.title}
                      width={80}
                      height={80}
                      className="w-24 h-32 object-cover rounded mr-4"
                    />
                  )}
                  <div>
                    <h2 className="text-xl font-semibold text-blue-500 hover:underline">
                      {book.title}
                    </h2>
                    <p className="text-sm italic text-white">
                      By {book.authors?.join(", ")}
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
                          • {book.categories.join(", ")}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </Link>
            </li>
          ))
        ) : (
          <li>No results found.</li>
        )}
      </ul>
    </main>
  );
}
