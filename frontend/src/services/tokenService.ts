const REFRESH_TOKEN_KEY =
  "secureops_refresh_token";

let accessToken: string | null = null;

export const tokenService = {
  getAccessToken(): string | null {
    return accessToken;
  },

  setAccessToken(token: string): void {
    accessToken = token;
  },

  clearAccessToken(): void {
    accessToken = null;
  },

  getRefreshToken(): string | null {
    return localStorage.getItem(
      REFRESH_TOKEN_KEY
    );
  },

  setRefreshToken(token: string): void {
    localStorage.setItem(
      REFRESH_TOKEN_KEY,
      token
    );
  },

  clearRefreshToken(): void {
    localStorage.removeItem(
      REFRESH_TOKEN_KEY
    );
  },

  clearTokens(): void {
    accessToken = null;
    localStorage.removeItem(
      REFRESH_TOKEN_KEY
    );
  },
};