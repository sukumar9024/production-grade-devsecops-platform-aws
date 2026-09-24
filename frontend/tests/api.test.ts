// @vitest-environment jsdom
import { beforeEach, afterEach, expect, test } from 'vitest';
import { AxiosError, type AxiosAdapter, type InternalAxiosRequestConfig } from 'axios';
import apiClient from '../src/api/client';
import authClient from '../src/api/apiClient';
import { tokenService } from '../src/services/tokenService';
import { getApiErrorMessage } from '../src/utils/apiError';

const apiAdapter = apiClient.defaults.adapter;
const authAdapter = authClient.defaults.adapter;
const unauthorized = (config: InternalAxiosRequestConfig) => new AxiosError('Expired', 'ERR_BAD_REQUEST', config, undefined, { status: 401, statusText: 'Unauthorized', headers: {}, config, data: { detail: 'Expired' } });
beforeEach(() => { localStorage.clear(); tokenService.clearTokens(); });
afterEach(() => { apiClient.defaults.adapter = apiAdapter; authClient.defaults.adapter = authAdapter; });

test('concurrent expired requests share one rotation and replay with the new token', async () => {
  tokenService.setAccessToken('expired'); tokenService.setRefreshToken('refresh-old');
  let rotations = 0;
  authClient.defaults.adapter = async config => {
    rotations++;
    await new Promise(resolve => setTimeout(resolve, 10));
    return { config, headers: {}, status: 200, statusText: 'OK', data: { access_token: 'fresh', refresh_token: 'refresh-new', token_type: 'bearer' } };
  };
  apiClient.defaults.adapter = (async config => {
    if (config.headers.Authorization !== 'Bearer fresh') throw unauthorized(config);
    return { config, headers: {}, status: 200, statusText: 'OK', data: { visible: true } };
  }) satisfies AxiosAdapter;
  const responses = await Promise.all([apiClient.get('/a'), apiClient.get('/b')]);
  expect(responses.map(response => response.data)).toEqual([{ visible: true }, { visible: true }]);
  expect(rotations).toBe(1);
  expect(tokenService.getRefreshToken()).toBe('refresh-new');
});

test('rejected refresh clears the session and does not loop', async () => {
  tokenService.setAccessToken('expired'); tokenService.setRefreshToken('revoked');
  let rotations = 0;
  apiClient.defaults.adapter = async config => { throw unauthorized(config); };
  authClient.defaults.adapter = async config => { rotations++; throw unauthorized(config); };
  await expect(apiClient.get('/a')).rejects.toBeDefined();
  expect(rotations).toBe(1);
  expect(tokenService.getAccessToken()).toBeNull();
  expect(tokenService.getRefreshToken()).toBeNull();
});

test('validation errors expose field names without rendering response objects', () => {
  const error = { isAxiosError: true, response: { status: 422, data: { detail: [{ loc: ['body', 'name'], msg: 'String should have at least 3 characters' }] } } };
  expect(getApiErrorMessage(error)).toContain('name');
  expect(getApiErrorMessage(error)).toContain('at least 3');
});
