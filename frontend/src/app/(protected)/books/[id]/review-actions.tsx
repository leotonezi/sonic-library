// app/books/[id]/ReviewActions.tsx
'use client';

import { Pencil, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { useAuthStore } from '@/store/useAuthStore';
import Review from '@/types/review';

type ReviewActionsProps = {
  review: Review;
};

export default function ReviewActions({ review }: ReviewActionsProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editedContent, setEditedContent] = useState(review.content);
  const router = useRouter();
  const user = useAuthStore((state) => state.user);

  const handleDeleteReview = async () => {
    if (!confirm('Are you sure you want to delete this review?')) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/reviews/${review.id}`,
        {
          method: 'DELETE',
          credentials: 'include',
        }
      );

      if (!response.ok) {
        throw new Error('Failed to delete review');
      }

      toast.success('Review deleted successfully!');
      router.refresh();
    } catch (error) {
      toast.error('Failed to delete review');
      console.error('Review deletion failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditReview = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/reviews/${review.id}`,
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
      setEditMode(false);
      router.refresh();
    } catch (error) {
      toast.error('Failed to update review');
      console.error('Review update failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!user || user.id !== review.user_id) return null;

  return editMode ? (
    <div className="space-y-2 mt-4">
      <textarea
        className="w-full p-2 rounded bg-white text-blue-800"
        value={editedContent}
        onChange={(e) => setEditedContent(e.target.value)}
        disabled={isLoading}
      />
      <div className="flex gap-2">
        <button
          onClick={handleEditReview}
          className="btn-primary text-sm"
          disabled={isLoading}
        >
          {isLoading ? 'Saving...' : 'Save'}
        </button>
        <button
          onClick={() => setEditMode(false)}
          className="btn-inverted text-sm"
          disabled={isLoading}
        >
          Cancel
        </button>
      </div>
    </div>
  ) : (
    <div className="absolute top-2 right-2 flex gap-2">
      <button
        onClick={() => setEditMode(true)}
        className="text-blue-300 hover:text-orange-400 cursor-pointer"
        aria-label="Edit review"
        disabled={isLoading}
      >
        <Pencil size={16} />
      </button>
      <button
        onClick={handleDeleteReview}
        className="text-blue-300 hover:text-orange-400 cursor-pointer"
        aria-label="Delete review"
        disabled={isLoading}
      >
        <Trash2 size={16} />
      </button>
    </div>
  );
}
