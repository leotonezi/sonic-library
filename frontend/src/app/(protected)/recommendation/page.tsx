'use client';

import { useEffect, useState } from "react";
import { apiFetch } from "@/utils/api";
import { useAuthStore } from "@/store/useAuthStore";

export default function RecommendationPage() {
  const user = useAuthStore((state) => state.user);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const [recommendationText, setRecommendationText] = useState<string>("");
  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!user) return;

      setLoadingRecommendations(true);

      try {
        const rec = await apiFetch<string>(`/recommendations/${user.id}`, {
          noCache: true,
        });

        if (rec) {
          const cleanText = rec
            .replace(/[*_~`>#-]/g, '')
            .replace(/$begin:math:display$(.*?)$end:math:display$$begin:math:text$.*?$end:math:text$/g, '$1')
            .replace(/\n{2,}/g, '\n\n');
          setRecommendationText(cleanText);
        }
      } catch (error) {
        console.error("❌ Error fetching recommendations:", error);
      } finally {
        setLoadingRecommendations(false);
      }
    };

    if (user?.id) {
      fetchRecommendations();
    }
  }, [user]);

  return (
    <div className="max-w-xl mx-auto mt-10 p-6 bg-blue-900 border border-blue-600 rounded-lg shadow text-white">
      <h1 className="text-2xl font-bold mb-4">📚 Book Recommendations</h1>

      <div>
        {loadingRecommendations ? (
          <p className="italic text-sm text-gray-300">🔄 Generating your recommendations...</p>
        ) : recommendationText ? (
          <pre className="whitespace-pre-wrap">{recommendationText}</pre>
        ) : (
          <p>No recommendations yet.</p>
        )}
      </div>
    </div>
  );
}