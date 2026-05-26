import { User } from './user';

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  user?: {
    id: number;
    email: string;
    name?: string;
  };
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isCheckingAuth: boolean;
  hasHydrated: boolean;
  setUser: (user: User | null) => void;
  logout: () => Promise<void>;
  checkAuth: () => Promise<boolean>;
  isAuthenticated: () => boolean;
}
