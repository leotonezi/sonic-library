// app/(protected)/books/external/[externalId]/UserBookActions.tsx

'use client';

import { UserBook } from '@/interfaces/book';
import { apiPost } from '@/utils/api';
import { useState } from 'react';
import { toast } from 'sonner';

interface Props {
  externalId: string;
  userBook: UserBook | null;
}

export default function UserBookActions({ externalId, userBook }: Props) {
  const [status, setStatus] = useState<string | null>(userBook?.status || null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddToReadingList = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiPost('/user-books', {
        body: JSON.stringify({
          external_book_id: externalId,
          status: 'TO_READ',
        }),
      }) as Response;

      if (!response.ok) {
        throw new Error('Failed to add to reading list');
      }

      setStatus('TO_READ');
      toast.success('Added to Reading List!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      toast.error(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkAsRead = async () => {
    setIsLoading(true);
    setError(null);

    try {
      let method = 'POST';
      let url = '/user-books';
      let body = JSON.stringify({
        external_book_id: externalId,
        status: 'READ',
      });

      // If book is already in library, update instead of create
      if (status) {
        method = 'PUT';
        url = `/user-books/${userBook?.id}`;
        body = JSON.stringify({
          status: 'READ',
        });
      }

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: body,
      });

      if (!response.ok) {
        throw new Error('Failed to mark as read');
      }

      setStatus('READ');
      toast.success('Marked as Read!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      toast.error(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mt-6 space-x-4">
      {isLoading && <span className="text-gray-400">Loading...</span>}
      {error && <span className="text-red-500">{error}</span>}

      {!status && (
        <button
          className="bg-blue-500 cursor-pointer hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition"
          onClick={handleAddToReadingList}
          disabled={isLoading}
        >
          Add to Reading List
        </button>
      )}

      <button
        className="bg-green-500 cursor-pointer hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition"
        onClick={handleMarkAsRead}
        disabled={isLoading}
      >
        Mark as Read
      </button>
    </div>
  );
}