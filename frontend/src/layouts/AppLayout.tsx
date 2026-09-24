import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
export function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  async function signOut() {
    try { await logout(); }
    catch { navigate('/login', { replace: true, state: { message: 'Signed out on this device. Server token revocation could not be confirmed.' } }); }
  }
  return <div className="app-shell"><a className="skip-link" href="#content">Skip to content</a>
    <header><strong>SecureOps</strong><div>{user?.username} — {user?.role.name} <button type="button" onClick={() => void signOut()}>Logout</button></div></header>
    <div className="app-body"><aside><nav aria-label="Main navigation">
      <NavLink to="/" end>Dashboard</NavLink><NavLink to="/projects">Projects</NavLink><NavLink to="/services">Services</NavLink><NavLink to="/deployments">Deployments</NavLink><NavLink to="/incidents">Incidents</NavLink>
      {user?.role.name === 'Admin' && <NavLink to="/audit-logs">Audit Logs</NavLink>}
    </nav></aside><main id="content"><Outlet /></main></div>
  </div>;
}
