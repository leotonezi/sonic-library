// app/library/[user_id]/page.tsx

import { ApiResponse } from "@/interfaces/auth";
import { UserBook } from "@/interfaces/book";
import { serverSideApiFetch } from "@/utils/api";
import { Metadata } from "next";
import { cookies } from "next/headers";
import Image from "next/image";

export const metadata: Metadata = {
  title: "My Library",
  description: "Your personal book library",
};

const statusLabels: Record<string, string> = {
  TO_READ: "To Read",
  READING: "Reading",
  READ: "Read",
};

async function getMyBooks(
  accessToken: string,
): Promise<ApiResponse<UserBook[]> | null> {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  if (!backendUrl) throw new Error("NEXT_PUBLIC_BACKEND_URL is not set");

  const response = await serverSideApiFetch(
    `${backendUrl}/user-books/my-books`,
    accessToken,
    {
      next: { revalidate: 0 },
    },
  );

  return response;
}

export default async function LibraryPage() {
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
    const data = await getMyBooks(accessToken);
    console.log(data);
    if (data && data.data) {
      userBooks = data.data; // data.data is UserBook[]
    }
  } catch (error) {
    console.error("Failed to fetch user books:", error);
  }
  function truncate(text: string, maxLength: number) {
    if (!text) return "";
    return text.length > maxLength ? text.slice(0, maxLength) + "…" : text;
  }

  return (
    <main className="p-6 bg-blue-950 text-blue-50 min-h-screen max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-blue-500 mb-6 text-center">
        My Library
      </h1>

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
                  <h2 className="text-2xl font-bold text-blue-400 mb-1">
                    {book?.title || "No Title"}
                  </h2>
                  <p className="text-sm italic text-blue-300 mb-2">
                    By {book?.author || "N/A"}
                  </p>
                  <p className="text-sm text-blue-300 mb-2">
                    Genres: {book?.genres?.join(", ") || "N/A"}
                  </p>
                  <p className="text-sm text-blue-200 leading-relaxed whitespace-pre-line flex-grow">
                    {truncate(book?.description || "", 300)}
                  </p>
                  <p className="mt-4 text-blue-400 italic text-sm">
                    {statusLabels[userBook.status] || userBook.status}
                  </p>
                </div>
              </article>
            );
          })
        )}
      </section>
    </main>
  );
}
