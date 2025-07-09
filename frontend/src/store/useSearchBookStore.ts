// store/useSearchBookStore.ts
import { create } from "zustand";
import { 
  searchExternalBooks, 
  getPopularBooks, 
  searchExternalBooksLegacy, 
  getPopularBooksLegacy 
} from "@/services/bookService";
import { ExternalBook, PaginationMetadata } from "@/interfaces/book";

interface SearchState {
  searchQuery: string;
  searchResults: ExternalBook[];
  popularBooks: ExternalBook[];
  isLoading: boolean;
  hasSearched: boolean;
  searchPagination: PaginationMetadata | null;
  popularPagination: PaginationMetadata | null;
  setSearchQuery: (query: string) => void;
  fetchExternalBooks: (genre?: string) => Promise<void>;
  fetchPopularBooks: () => Promise<void>;
  fetchExternalBooksPaginated: (query: string, page?: number, maxResults?: number) => Promise<void>;
  fetchPopularBooksPaginated: (page?: number, maxResults?: number) => Promise<void>;
}

export const useSearchBookStore = create<SearchState>((set, get) => ({
  searchQuery: "",
  searchResults: [],
  popularBooks: [],
  isLoading: false,
  hasSearched: false,
  searchPagination: null,
  popularPagination: null,
  setSearchQuery: (query) => set({ searchQuery: query }),
  
  fetchPopularBooks: async () => {
    set({ isLoading: true });
    try {
      const data = await getPopularBooksLegacy();
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
      const data = await searchExternalBooksLegacy(query);
      set({ searchResults: data });
    } catch (error) {
      console.error("Error fetching external books:", error);
      set({ searchResults: [] });
    } finally {
      set({ isLoading: false });
    }
  },

  fetchExternalBooksPaginated: async (query: string, page = 1, maxResults = 10) => {
    if (!query.trim()) {
      set({ searchResults: [], searchPagination: null });
      return;
    }

    set({ isLoading: true, hasSearched: true });
    try {
      const response = await searchExternalBooks(query, page, maxResults);
      if (response) {
        set({ 
          searchResults: response.data,
          searchPagination: response.pagination 
        });
      }
    } catch (error) {
      console.error("Error fetching external books:", error);
      set({ searchResults: [], searchPagination: null });
    } finally {
      set({ isLoading: false });
    }
  },

  fetchPopularBooksPaginated: async (page = 1, maxResults = 12) => {
    set({ isLoading: true });
    try {
      const response = await getPopularBooks(page, maxResults);
      if (response) {
        set({ 
          popularBooks: response.data,
          popularPagination: response.pagination 
        });
      }
    } catch (error) {
      console.error("Error fetching popular books:", error);
      set({ popularBooks: [], popularPagination: null });
    } finally {
      set({ isLoading: false });
    }
  },
}));
