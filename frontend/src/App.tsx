import {
  Link,
  Route,
  Routes,
} from "react-router-dom";

import { AppLayout } from "./layouts/AppLayout";

import { RegisterPage } from "./pages/auth/RegisterPage";
import { LoginPage } from "./pages/auth/LoginPage";
import { UnauthorizedPage } from "./pages/auth/UnauthorizedPage";

import { DashboardPage } from "./pages/dashboard/DashboardPage";
import { ProjectsPage } from "./pages/projects/ProjectsPage";
import { ServicesPage } from "./pages/services/ServicesPage";
import { DeploymentsPage } from "./pages/deployments/DeploymentsPage";
import { IncidentsPage } from "./pages/incidents/IncidentsPage";
import { AuditLogsPage } from "./pages/audit/AuditLogsPage";

import { ProtectedRoute } from "./routes/ProtectedRoute";
import { RoleRoute } from "./routes/RoleRoute";


export default function App() {
  return (
    <Routes>
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/login"
        element={<LoginPage />}
      />

      <Route
        path="/unauthorized"
        element={<UnauthorizedPage />}
      />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route
            index
            element={<DashboardPage />}
          />

          <Route
            path="projects"
            element={<ProjectsPage />}
          />

          <Route
            path="services"
            element={<ServicesPage />}
          />

          <Route
            path="deployments"
            element={<DeploymentsPage />}
          />

          <Route
            path="incidents"
            element={<IncidentsPage />}
          />

          <Route
            element={
              <RoleRoute
                allowedRoles={[
                  "Admin",
                ]}
              />
            }
          >
            <Route
              path="audit-logs"
              element={<AuditLogsPage />}
            />
          </Route>
        </Route>
      </Route>

      <Route
        path="*"
        element={
          <main><h1>404 — Page not found</h1><Link to="/">Return to dashboard</Link></main>
        }
      />
    </Routes>
  );
}