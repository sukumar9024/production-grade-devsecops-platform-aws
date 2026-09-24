import apiClient from '../api/client';
import { listAll } from './resourceService';
import type { Service } from '../types/service';
import type { Deployment } from '../types/deployment';
import type { Incident } from '../types/incident';

export interface DashboardData {
  totalServices: number;
  healthyServices: number;
  unavailableServices: number;
  recentDeployments: Deployment[];
  openIncidents: Incident[];
}
export const dashboardService = {
  async getDashboard(): Promise<DashboardData> {
    const [services, deployments, open, investigating] = await Promise.all([
      listAll<Service>('/api/v1/services'),
      apiClient.get<Deployment[]>('/api/v1/deployments', { params: { limit: 5 } }),
      listAll<Incident>('/api/v1/incidents', { incident_status: 'open' }),
      listAll<Incident>('/api/v1/incidents', { incident_status: 'investigating' }),
    ]);
    return {
      totalServices: services.length,
      healthyServices: services.filter(service => service.status === 'healthy').length,
      unavailableServices: services.filter(service => service.status === 'unavailable').length,
      recentDeployments: deployments.data,
      openIncidents: [...open, ...investigating].sort((a, b) => new Date(b.detected_at).getTime() - new Date(a.detected_at).getTime()),
    };
  },
};
