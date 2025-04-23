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
  user: AuthResponse["user"] | null;
  accessToken: string | null;
  refreshToken: string | null;
  setAuth: (response: AuthResponse) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}