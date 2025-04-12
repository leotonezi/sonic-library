'use client';

import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setUser } from "@/redux/userSlice";
import { RootState } from "@/redux/store";
import { apiFetch } from "@/utils/api";

export default function RecommendationPage() {
  const dispatch = useDispatch();
  const user = useSelector((state: RootState) => state.user);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const [recommendationText, setRecommendationText] = useState<string>("");

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      const userData = await apiFetch<{ id: number; email: string }>("/users/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        noCache: true,
      });

      if (userData) {
        dispatch(setUser(userData));
      }
    };

    fetchUser();
  }, [dispatch]);

  useEffect(() => {
    const fetchRecommendations = async () => {
      const token = localStorage.getItem("access_token");
      if (!token || !user.id) return;
  
      setLoadingRecommendations(true);
  
      try {
        const rec = await apiFetch<string>(`/recommendations/${user.id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
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
  
    if (user.id) {
      fetchRecommendations();
    }
  }, [user.id]);

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