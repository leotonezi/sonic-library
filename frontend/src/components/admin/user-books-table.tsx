"use client";

import { useState, useEffect, useCallback } from "react";
import { Search, Trash2 } from "lucide-react";
import type { AdminUserBook, PaginationResponse } from "@/types";
import { getUserBooks, deleteUserBook } from "@/services/adminService";
import { Pagination } from "@/components/pagination";
import { toast } from "sonner";

const statusColors: Record<string, string> = {
  TO_READ: "bg-gray-700 text-gray-200 border-gray-500",
  READING: "bg-blue-800 text-blue-200 border-blue-500",
  READ: "bg-green-900 text-green-300 border-green-700",
};

export function AdminUserBooksTable() {
  const [data, setData] = useState<PaginationResponse<AdminUserBook> | null>(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [loading, setLoading] = useState(true);
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
    const result = await getUserBooks(page, debouncedSearch || undefined);
    setData(result);
    setLoading(false);
  }, [page, debouncedSearch]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleDelete = async (id: number) => {
    const result = await deleteUserBook(id);
    if (result !== null) {
      toast.success("User-book record deleted");
      setConfirmDeleteId(null);
      fetchData();
    } else {
      toast.error("Failed to delete user-book record");
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
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Added</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="border-b border-blue-800">
                  {Array.from({ length: 6 }).map((_, j) => (
                    <td key={j} className="px-4 py-3">
                      <div className="h-4 w-16 bg-blue-800 rounded animate-pulse" />
                    </td>
                  ))}
                </tr>
              ))
            ) : !data || data.items.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-blue-400">
                  No user-book records found.
                </td>
              </tr>
            ) : (
              data.items.map((ub) => (
                <tr
                  key={ub.id}
                  className="border-b border-blue-800 bg-blue-900 hover:bg-blue-800 transition-colors"
                >
                  <td className="px-4 py-3 text-blue-200">{ub.id}</td>
                  <td className="px-4 py-3 text-white">{ub.user_name}</td>
                  <td className="px-4 py-3 text-blue-200">{ub.book_title || ub.external_book_id || "—"}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium border ${statusColors[ub.status] || "bg-blue-800 text-blue-200 border-blue-600"}`}
                    >
                      {ub.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-blue-200">
                    {new Date(ub.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3">
                    <button onClick={() => setConfirmDeleteId(ub.id)} className="text-red-400 hover:text-red-300">
                      <Trash2 size={16} />
                    </button>
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

      {/* Delete Confirmation */}
      {confirmDeleteId !== null && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-blue-900 border border-blue-600 rounded-lg p-6 w-full max-w-sm">
            <h3 className="text-white text-lg font-semibold mb-2">Delete User-Book</h3>
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
