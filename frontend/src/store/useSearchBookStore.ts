// store/useSearchBookStore.ts
import { create } from "zustand";
import { searchExternalBooks, getPopularBooks } from "@/services/bookService";
import { ExternalBook } from "@/interfaces/book";

interface SearchState {
  searchQuery: string;
  searchResults: ExternalBook[];
  popularBooks: ExternalBook[];
  isLoading: boolean;
  hasSearched: boolean;
  setSearchQuery: (query: string) => void;
  fetchExternalBooks: (genre?: string) => Promise<void>;
  fetchPopularBooks: () => Promise<void>;
}

export const useSearchBookStore = create<SearchState>((set, get) => ({
  searchQuery: "",
  searchResults: [],
  popularBooks: [],
  isLoading: false,
  hasSearched: false,
  setSearchQuery: (query) => set({ searchQuery: query }),
  
  fetchPopularBooks: async () => {
    set({ isLoading: true });
    try {
      const data = await getPopularBooks();
      set({ popularBooks: data });
    } catch (error) {
      console.error("Error fetching popular books:", error);
      set({ popularBooks: [] });
    } finally {
      set({ isLoading: false });
    }
  },

  fetchExternalBooks: async (genre?: string) => {
    const { searchQuery } = get();
    let query = searchQuery;

    if (genre) {
      query = `subject:${genre} ${searchQuery}`.trim();
    }

    if (!query.trim()) {
      set({ searchResults: [] });
      return;
    }

    set({ isLoading: true, hasSearched: true });
    try {
      const data = await searchExternalBooks(query);
      set({ searchResults: data });
    } catch (error) {
      console.error("Error fetching external books:", error);
      set({ searchResults: [] });
    } finally {
      set({ isLoading: false });
    }
  },
}));
