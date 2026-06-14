import { Suspense } from "react";
import { cookies } from "next/headers";
import { notFound, redirect } from "next/navigation";
import AddReviewForm from "./add-review-form";
import ReviewsList from "./review-list";
import ReviewsSkeleton from "./reviews-skeleton";
import { Book } from "@/types";
import { ApiResponse } from "@/types";
import { serverSideApiFetch, getBackendUrl, ApiError } from "@/lib/api-client";

export const dynamic = "force-dynamic";

async function getBookData(
  bookId: string,
  accessToken: string,
): Promise<Book> {
  const bookData = (await serverSideApiFetch(
    `${getBackendUrl()}/books/${bookId}`,
    accessToken,
  )) as ApiResponse<Book>;

  const book = bookData?.data;

  if (!book || !book.id) {
    throw new Error("Invalid book data received");
  }

  return book;
}

export default async function BookPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const cookieStore = await cookies();
  const accessToken = cookieStore.get("access_token")?.value ?? '';

  if (!accessToken) {
    redirect('/login');
  }

  if (!id || isNaN(Number(id))) {
    notFound();
  }

  let book: Book;
  try {
    book = await getBookData(id, accessToken);
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      redirect('/login');
    }
    throw error;
  }

  if (!book) {
    notFound();
  }

  return (
    <div className="p-6 bg-blue-950 text-blue-50 min-h-screen flex flex-col items-center">
      <div className="relative bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full mb-6">
        <div className="flex justify-between items-start">
          <h1 className="text-3xl font-bold text-blue-500 mb-2">
            {book.title}
          </h1>
        </div>
        <p className="text-sm italic text-blue-100 mb-4">By {book.author}</p>
        {book.description && (
          <p className="text-blue-200 leading-relaxed">{book.description}</p>
        )}
      </div>

      <AddReviewForm bookId={book?.id} />
      <Suspense fallback={<ReviewsSkeleton />}>
        <ReviewsList bookId={id} token={accessToken} />
      </Suspense>
    </div>
  );
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return {
    title: `Book ${id}`,
  };
}
