import authClient from '../api/apiClient';
import { tokenService } from './tokenService';
import type { TokenResponse } from '../types/auth';

export const SESSION_EXPIRED_EVENT = 'secureops:session-expired';
let pendingRefresh: Promise<TokenResponse> | null = null;

export function expireSession() {
  tokenService.clearTokens();
  window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
}

export function refreshSession(): Promise<TokenResponse> {
  if (pendingRefresh) return pendingRefresh;
  const refreshToken = tokenService.getRefreshToken();
  if (!refreshToken) return Promise.reject(new Error('No active session'));
  pendingRefresh = authClient.post<TokenResponse>('/api/v1/auth/refresh', { refresh_token: refreshToken })
    .then(({ data }) => {
      // Logout or another login may have occurred while this request was in flight.
      if (tokenService.getRefreshToken() !== refreshToken) throw new Error('Session changed');
      tokenService.setAccessToken(data.access_token);
      tokenService.setRefreshToken(data.refresh_token);
      return data;
    })
    .catch(error => {
      if (tokenService.getRefreshToken() === refreshToken) expireSession();
      throw error;
    })
    .finally(() => { pendingRefresh = null; });
  return pendingRefresh;
}
