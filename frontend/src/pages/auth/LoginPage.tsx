import { useState, type FormEvent } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { getApiErrorMessage } from '../../utils/apiError';

export function LoginPage() {
  const { authenticated, loading, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const message: unknown = location.state?.message;
  if (loading) return <main>Restoring session…</main>;
  if (authenticated) return <Navigate to="/" replace />;
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setError(null); setBusy(true);
    try {
      await login({ identity: String(data.get('identity')), password: String(data.get('password')) });
      navigate('/', { replace: true });
    } catch (error) { setError(getApiErrorMessage(error)); }
    finally { setBusy(false); }
  }
  return <main className="auth-page"><section className="card"><h1>SecureOps</h1><h2>Sign in</h2>
    {typeof message === 'string' && <p role="status">{message}</p>}
    <form className="form-grid" onSubmit={event => void submit(event)}>
      <div><label htmlFor="identity">Email or username</label><input id="identity" name="identity" autoComplete="username" required maxLength={320} /></div>
      <div><label htmlFor="password">Password</label><input id="password" name="password" type="password" autoComplete="current-password" required maxLength={128} /></div>
      {error && <p className="error-message" role="alert">{error}</p>}
      <button disabled={busy} type="submit">{busy ? 'Signing in…' : 'Sign in'}</button>
    </form><p><Link to="/register">Create an account</Link></p>
  </section></main>;
}
