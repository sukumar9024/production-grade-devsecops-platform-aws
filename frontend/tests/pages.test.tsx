// @vitest-environment jsdom
import { afterEach, beforeEach, expect, test } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../src/App';
import { AuthContext } from '../src/context/authContextValue';
import apiClient from '../src/api/client';
import type { User } from '../src/types/auth';

const originalAdapter = apiClient.defaults.adapter;
const project = { id: 'p1', name: 'Platform', description: 'Operations', created_by: { id: 'u1', username: 'operator', full_name: null }, created_at: '2026-09-20T10:00:00Z', updated_at: '2026-09-20T10:00:00Z' };
const service = { id: 's1', name: 'Orders', project: { id: 'p1', name: 'Platform' }, environment: 'production', version: '1.0.0', status: 'healthy', health_check_url: null, created_at: '2026-09-20T10:00:00Z', updated_at: '2026-09-20T10:00:00Z' };
const deployment = { id: 'd1', version: '1.0.0', git_commit: 'abcd1234', status: 'success', service: { id: 's1', name: 'Orders', environment: 'production' }, deployed_at: '2026-09-21T10:00:00Z', created_at: '2026-09-21T09:00:00Z', updated_at: '2026-09-21T10:00:00Z', image_digest: null, pipeline_id: null, failure_reason: null };
let writes: { method: string | undefined; url: string | undefined; data: unknown }[];
beforeEach(() => {
  writes = [];
  apiClient.defaults.adapter = async config => {
    if (config.method !== 'get') writes.push({ method: config.method, url: config.url, data: JSON.parse(config.data) });
    const data = config.method !== 'get' ? { ...project, ...JSON.parse(config.data) } : config.url?.includes('/projects') ? [project] : config.url?.includes('/services') ? [service] : config.url?.includes('/deployments') ? [deployment] : [];
    return { config, headers: {}, status: 200, statusText: 'OK', data };
  };
});
afterEach(() => { cleanup(); apiClient.defaults.adapter = originalAdapter; });
function show(path: string, role: 'Admin' | 'Engineer' | 'Viewer' | null) {
  const user = role ? { id: 'u1', username: 'operator', email: 'operator@example.com', full_name: null, status: 'active', is_verified: true, role: { id: 'r1', name: role }, created_at: '', updated_at: '' } as User : null;
  return render(<MemoryRouter initialEntries={[path]}><AuthContext.Provider value={{ user, loading: false, authenticated: !!user, login: async () => {}, logout: async () => {} }}><App /></AuthContext.Provider></MemoryRouter>);
}
test('service readers can inspect health and last deployment without mutation controls', async () => {
  show('/services', 'Viewer');
  expect(await screen.findByText('Orders')).toBeDefined();
  expect(screen.getByRole('columnheader', { name: 'Last deployment' })).toBeDefined();
  expect(screen.getByText('healthy')).toBeDefined();
  expect(screen.queryByRole('button', { name: /create/i })).toBeNull();
  expect(screen.queryByRole('button', { name: /edit/i })).toBeNull();
});
test('engineer can edit a project with PATCH rather than creating a duplicate', async () => {
  show('/projects', 'Engineer');
  fireEvent.click(await screen.findByRole('button', { name: 'Edit' }));
  fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Updated Platform' } });
  fireEvent.click(screen.getByRole('button', { name: 'Save changes' }));
  await waitFor(() => expect(writes).toEqual([{ method: 'patch', url: '/api/v1/projects/p1', data: { name: 'Updated Platform', description: 'Operations' } }]));
  expect(screen.queryByRole('button', { name: 'Delete' })).toBeNull();
});
test('viewer cannot open the administrator audit route', async () => {
  show('/audit-logs', 'Viewer');
  expect(await screen.findByRole('heading', { name: 'Unauthorized' })).toBeDefined();
});
test('unauthenticated visitors are redirected to login', async () => {
  show('/services', null);
  expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeDefined();
});
test('registration form accepts account details without exposing a role selector', () => {
  show('/register', null);
  expect(screen.getByLabelText('Email')).toBeDefined();
  expect(screen.getByLabelText('Username')).toBeDefined();
  expect(screen.queryByLabelText('Role')).toBeNull();
});
