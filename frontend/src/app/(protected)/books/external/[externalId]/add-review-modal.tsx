import { Fragment, useState } from "react";
import { Dialog, Transition } from "@headlessui/react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/useAuthStore";

type AddReviewModalProps = {
  open: boolean;
  onClose: () => void;
  bookId: number;
  externalId?: string;
  onReviewAdded?: () => void;
};

export default function AddReviewModal({
  open,
  onClose,
  bookId,
  externalId,
  onReviewAdded,
}: AddReviewModalProps) {
  const [content, setContent] = useState("");
  const [rate, setRating] = useState(5);
  const [loading, setLoading] = useState(false);
  const user = useAuthStore((state) => state.user);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

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
            content,
            rate,
            book_id: bookId,
            external_book_id: externalId,
            user_id: user?.id,
          }),
        },
      );

      if (!response.ok) {
        throw new Error("Failed to submit review");
      }

      toast.success("Review added successfully!");
      setContent("");
      setRating(5);
      onReviewAdded?.();
      router.refresh();
      onClose();
    } catch (error) {
      toast.error("Failed to add review");
      console.error("Review creation failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Transition appear show={open} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/50" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-blue-950 p-6 text-left align-middle shadow-xl transition-all">
                <Dialog.Title
                  as="h3"
                  className="text-xl font-bold mb-4 text-blue-200"
                >
                  Add a Review
                </Dialog.Title>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <textarea
                    className="w-full p-2 rounded bg-blue-900 text-blue-50"
                    rows={4}
                    placeholder="Write your review..."
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    required
                    disabled={loading}
                  />
                  <div>
                    <label className="text-blue-200 mr-2">Rating:</label>
                    <select
                      className="bg-blue-900 text-blue-50 rounded p-1"
                      value={rate}
                      onChange={(e) => setRating(Number(e.target.value))}
                      disabled={loading}
                    >
                      {[1, 2, 3, 4, 5].map((n) => (
                        <option key={n} value={n}>
                          {n}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex justify-end space-x-2">
                    <button
                      type="button"
                      className="px-4 py-2 bg-blue-700 rounded text-blue-50"
                      onClick={onClose}
                      disabled={loading}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-blue-500 rounded text-blue-50 font-semibold"
                      disabled={loading}
                    >
                      {loading ? "Submitting..." : "Submit"}
                    </button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
