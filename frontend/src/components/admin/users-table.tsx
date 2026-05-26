"use client";

import { useState, useEffect, useCallback } from "react";
import { Search } from "lucide-react";
import type { AdminUser, PaginationResponse } from "@/types";
import { getUsers } from "@/services/adminService";
import { Pagination } from "@/components/pagination";

export function AdminUsersTable() {
  const [data, setData] = useState<PaginationResponse<AdminUser> | null>(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [loading, setLoading] = useState(true);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    const result = await getUsers(page, debouncedSearch || undefined);
    setData(result);
    setLoading(false);
  }, [page, debouncedSearch]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div>
      {/* Search */}
      <div className="mb-4">
        <div className="flex items-center bg-blue-950 border border-blue-600 rounded-md max-w-md">
          <Search size={16} className="ml-3 text-blue-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name or email..."
            className="w-full px-3 py-2 bg-transparent text-white placeholder-blue-400 focus:outline-none text-sm"
          />
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-lg border border-blue-600">
        <table className="w-full text-sm text-left">
          <thead className="bg-blue-950 text-blue-300 border-b border-blue-600">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Active</th>
              <th className="px-4 py-3">Books</th>
              <th className="px-4 py-3">Reviews</th>
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
                  No users found.
                </td>
              </tr>
            ) : (
              data.items.map((user) => (
                <tr
                  key={user.id}
                  className="border-b border-blue-800 bg-blue-900 hover:bg-blue-800 transition-colors"
                >
                  <td className="px-4 py-3 text-blue-200">{user.id}</td>
                  <td className="px-4 py-3 text-white">{user.name}</td>
                  <td className="px-4 py-3 text-blue-200">{user.email}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium ${
                        user.is_active
                          ? "bg-green-900 text-green-300 border border-green-700"
                          : "bg-red-900 text-red-300 border border-red-700"
                      }`}
                    >
                      {user.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-blue-200">{user.books_count}</td>
                  <td className="px-4 py-3 text-blue-200">{user.reviews_count}</td>
                  <td className="px-4 py-3 text-orange-300">
                    {/* Actions will be added in US-012 */}
                    —
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {data && (
        <Pagination
          page={data.page}
          totalPages={data.total_pages}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}
