import type { ReactNode } from 'react';
export type Row = Record<string, unknown> & { id: string };
export type Field = { name: string; label: string; type?: 'textarea' | 'url' | 'datetime-local'; required?: boolean; minLength?: number; maxLength?: number; options?: string[]; source?: string; createOnly?: boolean; editOnly?: boolean };
export type Column = { label: string; render: (row: Row) => ReactNode };
export type ResourceConfig = { title: string; singular: string; path: string; columns: Column[]; fields?: Field[]; deletable?: boolean; enrich?: (rows: Row[]) => Promise<Row[]> };
export const value = (row: Row, key: string) => {
  const result = key.split('.').reduce<unknown>((object, part) => object && typeof object === 'object' ? (object as Record<string, unknown>)[part] : undefined, row);
  return result === null || result === undefined || result === '' ? '—' : String(result);
};
export const column = (label: string, key: string): Column => ({ label, render: row => value(row, key) });
export const dateColumn = (label: string, key: string): Column => ({ label, render: row => value(row, key) === '—' ? '—' : new Date(value(row, key)).toLocaleString() });
