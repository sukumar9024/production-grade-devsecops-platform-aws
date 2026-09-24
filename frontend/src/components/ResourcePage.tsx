import { useCallback, useEffect, useState, type FormEvent } from 'react';
import apiClient from '../api/client';
import { useAuth } from '../hooks/useAuth';
import { getApiErrorMessage } from '../utils/apiError';
import { listAll } from '../services/resourceService';

import { value, type Row, type ResourceConfig } from './resourceConfig';

export function ResourcePage({ config }: { config: ResourceConfig }) {
  const { user } = useAuth();
  const canModify = !!config.fields && ['Admin', 'Engineer'].includes(user?.role.name ?? '');
  const canDelete = config.deletable && user?.role.name === 'Admin';
  const [rows, setRows] = useState<Row[]>([]);
  const [references, setReferences] = useState<Record<string, Row[]>>({});
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState<Row | null>(null);
  const [form, setForm] = useState<Record<string, string>>({});
  const fields = config.fields?.filter(field => editing ? !field.createOnly : !field.editOnly) ?? [];

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiClient.get<Row[]>(config.path, { params: { offset, limit: 20 } });
      setRows(config.enrich ? await config.enrich(response.data) : response.data);
    } finally { setLoading(false); }
  }, [config, offset]);
  useEffect(() => { void Promise.resolve().then(load).catch(error => setError(getApiErrorMessage(error))); }, [load]);
  useEffect(() => {
    if (!canModify) return;
    let active = true;
    const sources = [...new Set(config.fields?.flatMap(field => field.source ? [field.source] : []))];
    void Promise.all(sources.map(async source => [source, await listAll<Row>(source)] as const))
      .then(entries => { if (active) setReferences(Object.fromEntries(entries)); })
      .catch(error => { if (active) setError(getApiErrorMessage(error)); });
    return () => { active = false; };
  }, [config, canModify]);

  function beginEdit(row: Row) {
    const values: Record<string, string> = {};
    for (const field of config.fields ?? []) {
      const raw = row[field.name];
      values[field.name] = raw == null ? '' : String(raw);
      if (field.type === 'datetime-local' && raw) {
        const date = new Date(String(raw));
        values[field.name] = new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
      }
    }
    setEditing(row); setForm(values); setError(null);
  }
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!canModify || busy) return;
    setBusy(true); setError(null);
    try {
      const payload = Object.fromEntries(fields.map(field => {
        const input = (form[field.name] ?? '').trim();
        return [field.name, field.type === 'datetime-local' && input ? new Date(input).toISOString() : input || null];
      }));
      if (editing) await apiClient.patch(`${config.path}/${editing.id}`, payload);
      else await apiClient.post(config.path, payload);
      setEditing(null); setForm({});
      await load();
    } catch (error) { setError(getApiErrorMessage(error)); }
    finally { setBusy(false); }
  }
  async function remove(row: Row) {
    if (!canDelete || busy || !window.confirm(`Delete ${config.singular.toLowerCase()} "${value(row, 'name')}"?`)) return;
    setBusy(true); setError(null);
    try {
      await apiClient.delete(`${config.path}/${row.id}`);
      if (rows.length === 1 && offset > 0) setOffset(offset - 20);
      else await load();
    } catch (error) { setError(getApiErrorMessage(error)); }
    finally { setBusy(false); }
  }

  return <section>
    <div className="page-header"><div><h1>{config.title}</h1><p>SecureOps operational inventory</p></div><button disabled={loading || busy} onClick={() => { setError(null); void load().catch(error => setError(getApiErrorMessage(error))); }}>Refresh</button></div>
    {error && <p className="error-message" role="alert">{error}</p>}
    {canModify && <section className="card"><h2>{editing ? `Edit ${config.singular.toLowerCase()}` : `Create ${config.singular.toLowerCase()}`}</h2>
      <form className="form-grid" onSubmit={event => void submit(event)}>
        {fields.map(field => <div key={field.name}><label htmlFor={field.name}>{field.label}</label>
          {field.options || field.source ? <select id={field.name} required={field.required} value={form[field.name] ?? ''} onChange={event => setForm({ ...form, [field.name]: event.target.value })}>
            <option value="">Select {field.label.toLowerCase()}</option>
            {field.options?.map(option => <option key={option} value={option}>{option}</option>)}
            {field.source && (references[field.source] ?? []).map(row => <option key={row.id} value={row.id}>{value(row, 'name')}{row.environment ? ` (${row.environment})` : ''}</option>)}
          </select> : field.type === 'textarea' ? <textarea id={field.name} required={field.required} minLength={field.minLength} maxLength={field.maxLength} value={form[field.name] ?? ''} onChange={event => setForm({ ...form, [field.name]: event.target.value })} /> :
          <input id={field.name} type={field.type ?? 'text'} required={field.required} minLength={field.minLength} maxLength={field.maxLength} value={form[field.name] ?? ''} onChange={event => setForm({ ...form, [field.name]: event.target.value })} />}
        </div>)}
        <div className="actions"><button type="submit" disabled={busy}>{busy ? 'Saving…' : editing ? 'Save changes' : `Create ${config.singular.toLowerCase()}`}</button>{editing && <button type="button" disabled={busy} onClick={() => { setEditing(null); setForm({}); }}>Cancel</button>}</div>
      </form>
    </section>}
    <section className="card table-card" aria-busy={loading}>
      {loading ? <p>Loading {config.title.toLowerCase()}…</p> : rows.length === 0 ? <p>No {config.title.toLowerCase()} found.</p> : <table><thead><tr>{config.columns.map(column => <th key={column.label} scope="col">{column.label}</th>)}{canModify && <th scope="col">Actions</th>}</tr></thead><tbody>{rows.map(row => <tr key={row.id}>{config.columns.map(column => <td key={column.label}>{column.render(row)}</td>)}{canModify && <td><div className="actions"><button disabled={busy} onClick={() => beginEdit(row)}>Edit</button>{canDelete && <button disabled={busy} onClick={() => void remove(row)}>Delete</button>}</div></td>}</tr>)}</tbody></table>}
      <div className="pagination"><button disabled={loading || offset === 0} onClick={() => setOffset(offset - 20)}>Previous</button><span>Page {offset / 20 + 1}</span><button disabled={loading || rows.length < 20} onClick={() => setOffset(offset + 20)}>Next</button></div>
    </section>
  </section>;
}
