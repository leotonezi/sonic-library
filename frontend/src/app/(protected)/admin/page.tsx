"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/store/useAuthStore";
import { ADMIN_EMAILS } from "@/config";
import { getStats } from "@/services/adminService";
import type { AdminStats } from "@/interfaces/admin";
import { StatsCards } from "@/components/admin/stats-cards";
import { AdminUsersTable } from "@/components/admin/users-table";
import { AdminReviewsTable } from "@/components/admin/reviews-table";
import { AdminUserBooksTable } from "@/components/admin/user-books-table";
const TABS = [
  { key: "users", label: "Users" },
  { key: "reviews", label: "Reviews" },
  { key: "user-books", label: "User Books" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

export default function AdminDashboard() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const user = useAuthStore((state) => state.user);
  const [stats, setStats] = useState<AdminStats | null>(null);

  const activeTab = (searchParams.get("tab") as TabKey) || "users";

  useEffect(() => {
    if (user && !ADMIN_EMAILS.includes(user.email)) {
      router.replace("/books");
    }
  }, [user, router]);

  useEffect(() => {
    getStats().then((data) => {
      if (data) setStats(data);
    });
  }, []);

  const setTab = (tab: TabKey) => {
    router.push(`/admin?tab=${tab}`);
  };

  if (!user || !ADMIN_EMAILS.includes(user.email)) {
    return null;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-6">Admin Dashboard</h1>

      <StatsCards stats={stats} />

      {/* Tabs */}
      <div className="flex border-b border-blue-600 mb-6">
        {TABS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`px-6 py-3 text-sm font-medium transition-colors ${
              activeTab === key
                ? "text-orange-300 border-b-2 border-orange-300"
                : "text-blue-400 hover:text-white"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "users" && <AdminUsersTable />}
      {activeTab === "reviews" && <AdminReviewsTable />}
      {activeTab === "user-books" && <AdminUserBooksTable />}
    </div>
  );
}
