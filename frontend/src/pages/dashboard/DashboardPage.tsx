import {
  useEffect,
  useState,
} from "react";

import {
  dashboardService,
  type DashboardData,
} from "../../services/dashboardService";

import { getApiErrorMessage } from "../../utils/apiError";


export function DashboardPage() {
  const [
    dashboard,
    setDashboard,
  ] = useState<DashboardData | null>(
    null
  );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  );


  useEffect(() => {
    async function loadDashboard() {
      try {
        const data =
          await dashboardService.getDashboard();

        setDashboard(data);

      } catch (err) {
        setError(
          getApiErrorMessage(err)
        );

      } finally {
        setLoading(false);
      }
    }

    void loadDashboard();
  }, []);


  if (loading) {
    return (
      <section>
        <h1>Dashboard</h1>

        <p>
          Loading dashboard...
        </p>
      </section>
    );
  }


  if (error) {
    return (
      <section>
        <h1>Dashboard</h1>

        <p role="alert">
          {error}
        </p>
      </section>
    );
  }


  if (!dashboard) {
    return null;
  }


  return (
    <section>
      <h1>Dashboard</h1>

      <div className="stats-grid">
        <article className="card">
          <h3>Total Services</h3>
          <strong>
            {dashboard.totalServices}
          </strong>
        </article>

        <article className="card">
          <h3>Healthy</h3>
          <strong>
            {dashboard.healthyServices}
          </strong>
        </article>

        <article className="card">
          <h3>Unavailable</h3>
          <strong>
            {
              dashboard
                .unavailableServices
            }
          </strong>
        </article>

        <article className="card">
          <h3>Active Incidents</h3>
          <strong>
            {
              dashboard
                .openIncidents
                .length
            }
          </strong>
        </article>
      </div>

      <section className="card table-card">
        <h2>
          Recent Deployments
        </h2>

        {dashboard
          .recentDeployments
          .length === 0 ? (
          <p>
            No deployments recorded.
          </p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Service</th>
                <th>Environment</th>
                <th>Version</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {dashboard
                .recentDeployments
                .map(
                  (deployment) => (
                    <tr
                      key={
                        deployment.id
                      }
                    >
                      <td>
                        {
                          deployment
                            .service
                            .name
                        }
                      </td>

                      <td>
                        {
                          deployment
                            .service
                            .environment
                        }
                      </td>

                      <td>
                        {
                          deployment
                            .version
                        }
                      </td>

                      <td>
                        {
                          deployment
                            .status
                        }
                      </td>
                    </tr>
                  )
                )}
            </tbody>
          </table>
        )}
      </section>

      <section className="card table-card">
        <h2>Active Incidents</h2>

        {dashboard
          .openIncidents
          .length === 0 ? (
          <p>
            No active incidents.
          </p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Service</th>
                <th>Severity</th>
                <th>Incident</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {dashboard
                .openIncidents
                .map(
                  (incident) => (
                    <tr
                      key={
                        incident.id
                      }
                    >
                      <td>
                        {
                          incident
                            .service
                            .name
                        }
                      </td>

                      <td>
                        {
                          incident
                            .severity
                        }
                      </td>

                      <td>
                        {
                          incident
                            .title
                        }
                      </td>

                      <td>
                        {
                          incident
                            .status
                        }
                      </td>
                    </tr>
                  )
                )}
            </tbody>
          </table>
        )}
      </section>
    </section>
  );
}