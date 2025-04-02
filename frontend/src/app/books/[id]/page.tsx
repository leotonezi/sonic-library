"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

interface Book {
  id: string;
  title: string;
  author: string;
  description?: string;
}

interface Review {
  id: number;
  content: string;
  rate: number;
  user_id: number;
  created_at?: string;
}

export default function BookPage() {
  const [book, setBook] = useState<Book | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [review, setReview] = useState("");
  const [rate, setRate] = useState("");
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const params = useParams();

  useEffect(() => {
    const fetchBookAndReviews = async () => {
      try {
        const [bookRes, reviewsRes] = await Promise.all([
          fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/books/${params.id}`),
          fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/reviews/book/${params.id}`)
        ]);

        const bookData = await bookRes.json();
        const reviewData = await reviewsRes.json();

        setBook(bookData);
        setReviews(reviewData);
      } catch (err) {
        console.error("Failed to fetch book or reviews", err);
      } finally {
        setLoading(false);
      }
    };

    if (params?.id) {
      fetchBookAndReviews();
    }
  }, [params?.id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/reviews`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content: review,
        rate: Number(rate),
        book_id: Number(params.id),
        user_id: 1,
      }),
    });

    if (response.ok) {
      setReview("");
      setRate("");
      router.refresh(); // Refresh route to get new reviews
    } else {
      alert("Failed to submit review");
    }
  };

  if (loading) return <p className="text-white p-6">Loading...</p>;
  if (!book) return <p className="text-white p-6">Book not found</p>;

  return (
    <main className="p-6 bg-[#0a1128] text-[#e0f0ff] min-h-screen flex flex-col items-center">
      <div className="bg-[#001f3f] border border-[#0077cc] p-6 rounded-lg shadow-md max-w-2xl w-full mb-6">
        <h1 className="text-3xl font-bold text-[#00aaff] mb-2">{book.title}</h1>
        <p className="text-sm italic text-[#66ccff] mb-4">By {book.author}</p>
        {book.description && (
          <p className="text-[#cceeff] leading-relaxed">{book.description}</p>
        )}
      </div>

      <div className="bg-[#001f3f] border border-[#0077cc] p-6 rounded-lg shadow-md max-w-2xl w-full mb-6">
        <h2 className="text-2xl font-semibold text-[#00aaff] mb-4">Add a Review</h2>
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
            placeholder="Rate (1-5)"
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
            className="bg-[#00aaff] text-white px-4 py-2 rounded hover:bg-[#0077cc]"
          >
            Submit Review
          </button>
        </form>
      </div>

      <div className="bg-[#001f3f] border border-[#0077cc] p-6 rounded-lg shadow-md max-w-2xl w-full">
        <h2 className="text-2xl font-semibold text-[#00aaff] mb-4">Reviews</h2>
        {reviews.length === 0 ? (
          <p className="text-[#cceeff] italic">No reviews yet.</p>
        ) : (
          <ul className="space-y-4">
            {reviews.map((r) => (
              <li key={r.id} className="bg-[#003366] p-4 rounded shadow">
                <p className="text-[#cceeff]">{r.content}</p>
                <p className="text-[#66ccff] text-sm">Rate: {r.rate}/5</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}