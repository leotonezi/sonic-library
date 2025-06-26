// app/library/[user_id]/page.tsx

import UserBookActions from "@/components/user-book-actions";
import { ApiResponse } from "@/interfaces/auth";
import { UserBook } from "@/interfaces/book";
import { serverSideApiFetch } from "@/utils/api";
import { convertBookToExternalBook } from "@/utils/book";
import { Metadata } from "next";
import { cookies } from "next/headers";
import Image from "next/image";
import Link from "next/link";

export const metadata: Metadata = {
  title: "My Library",
  description: "Your personal book library",
};

async function getMyBooks(
  accessToken: string,
  status?: string,
): Promise<ApiResponse<UserBook[]> | null> {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!backendUrl) throw new Error("NEXT_PUBLIC_BACKEND_URL is not set");

  const url = new URL(`${backendUrl}/user-books/my-books`);
  if (status) {
    url.searchParams.append("status", status);
  }

  const response = await serverSideApiFetch(url.toString(), accessToken, {
    next: { revalidate: 0 },
  });

  return response;
}

export default async function LibraryPage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string }>;
}) {
  const resolvedSearchParams = await searchParams;
  const statusFilter = resolvedSearchParams.status;
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value;

  if (!accessToken) {
    return (
      <main className="max-w-4xl mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6">My Library</h1>
        <p>You must be logged in to view your library.</p>
      </main>
    );
  }

  let userBooks: UserBook[] = [];

  try {
    const data = await getMyBooks(accessToken, statusFilter);
    if (data && data.data) {
      userBooks = data.data;
    }
  } catch (error) {
    console.error("Failed to fetch user books:", error);
  }

  function truncate(text: string, maxLength: number) {
    if (!text) return "";
    return text.length > maxLength ? text.slice(0, maxLength) + "…" : text;
  }

  const filterOptions = [
    { value: "TO_READ", label: "To Read" },
    { value: "READ", label: "Read" },
    { value: "READING", label: "Reading" },
  ];

  return (
    <main className="p-6 bg-blue-950 text-blue-50 min-h-screen max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-blue-500 mb-6 text-center">
        My Library
      </h1>

      <section className="mb-6 flex justify-center gap-4">
        {filterOptions.map(({ value, label }) => (
          <a
            key={value}
            href={`?status=${value}`}
            className={`px-4 py-2 rounded cursor-pointer ${
              statusFilter === value
                ? "bg-blue-700 text-white"
                : "bg-blue-800 text-blue-300 hover:bg-blue-700"
            }`}
          >
            {label}
          </a>
        ))}
        <a
          href="/library"
          className={`px-4 py-2 rounded cursor-pointer ${
            !statusFilter
              ? "bg-blue-700 text-white"
              : "bg-blue-800 text-blue-300 hover:bg-blue-700"
          }`}
        >
          All
        </a>
      </section>

      <section className="space-y-6">
        {userBooks.length === 0 ? (
          <p>No books found.</p>
        ) : (
          userBooks.map((userBook) => {
            const book = userBook.book;
            return (
              <article
                key={userBook.id}
                className="relative bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md flex gap-6"
              >
                {book?.image_url ? (
                  <div className="relative w-24 h-36 flex-shrink-0 rounded overflow-hidden border border-blue-700">
                    <Image
                      src={book.image_url}
                      alt={`Cover of ${book.title}`}
                      fill
                      style={{ objectFit: "cover" }}
                      sizes="96px 144px"
                      priority={false}
                    />
                  </div>
                ) : (
                  <div className="w-24 h-36 bg-blue-800 rounded flex items-center justify-center text-blue-400 text-xs flex-shrink-0 border border-blue-700">
                    No Image
                  </div>
                )}

                <div className="flex-1 flex flex-col">
                  <Link
                    href={`/books/external/${userBook?.external_book_id}`}
                    passHref
                  >
                    <h2 className="text-2xl font-bold text-blue-400 mb-1 hover:text-blue-300 transition-colors cursor-pointer">
                      {book?.title || "No Title"}
                    </h2>
                  </Link>
                  <p className="text-sm italic text-blue-300 mb-2">
                    By {book?.author || "N/A"}
                  </p>
                  <p className="text-sm text-blue-300 mb-2">
                    Genres: {book?.genres?.join(", ") || "N/A"}
                  </p>
                  <p className="text-sm text-blue-200 leading-relaxed whitespace-pre-line flex-grow">
                    {truncate(book?.description || "", 300)}
                  </p>
                  <UserBookActions
                    externalId={userBook.external_book_id || ""}
                    userBook={userBook}
                    book={book ? convertBookToExternalBook(book) : null}
                  />
                </div>
              </article>
            );
          })
        )}
      </section>
    </main>
  );
}
