"use client";

import { useState, useEffect, useCallback } from "react";
import { Search, Pencil, Trash2, Star } from "lucide-react";
import type { AdminReview, PaginationResponse } from "@/interfaces/admin";
import { getReviews, updateReview, deleteReview } from "@/services/adminService";
import { Pagination } from "@/components/pagination";
import { toast } from "sonner";

export function AdminReviewsTable() {
  const [data, setData] = useState<PaginationResponse<AdminReview> | null>(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editContent, setEditContent] = useState("");
  const [editRate, setEditRate] = useState(1);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    const result = await getReviews(page, debouncedSearch || undefined);
    setData(result);
    setLoading(false);
  }, [page, debouncedSearch]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleEdit = (review: AdminReview) => {
    setEditingId(review.id);
    setEditContent(review.content);
    setEditRate(review.rate);
  };

  const handleSaveEdit = async () => {
    if (editingId === null) return;
    const result = await updateReview(editingId, { content: editContent, rate: editRate });
    if (result) {
      toast.success("Review updated");
      setEditingId(null);
      fetchData();
    } else {
      toast.error("Failed to update review");
    }
  };

  const handleDelete = async (id: number) => {
    const result = await deleteReview(id);
    if (result !== null) {
      toast.success("Review deleted");
      setConfirmDeleteId(null);
      fetchData();
    } else {
      toast.error("Failed to delete review");
    }
  };

  return (
    <div>
      <div className="mb-4">
        <div className="flex items-center bg-blue-950 border border-blue-600 rounded-md max-w-md">
          <Search size={16} className="ml-3 text-blue-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by user name or book title..."
            className="w-full px-3 py-2 bg-transparent text-white placeholder-blue-400 focus:outline-none text-sm"
          />
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border border-blue-600">
        <table className="w-full text-sm text-left">
          <thead className="bg-blue-950 text-blue-300 border-b border-blue-600">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">User</th>
              <th className="px-4 py-3">Book</th>
              <th className="px-4 py-3">Rating</th>
              <th className="px-4 py-3">Content</th>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="border-b border-blue-800">
                  {Array.from({ length: 7 }).map((_, j) => (
                    <td key={j} className="px-4 py-3">
                      <div className="h-4 w-16 bg-blue-800 rounded animate-pulse" />
                    </td>
                  ))}
                </tr>
              ))
            ) : !data || data.items.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-blue-400">
                  No reviews found.
                </td>
              </tr>
            ) : (
              data.items.map((review) => (
                <tr
                  key={review.id}
                  className="border-b border-blue-800 bg-blue-900 hover:bg-blue-800 transition-colors"
                >
                  <td className="px-4 py-3 text-blue-200">{review.id}</td>
                  <td className="px-4 py-3 text-white">{review.user_name}</td>
                  <td className="px-4 py-3 text-blue-200">{review.book_title || review.external_book_id || "—"}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-0.5">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star
                          key={i}
                          size={14}
                          className={i < review.rate ? "text-orange-300 fill-orange-300" : "text-blue-700"}
                        />
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-blue-200 max-w-xs truncate">
                    {review.content.length > 100 ? review.content.slice(0, 100) + "..." : review.content}
                  </td>
                  <td className="px-4 py-3 text-blue-200">
                    {new Date(review.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleEdit(review)} className="text-orange-300 hover:text-orange-200">
                        <Pencil size={16} />
                      </button>
                      <button onClick={() => setConfirmDeleteId(review.id)} className="text-red-400 hover:text-red-300">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {data && (
        <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
      )}

      {/* Edit Modal */}
      {editingId !== null && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-blue-900 border border-blue-600 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-white text-lg font-semibold mb-4">Edit Review</h3>
            <label className="block text-blue-300 text-sm mb-1">Rating (1-5)</label>
            <input
              type="number"
              min={1}
              max={5}
              value={editRate}
              onChange={(e) => setEditRate(Number(e.target.value))}
              className="w-full mb-3 px-3 py-2 bg-blue-950 border border-blue-600 rounded text-white text-sm"
            />
            <label className="block text-blue-300 text-sm mb-1">Content</label>
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              rows={4}
              className="w-full mb-4 px-3 py-2 bg-blue-950 border border-blue-600 rounded text-white text-sm"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setEditingId(null)}
                className="px-4 py-2 text-sm text-blue-300 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                className="px-4 py-2 text-sm bg-orange-500 hover:bg-orange-600 text-white rounded"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      {confirmDeleteId !== null && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-blue-900 border border-blue-600 rounded-lg p-6 w-full max-w-sm">
            <h3 className="text-white text-lg font-semibold mb-2">Delete Review</h3>
            <p className="text-blue-300 text-sm mb-4">Are you sure? This action cannot be undone.</p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setConfirmDeleteId(null)}
                className="px-4 py-2 text-sm text-blue-300 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(confirmDeleteId)}
                className="px-4 py-2 text-sm bg-red-600 hover:bg-red-700 text-white rounded"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
