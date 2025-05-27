import Review from '@/interfaces/review';
import ReviewActions from './review-actions';
import { Star } from 'lucide-react';

const renderStars = (rate: number) => {
  return Array.from({ length: 5 }, (_, i) => (
    <Star
      key={i}
      size={16}
      className={i < rate ? 'text-yellow-400 fill-yellow-400' : 'text-gray-400'}
      fill={i < rate ? 'currentColor' : 'none'}
      strokeWidth={1.5}
    />
  ));
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
            <li key={review.id} className="bg-blue-800 p-4 rounded shadow relative">
              <ReviewActions review={review} />
              <p className="text-blue-200 my-2">{review.content}</p>
              <p className="text-blue-100 text-sm flex items-center gap-1">
                {renderStars(review.rate)}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}