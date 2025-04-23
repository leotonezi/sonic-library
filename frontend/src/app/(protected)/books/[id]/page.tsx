'use client';

import { useCallback, useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { apiFetch, apiPost } from "@/utils/api";
import Book from "@/types/book";
import Review from "@/types/review";
import { toast } from "sonner";
import { Pencil, Star, Trash2 } from "lucide-react";
import { useAuthStore } from "@/store/useAuthStore";

export default function BookPage() {
  const router = useRouter();
  const [book, setBook] = useState<Book | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [review, setReview] = useState("");
  const [rate, setRate] = useState("");
  const [loading, setLoading] = useState(true);
  const [editReviewId, setEditReviewId] = useState<number | null>(null);
  const [editedContent, setEditedContent] = useState("");

  const params = useParams();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  useEffect(() => {
    if (!user) {
      logout();
      router.push("/login");
    }
  }, [user, logout, router]);

  const fetchBookAndReviews = useCallback(async () => {
    if (!user || !params?.id) return;
    try {
      const [bookRes, reviewsRes] = await Promise.all([
        apiFetch<Book>(`/books/${params.id}`),
        apiFetch<Review[]>(`/reviews/book/${params.id}`, { noCache: true }),
      ]);

      setBook(bookRes);
      setReviews(reviewsRes ?? []);
    } catch (err) {
      console.error("Failed to fetch book or reviews", err);
    } finally {
      setLoading(false);
    }
  }, [params?.id, user]);

  useEffect(() => {
    if (params?.id) {
      fetchBookAndReviews();
    }
  }, [params?.id, fetchBookAndReviews]);

  const averageRating =
    reviews.length > 0
      ? (reviews.reduce((sum, r) => sum + r.rate, 0) / reviews.length).toFixed(1)
      : null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await apiPost<Review>('/reviews/', {
        content: review,
        rate: Number(rate),
        book_id: Number(params.id),
        user_id: 1,
      });
    
      toast.success("Review added!");
      setReview("");
      setRate("");
      setReviews(prev => [...prev, response]);
    } catch (err) {
      toast.error("Failed to submit review");
      console.error("Review post failed:", err);
    }
  };

  const handleDeleteReview = async (reviewId: number) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/reviews/${reviewId}`, {
      method: "DELETE",
    });

    if (response.ok) {
      toast.success("Review deleted!");
      setReviews((prev) => prev.filter((r) => r.id !== reviewId));
    } else {
      toast.error("Failed to delete review");
    }
  };

  const handleEditReview = async (reviewId: number) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/reviews/${reviewId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content: editedContent }),
    });

    if (response.ok) {
      toast.success("Review updated!");
      setReviews((prev) =>
        prev.map((r) => (r.id === reviewId ? { ...r, content: editedContent } : r))
      );
      setEditReviewId(null);
      setEditedContent("");
    } else {
      toast.error("Failed to update review");
    }
  };

  if (loading) return <p className="text-white p-6">Loading...</p>;
  if (!book) return <p className="text-white p-6">Book not found</p>;

  return (
    <main className="p-6 bg-blue-950 text-blue-50 min-h-screen flex flex-col items-center">
     <div className="relative bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full mb-6">
      <div className="flex justify-between items-start">
        <h1 className="text-3xl font-bold text-blue-500 mb-2">{book.title}</h1>
        {averageRating && (
          <div className="flex items-center text-yellow-400 text-2xl ml-4">
            {averageRating}
            <Star className="ml-1" size={24} />
          </div>
        )}
      </div>

      <p className="text-sm italic text-blue-100 mb-4">By {book.author}</p>

      {book.description && (
        <p className="text-blue-200 leading-relaxed">{book.description}</p>
      )}
    </div>

      <div className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full mb-6">
        <h2 className="text-2xl font-semibold text-blue-500 mb-4">Add a Review</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea
            placeholder="Write your review..."
            className="w-full p-3 rounded text-black bg-white"
            value={review}
            onChange={(e) => setReview(e.target.value)}
            required
          />
          <div className="flex items-center gap-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                className={`text-2xl transition-colors cursor-pointer ${
                  Number(rate) >= star ? "text-yellow-400" : "text-gray-400"
                }`}
                onClick={() => setRate(String(star))}
                aria-label={`Rate ${star} star${star > 1 ? "s" : ""}`}
              >
                <Star size={16}/>
              </button>
            ))}
          </div>
          <button
            type="submit"
            className="btn-primary"
            >
            Submit Review
          </button>
        </form>
      </div>

      <div className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full">
        <h2 className="text-2xl font-semibold text-blue-500 mb-4">Reviews</h2>
        {reviews.length === 0 ? (
          <p className="text-blue-200 italic">No reviews yet.</p>
        ) : (
          <ul className="space-y-4">
            {reviews.map((r) => (
              <li key={r.id} className="bg-blue-800 p-4 rounded shadow relative">
                <div className="absolute top-2 right-2 flex gap-2">
                {user.id === r.user_id &&
                <>
                  <button
                    onClick={() => {
                      setEditReviewId(r.id);
                      setEditedContent(r.content);
                    }}
                    className="text-blue-300 hover:text-orange-400 cursor-pointer mb-4"
                    aria-label="Edit review"
                  >
                    <Pencil size={16} />
                  </button>
                  <button
                    onClick={() => handleDeleteReview(r.id)}
                    className="text-blue-300 hover:text-orange-400 cursor-pointer mb-4"
                    aria-label="Delete review"
                  >
                    <Trash2 size={16} />
                  </button>
                </>
                }
                </div>
                {editReviewId === r.id ? (
                  <div className="space-y-2 mt-4">
                    <textarea
                      className="w-full p-2 rounded bg-white text-blue-800"
                      value={editedContent}
                      onChange={(e) => setEditedContent(e.target.value)}
                    />
                    <button
                      onClick={() => handleEditReview(r.id)}
                      className="btn-primary text-sm"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => {
                        setEditReviewId(null);
                        setEditedContent("");
                      }}
                      className="btn-inverted text-sm ml-2"
                    >
                      Cancel
                    </button>
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
    </main>
  );
}