import apiClient from "../api/client";

import type {
  Service,
} from "../types/service";

import type {
  Deployment,
} from "../types/deployment";

import type {
  Incident,
} from "../types/incident";


export interface DashboardData {
  totalServices: number;
  healthyServices: number;
  unavailableServices: number;
  recentDeployments: Deployment[];
  openIncidents: Incident[];
}


export const dashboardService = {
  async getDashboard():
    Promise<DashboardData> {

    const [
      servicesResponse,
      deploymentsResponse,
      incidentsResponse,
    ] = await Promise.all([
      apiClient.get<Service[]>(
        "/api/v1/services?limit=100"
      ),

      apiClient.get<Deployment[]>(
        "/api/v1/deployments?limit=5"
      ),

      apiClient.get<Incident[]>(
        "/api/v1/incidents?incident_status=open&limit=5"
      ),
    ]);

    const services =
      servicesResponse.data;

    return {
      totalServices:
        services.length,

      healthyServices:
        services.filter(
          (service) =>
            service.status === "healthy"
        ).length,

      unavailableServices:
        services.filter(
          (service) =>
            service.status
            === "unavailable"
        ).length,

      recentDeployments:
        deploymentsResponse.data,

      openIncidents:
        incidentsResponse.data,
    };
  },
};