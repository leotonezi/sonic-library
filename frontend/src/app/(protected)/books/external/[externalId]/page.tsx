// app/(protected)/books/external/[externalId]/page.tsx

import { cookies } from 'next/headers';
import { redirect, notFound } from 'next/navigation';
import { ApiResponse } from '@/interfaces/auth';
import { serverSideApiFetch } from '@/utils/api';
import Image from 'next/image';
import ReviewsList from '../../[id]/review-list';
import UserBookActions from './user-book-actions';
import { ExternalBook, UserBook } from '@/interfaces/book';

export const dynamic = 'force-dynamic';

async function getExternalBookData(externalId: string, accessToken: string): Promise<ExternalBook> {
  try {
    const bookData = await serverSideApiFetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/books/external/${externalId}`,
      accessToken
    ) as ApiResponse<ExternalBook>;

    const book = bookData.data;

    if (!book || !book.external_id) {
      throw new Error('Invalid book data received');
    }

    return book;
  } catch (error) {
    console.error('Error fetching external book data:', error);
    throw error;
  }
}

async function getUserBookData(externalId: string, accessToken: string): Promise<UserBook | null> {
  try {
    const response = await serverSideApiFetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/user-books/book/external/${externalId}`,
      accessToken
    );

    if (!response) {
      return null;
    }

    if (response?.status === 404) {
      return null;
    }

    const res = await response.json();
    return res.data ?? null;
  } catch (error) {
    if (error instanceof Error && error.message?.includes('404')) {
      return null;
    }
    throw error;
  }
}

type Props = {
  params: Promise<{ externalId: string }>
}

export default async function ExternalBookPage({ params }: Props) {
  const { externalId } = await params;
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('access_token')?.value;

  if (!accessToken) {
    redirect('/login');
  }

  try {
    const book = await getExternalBookData(externalId, accessToken);
    
    if (!book) notFound();

    const userBook = await getUserBookData(externalId, accessToken);

    return (
      <main className="p-6 bg-blue-950 text-blue-50 min-h-screen flex flex-col items-center">
        <div className="relative bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-1">
              {book.thumbnail && (
                <Image
                  src={book.thumbnail}
                  alt={book.title}
                  width={80}
                  height={80}
                  className="w-full rounded-md shadow-md"
                />
              )}
            </div>

            <div className="md:col-span-2">
              <div className="flex justify-between items-start">
                <h1 className="text-3xl font-bold text-blue-500 mb-2">{book.title}</h1>
              </div>
              
              <p className="text-sm italic text-blue-100 mb-4">
                By {book.authors?.join(', ') || 'Unknown Author'}
              </p>
              
              {book.description && (
                <p className="text-blue-200 leading-relaxed mb-4">{book.description}</p>
              )}

              {/* Additional Info */}
              <div className="text-blue-200 space-y-2">
                <p>
                  <span className="font-semibold">Published:</span> {book.publishedDate}
                </p>
                <p>
                  <span className="font-semibold">Pages:</span> {book.pageCount}
                </p>
                <p>
                  <span className="font-semibold">Language:</span> {book.language}
                </p>
                {book.categories && book.categories.length > 0 && (
                  <p>
                    <span className="font-semibold">Categories:</span>{' '}
                    {book.categories.join(', ')}
                  </p>
                )}
              </div>

              <UserBookActions externalId={externalId} userBook={userBook} />
            </div>
          </div>

          <div className="mt-5">
            <ReviewsList/>
          </div>
        </div>
      </main>
    );
  } catch (error) {
    console.error('Error in ExternalBookPage:', error);
    return (
      <div className="p-6 bg-blue-950 text-red-400 min-h-screen flex items-center justify-center">
        <div className="bg-red-900/50 p-4 rounded-lg max-w-md text-center">
          <h2 className="text-xl font-semibold mb-2">Error Loading Book</h2>
          <p>We encountered an error while loading this book. Please try again later.</p>
        </div>
      </div>
    );
  }
}