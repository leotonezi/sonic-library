"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch, apiPost } from "@/utils/api";
import Book from "@/types/book";
import Review from "@/types/review";
import { ApiResponse } from "@/types/auth";
import { toast } from "sonner";

export default function BookPage() {
  const [book, setBook] = useState<Book | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [review, setReview] = useState("");
  const [rate, setRate] = useState("");
  const [loading, setLoading] = useState(true);
  const params = useParams();

  const fetchBookAndReviews = useCallback(async () => {
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
  }, [params.id]);

  useEffect(() => {
    if (params?.id) {
      fetchBookAndReviews();
    }
  }, [params?.id, fetchBookAndReviews]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const response = await apiPost<ApiResponse<Review>>('/reviews/', {
      content: review,
      rate: Number(rate),
      book_id: Number(params.id),
      user_id: 1,
    });

    if (response?.ok) {
      toast.success('Review added!');

      setReview("");
      setRate("");
      setReviews(prev => [...prev, response.data as Review]);
    } else {
      toast.error("Failed to submit review");
    }
  };

  if (loading) return <p className="text-white p-6">Loading...</p>;
  if (!book) return <p className="text-white p-6">Book not found</p>;

  return (
    <main className="p-6 bg-blue-950 text-blue-50 min-h-screen flex flex-col items-center">
      <div className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full mb-6">
        <h1 className="text-3xl font-bold text-blue-500 mb-2">{book.title}</h1>
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
          <input
            type="number"
            placeholder="Rate (1–5)"
            className="w-full p-2 rounded text-black bg-white"
            value={rate}
            onChange={(e) => {
              const value = Number(e.target.value);
              if (value >= 1 && value <= 5) {
                setRate(e.target.value);
              }
            }}
            min={1}
            max={5}
            required
          />
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
              <li key={r.id} className="bg-blue-800 p-4 rounded shadow">
                <p className="text-blue-200">{r.content}</p>
                <p className="text-blue-100 text-sm">Rate: {r.rate}/5</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}