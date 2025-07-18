"use client";

import { useState } from "react";
import { Star } from "lucide-react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/useAuthStore";

export default function AddReviewForm({ bookId }: { bookId: number | null }) {
  const [review, setReview] = useState("");
  const [rate, setRate] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const user = useAuthStore((state) => state.user);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/reviews/`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            content: review,
            rate: Number(rate),
            book_id: bookId,
            user_id: user?.id,
          }),
        },
      );

      if (!response.ok) {
        throw new Error("Failed to submit review");
      }

      toast.success("Review added successfully!");
      setReview("");
      setRate("");

      // Refresh the page to show the new review
      router.refresh();
    } catch (error) {
      toast.error("Failed to submit review");
      console.error("Review submission failed:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md max-w-2xl w-full mb-6">
      <h2 className="text-2xl font-semibold text-blue-500 mb-4">
        Add a Review
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          placeholder="Write your review..."
          className="w-full p-3 rounded text-black bg-white"
          value={review}
          onChange={(e) => setReview(e.target.value)}
          required
          disabled={isSubmitting}
        />
        <div className="flex items-center gap-2">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              className={`text-2xl transition-colors cursor-pointer ${
                Number(rate) >= star
                  ? "text-yellow-400 fill-yellow-400"
                  : "text-gray-400"
              }`}
              onClick={() => setRate(String(star))}
              disabled={isSubmitting}
              aria-label={`Rate ${star} star${star > 1 ? "s" : ""}`}
            >
              <Star size={16} />
            </button>
          ))}
        </div>
        <button
          type="submit"
          className="btn-primary relative"
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <>
              <span className="opacity-0">Submit Review</span>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-5 h-5 border-t-2 border-b-2 border-white rounded-full animate-spin" />
              </div>
            </>
          ) : (
            "Submit Review"
          )}
        </button>
      </form>
    </div>
  );
}
