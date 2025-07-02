import Review from "@/interfaces/review";
import ReviewActions from "./review-actions";
import { Star, User } from "lucide-react";

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
  if (!filename) return undefined;
  return `${process.env.NEXT_PUBLIC_BACKEND_URL}/uploads/profile_pictures/${filename}`;
};

export default function ReviewsList({ reviews = [] }: { reviews?: Review[] }) {
  if (!reviews) {
    return null;
  }
  return (
    <div className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full">
      <h2 className="text-2xl font-semibold text-blue-500 mb-4">Reviews</h2>
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
                    <img
                      src={getProfilePictureUrl(review.user_profile_picture)}
                      alt={review.user_name}
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
