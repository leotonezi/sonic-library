import User from "./user";

export interface ApiResponse<T> {
  message: string;
  status: string;
  data?: T | null;
  error?: string;
}

export interface AuthResponse {
  access_token: string; // The access token for authentication
  refresh_token?: string; // Optional refresh token
  user?: {
    id: number; // User ID
    email: string; // User email
    name?: string; // Optional user name
  };
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isCheckingAuth: boolean;
  setUser: (user: User | null) => void;
  logout: () => Promise<void>;
  checkAuth: () => Promise<boolean>;
  isAuthenticated: () => boolean;
}