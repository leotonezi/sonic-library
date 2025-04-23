// store/useAuthStore.ts
import { create } from "zustand";
import { AuthState } from "@/types/auth";

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: null,
  refreshToken: null,

  setAuth: ({ access_token, refresh_token, user }) => {
    localStorage.setItem("access_token", access_token);
    if (refresh_token) localStorage.setItem("refresh_token", refresh_token);

    set({
      user: user ?? null,
      accessToken: access_token,
      refreshToken: refresh_token ?? null,
    });
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null, accessToken: null, refreshToken: null });
  },

  isAuthenticated: () => !!get().accessToken,
}));