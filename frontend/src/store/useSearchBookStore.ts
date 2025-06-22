// store/useSearchBookStore.ts
import { create } from "zustand";
import { searchExternalBooks } from "@/services/bookService";
import { ExternalBook } from "@/interfaces/book";

interface SearchState {
  searchQuery: string;
  searchResults: ExternalBook[];
  setSearchQuery: (query: string) => void;
  fetchExternalBooks: (genre?: string) => Promise<void>; // Modified
}

export const useSearchBookStore = create<SearchState>((set, get) => ({
  searchQuery: "",
  searchResults: [],
  setSearchQuery: (query) => set({ searchQuery: query }),
  fetchExternalBooks: async (genre?: string) => {
    const { searchQuery } = get(); // Use get() to access current state
    let query = searchQuery;

    if (genre) {
      query = `subject:${genre} ${searchQuery}`.trim();
    }

    if (!query.trim()) {
      set({ searchResults: [] });
      return;
    }

    try {
      const data = await searchExternalBooks(query); // Pass the modified query
      set({ searchResults: data });
    } catch (error) {
      console.error("Error fetching external books:", error);
      set({ searchResults: [] });
    }
  },
}));
