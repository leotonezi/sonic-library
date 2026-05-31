// app/(protected)/books/external/[externalId]/page.tsx

import { cookies } from "next/headers";
import { notFound, redirect } from "next/navigation";
import { ApiResponse } from "@/types";
import { getBackendUrl, serverSideApiFetch } from "@/lib/api-client";
import Image from "next/image";
import { Star, User } from "lucide-react";
import { ExternalBook, UserBook, Review } from "@/types";
import ExternalBookPageClient from "@/components/external-book-client";
import UserBookActions from "@/components/user-book-actions";

function renderStars(rate: number) {
  return Array.from({ length: 5 }, (_, i) => (
    <Star
      key={i}
      size={16}
      className={i < rate ? "text-yellow-400 fill-yellow-400" : "text-gray-400"}
      fill={i < rate ? "currentColor" : "none"}
      strokeWidth={1.5}
    />
  ));
}

function getProfilePictureUrl(filename?: string) {
  if (!filename) return '';
  return `${process.env.NEXT_PUBLIC_BACKEND_URL}/uploads/profile_pictures/${filename}`;
}

function ExternalReviewsList({ reviews }: { reviews: Review[] }) {
  return (
    <div className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full">
      <h2 className="text-2xl font-semibold text-blue-500 mb-4">Reviews</h2>
      {reviews.length === 0 ? (
        <p className="text-blue-200 italic">No reviews yet.</p>
      ) : (
        <ul className="space-y-4">
          {reviews.map((review) => (
            <li key={review.id} className="bg-blue-800 p-4 rounded shadow relative">
              {review.user_name && (
                <div className="flex items-center gap-3 mb-3">
                  {review.user_profile_picture ? (
                    <Image
                      src={getProfilePictureUrl(review.user_profile_picture)}
                      alt={review.user_name}
                      width={32}
                      height={32}
                      className="w-8 h-8 rounded-full object-cover border border-blue-500"
                    />
                  ) : (
                    <div className="w-8 h-8 bg-blue-700 border border-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-sm text-blue-200 font-medium">
                        {review.user_name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  )}
                  <div className="flex items-center gap-1 text-blue-300 text-sm font-medium">
                    <User size={14} />
                    <span>{review.user_name}</span>
                  </div>
                </div>
              )}
              <p className="text-blue-200 my-2">{review.content}</p>
              <div className="flex justify-between items-center mt-3">
                <p className="text-blue-100 text-sm flex items-center gap-1">
                  {renderStars(review.rate)}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export const dynamic = "force-dynamic";

async function getExternalBookData(
  externalId: string,
  accessToken: string,
): Promise<{ book: ExternalBook; userBook: UserBook; reviews: Review[] }> {
  try {
    const response = (await serverSideApiFetch(
      `${getBackendUrl()}/books/external/${externalId}`,
      accessToken,
      {
        cache: 'no-store',
      },
    )) as ApiResponse<{
      book: ExternalBook;
      userBook: UserBook;
      reviews: Review[];
    }>;
    const data = response.data;

    if (!data || !data.book || !data.book.external_id) {
      throw new Error("Invalid book data received");
    }

    return data;
  } catch (error) {
    throw error;
  }
}

type Props = {
  params: Promise<{ externalId: string }>;
};

export default async function ExternalBookPage({ params }: Props) {
  const { externalId } = await params;
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value ?? '';

  try {
    const { book, userBook, reviews } = await getExternalBookData(
      externalId,
      accessToken,
    );

    if (!book) notFound();

    return (
      <div className="p-6 bg-blue-950 text-blue-50 min-h-screen flex flex-col items-center">
        <div className="relative bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-1">
              {book.thumbnail && (
                <Image
                  src={book.thumbnail.replace(/^http:\/\//, 'https://')}
                  alt={book.title}
                  width={80}
                  height={80}
                  className="w-full rounded-md shadow-md"
                />
              )}
            </div>

            <div className="md:col-span-2">
              <div className="flex justify-between items-start">
                <h1 className="text-3xl font-bold text-blue-500 mb-2">
                  {book.title}
                </h1>
              </div>

              <p className="text-sm italic text-blue-100 mb-4">
                By {book.authors?.join(", ") || "Unknown Author"}
              </p>

              {book.description && (
                <p className="text-blue-200 leading-relaxed mb-4">
                  {book.description}
                </p>
              )}

              {/* Additional Info */}
              <div className="text-blue-200 space-y-2">
                <p>
                  <span className="font-semibold">Published:</span>{" "}
                  {book.publishedDate}
                </p>
                <p>
                  <span className="font-semibold">Pages:</span> {book.pageCount}
                </p>
                <p>
                  <span className="font-semibold">Language:</span>{" "}
                  {book.language}
                </p>
                {book.categories && book.categories.length > 0 && (
                  <p>
                    <span className="font-semibold">Categories:</span>{" "}
                    {book.categories.join(", ")}
                  </p>
                )}
              </div>

              <UserBookActions
                externalId={externalId}
                userBook={userBook}
                book={book}
              />
              {userBook && (
                <ExternalBookPageClient
                  userBook={userBook}
                  externalId={externalId}
                />
              )}
            </div>
          </div>

          <div className="mt-5">
            <ExternalReviewsList reviews={reviews} />
          </div>
        </div>
      </div>
    );
  } catch (error) {
    if (error instanceof Error && error.message.includes('401')) {
      redirect('/login');
    }
    return (
      <div className="p-6 bg-blue-950 text-red-400 min-h-screen flex items-center justify-center">
        <div className="bg-red-900/50 p-4 rounded-lg max-w-md text-center">
          <h2 className="text-xl font-semibold mb-2">Error Loading Book</h2>
          <p>
            We encountered an error while loading this book. Please try again
            later.
          </p>
        </div>
      </div>
    );
  }
}
