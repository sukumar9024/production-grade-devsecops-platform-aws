import {
  NavLink,
  Outlet,
} from "react-router-dom";

import { useAuth } from "../hooks/useAuth";


export function AppLayout() {
  const {
    user,
    logout,
  } = useAuth();


  return (
    <div>
      <header>
        <strong>
          SecureOps
        </strong>

        <div>
          {user?.username}

          {" — "}

          {user?.role.name}

          <button
            type="button"
            onClick={() => {
              void logout();
            }}
          >
            Logout
          </button>
        </div>
      </header>

      <div>
        <aside>
          <nav>
            <NavLink to="/">
              Dashboard
            </NavLink>

            <NavLink to="/projects">
              Projects
            </NavLink>

            <NavLink to="/services">
              Services
            </NavLink>

            <NavLink to="/deployments">
              Deployments
            </NavLink>

            <NavLink to="/incidents">
              Incidents
            </NavLink>

            {user?.role.name ===
              "Admin" && (
              <NavLink to="/audit-logs">
                Audit Logs
              </NavLink>
            )}
          </nav>
        </aside>

        <main>
          <Outlet />
        </main>
      </div>
    </div>
  );
}