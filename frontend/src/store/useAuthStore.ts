import { create } from "zustand";
import { AuthState } from "@/interfaces/auth";
import User from "@/interfaces/user";

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isLoading: false,
  isCheckingAuth: false,

  setUser: (user: User | null) => {
    set({ user });
  },

  logout: async () => {
    try {
      set({ isLoading: true });
      await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      set({ user: null, isLoading: false, isCheckingAuth: false });
    }
  },

  checkAuth: async () => {
    if (get().isCheckingAuth) {
      return get().user !== null;
    }

    try {
      set({ isLoading: true, isCheckingAuth: true });
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/users/me`,
        {
          credentials: 'include',
        }
      );

      if (!response.ok) {
        set({ user: null, isCheckingAuth: false });
        return false;
      }

      const userData = await response.json();
      set({ user: userData.data, isCheckingAuth: false });
      return true;
    } catch (error) {
      console.error('Auth check failed:', error);
      set({ user: null, isCheckingAuth: false });
      return false;
    } finally {
      set({ isLoading: false });
    }
  },

  isAuthenticated: () => !!get().user,
}));