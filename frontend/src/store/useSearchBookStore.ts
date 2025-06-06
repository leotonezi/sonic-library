// store/useSearchStore.ts
import { create } from "zustand";
import { searchExternalBooks } from "@/services/bookService";
import { ExternalBook } from "@/interfaces/book";

interface SearchState {
  searchQuery: string;
  searchResults: ExternalBook[];
  setSearchQuery: (query: string) => void;
  fetchExternalBooks: () => Promise<void>;
}

export const useSearchBookStore = create<SearchState>((set, get) => ({
  searchQuery: "",
  searchResults: [],
  setSearchQuery: (query) => set({ searchQuery: query }),
  fetchExternalBooks: async () => {
    const { searchQuery } = get(); // Use get() to access current state
    if (!searchQuery.trim()) {
      set({ searchResults: [] });
      return;
    }
    try {
      const data = await searchExternalBooks(searchQuery);
      set({ searchResults: data });
    } catch (error) {
      console.error("Error fetching external books:", error);
      set({ searchResults: [] });
    }
  },
}));
