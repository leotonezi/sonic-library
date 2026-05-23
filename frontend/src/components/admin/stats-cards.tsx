"use client";

import { Users, UserCheck, BookOpen, MessageSquare, Library, Star } from "lucide-react";
import type { AdminStats } from "@/types";

interface StatsCardsProps {
  stats: AdminStats | null | undefined;
}

const cards = [
  { key: "total_users" as const, label: "Total Users", icon: Users },
  { key: "total_active_users" as const, label: "Active Users", icon: UserCheck },
  { key: "total_books" as const, label: "Total Books", icon: BookOpen },
  { key: "total_reviews" as const, label: "Total Reviews", icon: MessageSquare },
  { key: "total_user_books" as const, label: "Total User-Books", icon: Library },
  { key: "avg_rating" as const, label: "Avg Rating", icon: Star },
];

function formatValue(key: string, value: number): string {
  if (key === "avg_rating") return value.toFixed(1);
  return value.toLocaleString();
}

export function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      {cards.map(({ key, label, icon: Icon }) => (
        <div
          key={key}
          className="bg-blue-900 border border-blue-600 p-6 rounded-lg shadow-md"
        >
          <div className="flex items-center gap-3">
            <Icon className="text-orange-300" size={24} />
            <div>
              <p className="text-sm text-blue-300">{label}</p>
              {stats ? (
                <p className="text-2xl font-bold text-blue-100">
                  {formatValue(key, stats[key])}
                </p>
              ) : (
                <div className="h-8 w-20 bg-blue-800 rounded animate-pulse mt-1" />
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
