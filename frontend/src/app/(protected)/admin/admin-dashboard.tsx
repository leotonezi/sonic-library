"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/store/useAuthStore";
import { getStats } from "@/services/adminService";
import type { AdminStats } from "@/types";
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

function AdminDashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const user = useAuthStore((state) => state.user);
  const [stats, setStats] = useState<AdminStats | null>(null);

  const rawTab = searchParams.get("tab");
  const VALID_TABS = TABS.map((t) => t.key);
  const isValidTab = (v: string): v is TabKey =>
    (VALID_TABS as string[]).includes(v);

  const isInvalidTab = rawTab !== null && !isValidTab(rawTab);
  const activeTab: TabKey = rawTab && isValidTab(rawTab) ? rawTab : "users";

  useEffect(() => {
    if (user && !user.is_admin) {
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

  if (!user || !user.is_admin) {
    return null;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-6">Admin Dashboard</h1>

      <StatsCards stats={stats} />

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

      {isInvalidTab && (
        <div className="flex flex-col items-start gap-4 py-8">
          <p className="text-orange-300 text-sm font-medium">
            Invalid tab: {rawTab}
          </p>
          <button
            onClick={() => router.push("/admin")}
            className="text-blue-400 hover:text-white text-sm underline transition-colors"
          >
            Go to dashboard
          </button>
        </div>
      )}
      {!isInvalidTab && activeTab === "users" && <AdminUsersTable />}
      {!isInvalidTab && activeTab === "reviews" && <AdminReviewsTable />}
      {!isInvalidTab && activeTab === "user-books" && <AdminUserBooksTable />}
    </div>
  );
}

export default function AdminDashboard() {
  return (
    <Suspense>
      <AdminDashboardContent />
    </Suspense>
  );
}
