import apiClient from '../api/client';

// The API caps list requests at 100; aggregate explicitly when totals are needed.
export async function listAll<T>(path: string, params: Record<string, string> = {}): Promise<T[]> {
  const items: T[] = [];
  for (let offset = 0; ; offset += 100) {
    const { data } = await apiClient.get<T[]>(path, { params: { ...params, limit: 100, offset } });
    items.push(...data);
    if (data.length < 100) return items;
  }
}
