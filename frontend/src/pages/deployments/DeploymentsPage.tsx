import { ResourcePage } from '../../components/ResourcePage';
import { column, dateColumn, type ResourceConfig } from '../../components/resourceConfig';
const config: ResourceConfig = {
  title: 'Deployments', singular: 'Deployment', path: '/api/v1/deployments',
  columns: [column('Deployment ID', 'id'), column('Service', 'service.name'), column('Application version', 'version'), column('Git commit', 'git_commit'), column('Environment', 'service.environment'), dateColumn('Deployment time', 'deployed_at'), column('Status', 'status'), column('Failure reason', 'failure_reason')],
  fields: [
    { name: 'service_id', label: 'Service', required: true, source: '/api/v1/services', createOnly: true },
    { name: 'version', label: 'Application version', required: true, maxLength: 100, createOnly: true },
    { name: 'git_commit', label: 'Git commit', required: true, minLength: 7, maxLength: 64, createOnly: true },
    { name: 'image_digest', label: 'Image digest', maxLength: 255 },
    { name: 'pipeline_id', label: 'Pipeline ID', maxLength: 100 },
    { name: 'status', label: 'Status', required: true, options: ['pending', 'in_progress', 'success', 'failed', 'rolled_back'], editOnly: true },
    { name: 'deployed_at', label: 'Deployment time', type: 'datetime-local', editOnly: true },
    { name: 'failure_reason', label: 'Failure reason', type: 'textarea', maxLength: 5000, editOnly: true },
  ],
};
export function DeploymentsPage() { return <ResourcePage config={config} />; }
