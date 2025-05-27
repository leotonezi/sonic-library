// app/(protected)/books/external/[externalId]/UserBookActions.tsx

"use client";

import { ExternalBook, UserBook } from "@/interfaces/book";
import { apiPost, apiPut } from "@/utils/api";
import { mapGoogleBookToBookCreate } from "@/utils/book";
import { useState } from "react";
import { toast } from "sonner";

interface Props {
  externalId: string;
  userBook: UserBook | null;
  book: ExternalBook | null;
}

export default function UserBookActions({ externalId, userBook, book }: Props) {
  const [status, setStatus] = useState<string | null>(userBook?.status || null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddToReadingList = async () => {
    setIsLoading(true);
    setError(null);

    if (!book) {
      return;
    }

    try {
      const data = await apiPost<UserBook>("/user-books", {
        external_book_id: externalId,
        status: "TO_READ",
        book: mapGoogleBookToBookCreate(book),
      });

      if (!data) {
        throw new Error("Failed to add to reading list");
      }

      setStatus("TO_READ");
      toast.success("Added to Reading List!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      toast.error(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkAsRead = async () => {
    setIsLoading(true);
    setError(null);

    if (!book) {
      return;
    }

    try {
      let data: UserBook | null;

      if (!status) {
        data = await apiPost<UserBook>("/user-books", {
          external_book_id: externalId,
          status: "READ",
          book: mapGoogleBookToBookCreate(book),
        });
      } else {
        data = await apiPut<UserBook>(`/user-books/${userBook?.id}`, {
          status: "READ",
        });
      }

      if (!data) {
        throw new Error("Failed to mark as read");
      }

      setStatus("READ");
      toast.success("Marked as Read!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      toast.error(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkAsReading = async () => {
    setIsLoading(true);
    setError(null);

    if (!book) {
      return;
    }

    try {
      let data: UserBook | null;

      if (!status) {
        data = await apiPost<UserBook>("/user-books", {
          external_book_id: externalId,
          status: "READING",
          book: mapGoogleBookToBookCreate(book),
        });
      } else {
        data = await apiPut<UserBook>(`/user-books/${userBook?.id}`, {
          status: "READING",
        });
      }

      if (!data) {
        throw new Error("Failed to mark as reading");
      }

      setStatus("READING");
      toast.success("Marked as Reading!");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      toast.error(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  let statusMessage = "";
  if (status === "READ") {
    statusMessage = "Read";
  } else if (status === "READING") {
    statusMessage = "Reading";
  } else if (status === "TO_READ") {
    statusMessage = "To Read";
  }

  return (
    <div className="mt-6 space-x-4">
      {isLoading && <span className="text-gray-400">Loading...</span>}
      {error && <span className="text-red-500">{error}</span>}

      {statusMessage && <span className="text-gray-400">{statusMessage}</span>}

      {!status && (
        <button
          className="bg-blue-500 cursor-pointer hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition"
          onClick={handleAddToReadingList}
          disabled={isLoading}
        >
          Add to Reading List
        </button>
      )}

      {(status === "TO_READ" || status === "READING") && (
        <button
          className="bg-green-500 cursor-pointer hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition"
          onClick={handleMarkAsRead}
          disabled={isLoading}
        >
          Mark as Read
        </button>
      )}

      {status === "TO_READ" && (
        <button
          className="bg-yellow-500 cursor-pointer hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded transition"
          onClick={handleMarkAsReading}
          disabled={isLoading}
        >
          Mark as Reading
        </button>
      )}
    </div>
  );
}
