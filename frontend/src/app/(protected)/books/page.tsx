// components/BooksPage.tsx
"use client";

import Link from "next/link";
import Image from "next/image";
import { useSearchBookStore } from "@/store/useSearchBookStore";
import { Book } from "lucide-react";

export default function BooksPage() {
  const searchResults = useSearchBookStore((state) => state.searchResults);

  return (
    <main className="p-6 bg-[#0a1128] text-white min-h-screen">
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
          <NoResultsState />
        )}
      </ul>
    </main>
  );
}

function NoResultsState() {
  const fetchExternalBooks = useSearchBookStore(
    (state) => state.fetchExternalBooks,
  );

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4">
      <div className="mb-6">
        <Book className="w-24 h-24 text-blue-400 opacity-50" />
      </div>

      <h3 className="text-2xl font-semibold text-white mb-2">No books found</h3>

      <p className="text-blue-200 text-center mb-8 max-w-md">
        Start building your digital library by adding your first book or try
        searching for something else.
      </p>

      <div className="flex flex-col sm:flex-row gap-4">
        <button
          onClick={() => {
            console.log("Browse popular books");
          }}
          className="px-6 py-3 border border-blue-500 text-blue-400 rounded-lg font-medium hover:bg-blue-500 hover:text-white transition-colors"
        >
          Browse Popular Books
        </button>
      </div>

      <div className="mt-8 text-center">
        <p className="text-sm text-blue-300 mb-2">Try searching for:</p>
        <div className="flex flex-wrap justify-center gap-2">
          {["Fiction", "Science", "History", "Biography"].map((suggestion) => (
            <button
              key={suggestion}
              className="px-3 py-1 text-xs bg-blue-800 text-blue-200 cursor-pointer rounded-full hover:bg-blue-700 transition-colors"
              onClick={() => {
                fetchExternalBooks(suggestion); // Call fetchExternalBooks with the suggestion
              }}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
