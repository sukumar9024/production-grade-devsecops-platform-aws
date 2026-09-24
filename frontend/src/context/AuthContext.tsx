import { useEffect, useState, type ReactNode } from 'react';
import { authService } from '../services/authService';
import { tokenService } from '../services/tokenService';
import { refreshSession, SESSION_EXPIRED_EVENT } from '../services/sessionService';
import type { LoginRequest, User } from '../types/auth';

import { AuthContext } from './authContextValue';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    const expired = () => setUser(null);
    window.addEventListener(SESSION_EXPIRED_EVENT, expired);
    async function restore() {
      try {
        if (tokenService.getRefreshToken()) {
          await refreshSession();
          const currentUser = await authService.me();
          if (active) setUser(currentUser);
        }
      } catch {
        if (active) setUser(null);
      } finally {
        if (active) setLoading(false);
      }
    }
    void restore();
    return () => { active = false; window.removeEventListener(SESSION_EXPIRED_EVENT, expired); };
  }, []);

  async function login(payload: LoginRequest) {
    const tokens = await authService.login(payload);
    tokenService.setAccessToken(tokens.access_token);
    tokenService.setRefreshToken(tokens.refresh_token);
    try { setUser(await authService.me()); }
    catch (error) { tokenService.clearTokens(); setUser(null); throw error; }
  }
  async function logout() {
    const refreshToken = tokenService.getRefreshToken();
    tokenService.clearTokens();
    setUser(null);
    if (refreshToken) await authService.logout(refreshToken);
  }
  return <AuthContext.Provider value={{ user, loading, authenticated: user !== null, login, logout }}>{children}</AuthContext.Provider>;
}
