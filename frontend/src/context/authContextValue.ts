import { createContext } from 'react';
import type { LoginRequest, User } from '../types/auth';
interface AuthContextValue {
  user: User | null;
  loading: boolean;
  authenticated: boolean;
  login: (payload: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
}
export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
