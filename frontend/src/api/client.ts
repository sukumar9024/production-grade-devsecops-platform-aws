import axios, { type InternalAxiosRequestConfig } from 'axios';
import { tokenService } from '../services/tokenService';
import { expireSession, refreshSession } from '../services/sessionService';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});
apiClient.interceptors.request.use(config => {
  const token = tokenService.getAccessToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  else delete config.headers.Authorization;
  return config;
});
apiClient.interceptors.response.use(response => response, async error => {
  const config = error.config as (InternalAxiosRequestConfig & { retried?: boolean }) | undefined;
  if (error.response?.status !== 401 || !config) throw error;
  if (config.retried || !tokenService.getRefreshToken()) {
    expireSession();
    throw error;
  }
  config.retried = true;
  const currentToken = tokenService.getAccessToken();
  // A slower response may arrive after another request already refreshed.
  if (!currentToken || config.headers.Authorization === `Bearer ${currentToken}`) await refreshSession();
  return apiClient.request(config);
});
export default apiClient;
