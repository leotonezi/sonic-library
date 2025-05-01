import { create } from "zustand";
import { persist } from "zustand/middleware";
import { AuthState } from "@/types/auth";

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,

      setAuth: ({ access_token, refresh_token, user }) => {
        set({
          user: user ?? null,
          accessToken: access_token,
          refreshToken: refresh_token ?? null,
        });
      },

      logout: () => {
        set({ user: null, accessToken: null, refreshToken: null });
      },

      isAuthenticated: () => !!get().accessToken,
    }),
    {
      name: "auth-storage", // localStorage key
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    }
  )
);