import authClient from "../api/apiClient";
import apiClient from "../api/client";

import type {
  LoginRequest,
  TokenResponse,
  User,
} from "../types/auth";


export const authService = {
  async register(payload: { email: string; username: string; full_name: string | null; password: string }): Promise<User> {
    return (await authClient.post<User>("/api/v1/auth/register", payload)).data;
  },
  async login(
    payload: LoginRequest
  ): Promise<TokenResponse> {
    const response =
      await authClient.post<TokenResponse>(
        "/api/v1/auth/login",
        payload
      );

    return response.data;
  },

  async me(): Promise<User> {
    const response =
      await apiClient.get<User>(
        "/api/v1/auth/me"
      );

    return response.data;
  },

  async refresh(
    refreshToken: string
  ): Promise<TokenResponse> {
    const response =
      await authClient.post<TokenResponse>(
        "/api/v1/auth/refresh",
        {
          refresh_token: refreshToken,
        }
      );

    return response.data;
  },

  async logout(
    refreshToken: string
  ): Promise<void> {
    await authClient.post(
      "/api/v1/auth/logout",
      {
        refresh_token: refreshToken,
      }
    );
  },
};