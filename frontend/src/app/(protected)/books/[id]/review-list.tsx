import { Review } from "@/types";
import { ApiResponse } from "@/types";
import ReviewActions from "./review-actions";
import { Star, User } from "lucide-react";
import Image from "next/image";
import { serverSideApiFetch, getBackendUrl } from "@/lib/api-client";

const renderStars = (rate: number) => {
  return Array.from({ length: 5 }, (_, i) => (
    <Star
      key={i}
      size={16}
      className={i < rate ? "text-yellow-400 fill-yellow-400" : "text-gray-400"}
      fill={i < rate ? "currentColor" : "none"}
      strokeWidth={1.5}
    />
  ));
};

const getProfilePictureUrl = (filename?: string) => {
  if (!filename) return '';
  return `${process.env.NEXT_PUBLIC_BACKEND_URL}/uploads/profile_pictures/${filename}`;
};

type ReviewsListProps = {
  bookId: string;
  token: string;
};

export default async function ReviewsList({ bookId, token }: ReviewsListProps) {
  const reviewsData = (await serverSideApiFetch(
    `${getBackendUrl()}/reviews/book/${bookId}`,
    token,
    { cache: 'no-store' },
  )) as ApiResponse<Review[]> | null;

  const reviews: Review[] = reviewsData?.data ?? [];

  const averageRating =
    reviews.length > 0
      ? (reviews.reduce((sum, r) => sum + r.rate, 0) / reviews.length).toFixed(1)
      : null;

  return (
    <div className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold text-blue-500">Reviews</h2>
        {averageRating && (
          <div className="flex items-center text-yellow-400 text-xl">
            {averageRating}
            <Star className="ml-1" size={20} />
          </div>
        )}
      </div>
      {reviews.length === 0 ? (
        <p className="text-blue-200 italic">No reviews yet.</p>
      ) : (
        <ul className="space-y-4">
          {reviews.map((review) => (
            <li
              key={review.id}
              className="bg-blue-800 p-4 rounded shadow relative"
            >
              <ReviewActions review={review} />

              {/* User Info with Profile Picture */}
              {review.user_name && (
                <div className="flex items-center gap-3 mb-3">
                  {review.user_profile_picture ? (
                    <Image
                      src={getProfilePictureUrl(review.user_profile_picture)}
                      alt={review.user_name || 'User'}
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
