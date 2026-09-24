// @vitest-environment jsdom
import { afterEach, expect, test } from 'vitest';
import apiClient from '../src/api/client';
import { dashboardService } from '../src/services/dashboardService';
const originalAdapter = apiClient.defaults.adapter;
afterEach(() => { apiClient.defaults.adapter = originalAdapter; });
test('dashboard counts beyond the first page and includes investigating incidents', async () => {
  apiClient.defaults.adapter = async config => {
    let data: unknown[] = [];
    if (config.url?.startsWith('/api/v1/services')) {
      const offset = config.params?.offset ?? 0;
      data = offset === 0 ? Array.from({ length: 100 }, (_, i) => ({ id: String(i), name: 'Service', environment: 'dev', version: null, status: 'healthy' })) : [{ id: '101', name: 'Failure', environment: 'dev', version: null, status: 'unavailable' }];
    } else if (config.url?.startsWith('/api/v1/incidents')) {
      const status = config.params?.incident_status;
      data = status === 'open' ? Array.from({ length: 7 }, (_, i) => ({ id: `open-${i}`, status: 'open' })) : status === 'investigating' ? [{ id: 'active', status: 'investigating' }] : [];
    }
    return { config, headers: {}, status: 200, statusText: 'OK', data };
  };
  const dashboard = await dashboardService.getDashboard();
  expect(dashboard.totalServices).toBe(101);
  expect(dashboard.healthyServices).toBe(100);
  expect(dashboard.unavailableServices).toBe(1);
  expect(dashboard.openIncidents).toHaveLength(8);
});
