import { ResourcePage } from '../../components/ResourcePage';
import { column, dateColumn, type ResourceConfig } from '../../components/resourceConfig';
import { listAll } from '../../services/resourceService';
import type { Deployment } from '../../types/deployment';
const config: ResourceConfig = {
  title: 'Services', singular: 'Service', path: '/api/v1/services', deletable: true,
  columns: [column('Service name', 'name'), column('Project', 'project.name'), column('Environment', 'environment'), column('Version', 'version'), column('Health status', 'status'), dateColumn('Last deployment', 'last_deployment'), column('Health check URL', 'health_check_url')],
  fields: [
    { name: 'project_id', label: 'Project', required: true, source: '/api/v1/projects', createOnly: true },
    { name: 'name', label: 'Name', required: true, minLength: 2, maxLength: 150 },
    { name: 'environment', label: 'Environment', required: true, options: ['dev', 'staging', 'production'] },
    { name: 'version', label: 'Version', maxLength: 100 },
    { name: 'health_check_url', label: 'Health check URL', type: 'url' },
    { name: 'status', label: 'Health status', required: true, options: ['unknown', 'healthy', 'degraded', 'unavailable'], editOnly: true },
  ],
  async enrich(rows) {
    if (!rows.length) return rows;
    const deployments = await listAll<Deployment>('/api/v1/deployments');
    const latest = new Map<string, string>();
    for (const deployment of deployments) {
      if (deployment.deployed_at && (!latest.has(deployment.service.id) || new Date(deployment.deployed_at) > new Date(latest.get(deployment.service.id)!))) latest.set(deployment.service.id, deployment.deployed_at);
    }
    return rows.map(row => ({ ...row, last_deployment: latest.get(row.id) ?? null }));
  },
};
export function ServicesPage() { return <ResourcePage config={config} />; }
