import { useState, type FormEvent } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { authService } from '../../services/authService';
import { getApiErrorMessage } from '../../utils/apiError';

export function RegisterPage() {
  const { authenticated } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  if (authenticated) return <Navigate to="/" replace />;
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setError(null); setBusy(true);
    try {
      await authService.register({ email: String(data.get('email')), username: String(data.get('username')), full_name: String(data.get('full_name')) || null, password: String(data.get('password')) });
      navigate('/login', { state: { message: 'Account created. Sign in to continue.' }, replace: true });
    } catch (error) { setError(getApiErrorMessage(error)); }
    finally { setBusy(false); }
  }
  return <main className="auth-page"><section className="card"><h1>SecureOps</h1><h2>Create account</h2><p>New accounts receive Viewer access. An administrator can update your role.</p>
    <form className="form-grid" onSubmit={event => void submit(event)}>
      <div><label htmlFor="email">Email</label><input id="email" name="email" type="email" autoComplete="email" required maxLength={320} /></div>
      <div><label htmlFor="username">Username</label><input id="username" name="username" autoComplete="username" required minLength={3} maxLength={100} pattern="[a-zA-Z0-9_.\\-]+" /></div>
      <div><label htmlFor="full_name">Full name</label><input id="full_name" name="full_name" autoComplete="name" maxLength={255} /></div>
      <div><label htmlFor="new-password">Password</label><input id="new-password" name="password" type="password" autoComplete="new-password" required minLength={12} maxLength={128} /><small>At least 12 characters.</small></div>
      {error && <p className="error-message" role="alert">{error}</p>}
      <button disabled={busy} type="submit">{busy ? 'Creating account…' : 'Create account'}</button>
    </form><p><Link to="/login">Sign in</Link></p>
  </section></main>;
}
