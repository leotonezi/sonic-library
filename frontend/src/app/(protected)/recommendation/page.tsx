'use client';

import { useEffect, useState } from "react";
import { apiFetch } from "@/utils/api";
import { useAuthStore } from "@/store/useAuthStore";
import Link from "next/link";
import BookRecommendationGraph from '@/components/features/BookRecommendationGraph';

interface BookRecommendation {
  external_id: string;
  title: string;
  authors: string[];
  description: string;
  reasoning: string;
}

export default function RecommendationPage() {
  const user = useAuthStore((state) => state.user);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const [recommendationText, setRecommendationText] = useState<string>("");
  const [parsedRecommendations, setParsedRecommendations] = useState<BookRecommendation[]>([]);

  const parseRecommendations = (text: string): BookRecommendation[] => {
    const recommendations: BookRecommendation[] = [];
    
    // Simple parsing logic - this could be enhanced based on actual LLM output format
    const lines = text.split('\n').filter(line => line.trim());
    let currentBook: Partial<BookRecommendation> = {};
    let reasoning = '';
    
    for (const line of lines) {
      // Look for external_id pattern - Google Books IDs can contain hyphens, underscores, letters, numbers
      const idMatch = line.match(/ID:\s*([A-Za-z0-9_-]+)/i) || 
                     line.match(/external_id:\s*([A-Za-z0-9_-]+)/i) ||
                     line.match(/Book ID:\s*([A-Za-z0-9_-]+)/i);
      if (idMatch) {
        if (currentBook.external_id && currentBook.title) {
          recommendations.push({
            ...currentBook,
            reasoning: reasoning.trim()
          } as BookRecommendation);
        }
        currentBook = { external_id: idMatch[1] };
        reasoning = '';
      }
      
      // Look for title
      const titleMatch = line.match(/Title:\s*(.+)/i) || line.match(/^\d+\.\s*"?([^"]+)"?\s*by/i);
      if (titleMatch) {
        currentBook.title = titleMatch[1].replace(/"/g, '').trim();
      }
      
      // Look for authors
      const authorMatch = line.match(/Author[s]?:\s*(.+)/i) || line.match(/by\s+(.+)/i);
      if (authorMatch) {
        currentBook.authors = authorMatch[1].split(',').map(a => a.trim());
      }
      
      // Look for description
      const descMatch = line.match(/Description:\s*(.+)/i);
      if (descMatch) {
        currentBook.description = descMatch[1];
      }
      
      // Look for reasoning
      const reasonMatch = line.match(/Why recommended:\s*(.+)/i);
      if (reasonMatch) {
        reasoning = reasonMatch[1];
      }
      
      // Collect reasoning text (fallback)
      if (!line.match(/(ID|Title|Author|Description|Why recommended):/i) && line.trim() && !line.match(/^\d+\./) && reasoning.length < 50) {
        reasoning += line + ' ';
      }
    }
    
    // Add the last book
    if (currentBook.external_id && currentBook.title) {
      recommendations.push({
        ...currentBook,
        reasoning: reasoning.trim()
      } as BookRecommendation);
    }
    
    return recommendations;
  };

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!user) return;

      setLoadingRecommendations(true);

      try {
        const rec = await apiFetch<string>(`/recommendations`, {
          noCache: true,
        });

        if (rec) {
          const cleanText = rec
            .replace(/[*_~`>#-]/g, '')
            .replace(/$begin:math:display$(.*?)$end:math:display$$begin:math:text$.*?$end:math:text$/g, '$1')
            .replace(/\n{2,}/g, '\n\n');
          setRecommendationText(cleanText);
          
          // Try to parse structured recommendations
          const parsed = parseRecommendations(cleanText);
          setParsedRecommendations(parsed);
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
    <div className="max-w-4xl mx-auto mt-10 p-8">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
          📚 Your Personal Book Recommendations
        </h1>
        <p className="text-gray-300 text-lg">Curated just for you based on your reading preferences</p>
      </div>

      <div>
        {loadingRecommendations ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-gray-600 text-lg">🔄 Generating your personalized recommendations...</p>
          </div>
        ) : parsedRecommendations.length > 0 ? (
          <div className="grid gap-6">
            {parsedRecommendations.map((book, index) => (
              <div key={`${book.external_id}-${index}`} className="bg-blue-900 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 p-6 border border-blue-600 text-white">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                      {index + 1}
                    </div>
                  </div>
                  
                  <div className="flex-grow">
                    <div className="mb-3">
                      {book.external_id ? (
                        <Link 
                          href={`/books/external/${book.external_id}`}
                          className="text-2xl font-bold text-white hover:text-blue-300 transition-colors duration-200 block"
                        >
                          {book.title}
                        </Link>
                      ) : (
                        <h3 className="text-2xl font-bold text-white">{book.title}</h3>
                      )}
                      
                      {book.authors && book.authors.length > 0 && (
                        <p className="text-blue-200 text-lg mt-1">
                          by {book.authors.join(', ')}
                        </p>
                      )}
                    </div>
                    
                    {book.description && (
                      <p className="text-blue-100 mb-3 leading-relaxed">
                        {book.description}
                      </p>
                    )}
                    
                    {book.reasoning && (
                      <div className="bg-blue-800 rounded-lg p-4 border-l-4 border-blue-400">
                        <p className="text-sm font-semibold text-blue-200 mb-1">Why we recommend this:</p>
                        <p className="text-blue-100 text-sm leading-relaxed">{book.reasoning}</p>
                      </div>
                    )}
                    
                    {book.external_id && (
                      <div className="mt-4">
                        <Link 
                          href={`/books/external/${book.external_id}`}
                          className="inline-flex items-center px-4 py-2 bg-blue-700 text-white rounded-lg hover:bg-blue-600 transition-colors duration-200 text-sm font-medium"
                        >
                          View Book Details →
                        </Link>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : recommendationText ? (
          <div className="bg-blue-900 rounded-xl shadow-lg p-8 border border-blue-600 text-white">
            <h3 className="text-xl font-semibold text-white mb-4">Your Recommendations</h3>
            <div className="prose prose-gray max-w-none">
              <pre className="whitespace-pre-wrap text-blue-100 leading-relaxed">{recommendationText}</pre>
            </div>
          </div>
        ) : (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">📖</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No recommendations yet</h3>
            <p className="text-gray-600">Start by reviewing some books you have read to get personalized recommendations!</p>
            <Link 
              href="/books"
              className="inline-block mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium"
            >
              Browse Books
            </Link>
          </div>
        )}
      </div>
      <div className="flex items-center gap-3 mb-4 mt-12">
        <h2 className="text-2xl font-bold">Visual Book Recommendation Graph</h2>
        <span className="bg-[#fa8537] text-white text-xs font-semibold px-2 py-1 rounded-full">
          Beta
        </span>
      </div>
      <BookRecommendationGraph />
    </div>
  );
}