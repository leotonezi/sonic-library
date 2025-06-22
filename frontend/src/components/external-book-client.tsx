"use client";

import { useState } from "react";
import { UserBook } from "@/interfaces/book";
import AddReviewModal from "@/app/(protected)/books/external/[externalId]/add-review-modal";

type Props = {
  userBook: UserBook;
  externalId: string;
};

export default function ExternalBookPageClient({
  userBook,
  externalId,
}: Props) {
  const [modalOpen, setModalOpen] = useState(false);
  const bookId = userBook?.book_id;
  return (
    <>
      <button
        className="mt-4 px-4 py-2 bg-blue-600 text-blue-50 hover:bg-blue-700 rounded cursor-pointer"
        onClick={() => setModalOpen(true)}
      >
        Add Review
      </button>
      {typeof bookId === "number" && (
        <AddReviewModal
          bookId={bookId}
          externalId={externalId}
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          onReviewAdded={() => {}}
        />
      )}
    </>
  );
}
