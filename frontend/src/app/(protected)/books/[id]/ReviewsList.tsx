// app/books/[id]/ReviewsList.tsx
'use client';

import { useState } from 'react';
import { Pencil, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import Review from '@/types/review';

type ReviewsListProps = {
  initialReviews: Review[];
};

export default function ReviewsList({ initialReviews }: ReviewsListProps) {
  const [reviews, setReviews] = useState<Review[]>(initialReviews);
  const [editReviewId, setEditReviewId] = useState<number | null>(null);
  const [editedContent, setEditedContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const router = useRouter();
  const user = useAuthStore((state) => state.user);

  const handleDeleteReview = async (reviewId: number) => {
    if (!confirm('Are you sure you want to delete this review?')) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/reviews/${reviewId}`,
        {
          method: 'DELETE',
          credentials: 'include',
        }
      );

      if (!response.ok) {
        throw new Error('Failed to delete review');
      }

      toast.success('Review deleted successfully!');
      setReviews((prev) => prev.filter((r) => r.id !== reviewId));
      router.refresh();
    } catch (error) {
      toast.error('Failed to delete review');
      console.error('Review deletion failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditReview = async (reviewId: number) => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/reviews/${reviewId}`,
        {
          method: 'PUT',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content: editedContent }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to update review');
      }

      toast.success('Review updated successfully!');
      setReviews((prev) =>
        prev.map((r) =>
          r.id === reviewId ? { ...r, content: editedContent } : r
        )
      );
      setEditReviewId(null);
      setEditedContent('');
      router.refresh();
    } catch (error) {
      toast.error('Failed to update review');
      console.error('Review update failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full">
      <h2 className="text-2xl font-semibold text-blue-500 mb-4">Reviews</h2>
      {reviews.length === 0 ? (
        <p className="text-blue-200 italic">No reviews yet.</p>
      ) : (
        <ul className="space-y-4">
          {reviews?.map((r) => (
            <li key={r.id} className="bg-blue-800 p-4 rounded shadow relative">
              <div className="absolute top-2 right-2 flex gap-2">
                {user?.id === r.user_id && (
                  <>
                    <button
                      onClick={() => {
                        setEditReviewId(r.id);
                        setEditedContent(r.content);
                      }}
                      className="text-blue-300 hover:text-orange-400 cursor-pointer"
                      aria-label="Edit review"
                      disabled={isLoading}
                    >
                      <Pencil size={16} />
                    </button>
                    <button
                      onClick={() => handleDeleteReview(r.id)}
                      className="text-blue-300 hover:text-orange-400 cursor-pointer"
                      aria-label="Delete review"
                      disabled={isLoading}
                    >
                      <Trash2 size={16} />
                    </button>
                  </>
                )}
              </div>
              {editReviewId === r.id ? (
                <div className="space-y-2 mt-4">
                  <textarea
                    className="w-full p-2 rounded bg-white text-blue-800"
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    disabled={isLoading}
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEditReview(r.id)}
                      className="btn-primary text-sm"
                      disabled={isLoading}
                    >
                      {isLoading ? 'Saving...' : 'Save'}
                    </button>
                    <button
                      onClick={() => {
                        setEditReviewId(null);
                        setEditedContent('');
                      }}
                      className="btn-inverted text-sm"
                      disabled={isLoading}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <p className="text-blue-200 my-2">{r.content}</p>
                  <p className="text-blue-100 text-sm">Rate: {r.rate}/5</p>
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}