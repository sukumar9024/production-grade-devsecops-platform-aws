import {
  createContext,
  useCallback,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { authService } from "../services/authService";
import { tokenService } from "../services/tokenService";

import type {
  LoginRequest,
  User,
} from "../types/auth";


interface AuthContextValue {
  user: User | null;
  loading: boolean;
  authenticated: boolean;

  login: (
    payload: LoginRequest
  ) => Promise<void>;

  logout: () => Promise<void>;
}


export const AuthContext =
  createContext<AuthContextValue | undefined>(
    undefined
  );


interface AuthProviderProps {
  children: ReactNode;
}


export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] =
    useState<User | null>(null);

  const [loading, setLoading] =
    useState(true);


  const restoreSession =
    useCallback(async () => {
      const refreshToken =
        tokenService.getRefreshToken();

      if (!refreshToken) {
        setLoading(false);
        return;
      }

      try {
        const tokens =
          await authService.refresh(
            refreshToken
          );

        tokenService.setAccessToken(
          tokens.access_token
        );

        if (tokens.refresh_token) {
          tokenService.setRefreshToken(
            tokens.refresh_token
          );
        }

        const currentUser =
          await authService.me();

        setUser(currentUser);
      } catch {
        tokenService.clearTokens();
        setUser(null);
      } finally {
        setLoading(false);
      }
    }, []);


  useEffect(() => {
    void restoreSession();
  }, [restoreSession]);


  async function login(
    payload: LoginRequest
  ): Promise<void> {
    const tokens =
      await authService.login(payload);

    tokenService.setAccessToken(
      tokens.access_token
    );

    tokenService.setRefreshToken(
      tokens.refresh_token
    );

    const currentUser =
      await authService.me();

    setUser(currentUser);
  }


  async function logout(): Promise<void> {
    const refreshToken =
      tokenService.getRefreshToken();

    try {
      if (refreshToken) {
        await authService.logout(
          refreshToken
        );
      }
    } finally {
      tokenService.clearTokens();
      setUser(null);
    }
  }


  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        authenticated: user !== null,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}