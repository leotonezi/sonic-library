import { cookies } from 'next/headers';
import { redirect, notFound } from 'next/navigation';
import { Star } from 'lucide-react';
import AddReviewForm from './add-review-form';
import ReviewsList from './review-list';
import { Book, BookWithRating } from '@/types/book';
import Review from '@/types/review';
import { ApiResponse } from '@/types/auth';
import { serverSideApiFetch } from '@/utils/api';

export const dynamic = 'force-dynamic';

async function getBookData(bookId: string, accessToken: string): Promise<{
  book: BookWithRating;
  reviews: Review[];
}> {
  try {
    const [bookData, reviewsData] = await Promise.all([
      serverSideApiFetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/books/${bookId}`,
        accessToken
      ),
      serverSideApiFetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/reviews/book/${bookId}`,
        accessToken,
        {
          next: { revalidate: 60 },
        }
      ),
    ]) as [ApiResponse<Book>, ApiResponse<Review[]>];

    const book = bookData.data;
    const reviews = reviewsData.data ?? [];

    console.log(book, reviews)

    if (!book || !book.id) {
      throw new Error('Invalid book data received');
    }

    const averageRating = reviews.length > 0
      ? (reviews.reduce((sum, r) => sum + r.rate, 0) / reviews.length).toFixed(1)
      : null;

    return {
      book: { ...book, averageRating },
      reviews,
    };
  } catch (error) {
    console.error('Error fetching book data:', error);
    throw error;
  }
}

export default async function BookPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('access_token')?.value;

  if (!accessToken) {
    redirect('/login');
  }

  if (!id || isNaN(Number(id))) {
    notFound();
  }

  try {
    const { book, reviews } = await getBookData(id, accessToken);
    
    if (!book) {
      notFound();
    }

    return (
      <main className="p-6 bg-blue-950 text-blue-50 min-h-screen flex flex-col items-center">
        <div className="relative bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full mb-6">
          <div className="flex justify-between items-start">
            <h1 className="text-3xl font-bold text-blue-500 mb-2">{book.title}</h1>
            {book.averageRating && (
              <div className="flex items-center text-yellow-400 text-2xl ml-4">
                {book.averageRating}
                <Star className="ml-1" size={24} />
              </div>
            )}
          </div>
          <p className="text-sm italic text-blue-100 mb-4">By {book.author}</p>
          {book.description && (
            <p className="text-blue-200 leading-relaxed">{book.description}</p>
          )}
        </div>

        <AddReviewForm bookId={book.id} />
        <ReviewsList reviews={reviews || []}/>
      </main>
    );
  } catch (error) {
    console.error('Error in BookPage:', error);
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

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return {
    title: `Book ${id}`,
  };
}