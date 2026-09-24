import { ResourcePage } from '../../components/ResourcePage';
import { column, dateColumn, type ResourceConfig } from '../../components/resourceConfig';
const config: ResourceConfig = {
  title: 'Incidents', singular: 'Incident', path: '/api/v1/incidents',
  columns: [column('Incident ID', 'id'), column('Title', 'title'), column('Severity', 'severity'), column('Service', 'service.name'), dateColumn('Timestamp', 'detected_at'), column('Status', 'status'), column('Description', 'description'), dateColumn('Resolved', 'resolved_at')],
  fields: [
    { name: 'service_id', label: 'Service', required: true, source: '/api/v1/services', createOnly: true },
    { name: 'title', label: 'Title', required: true, minLength: 3, maxLength: 200 },
    { name: 'description', label: 'Description', required: true, type: 'textarea', minLength: 3, maxLength: 5000 },
    { name: 'severity', label: 'Severity', required: true, options: ['low', 'medium', 'high', 'critical'] },
    { name: 'status', label: 'Status', required: true, options: ['open', 'investigating', 'resolved', 'closed'], editOnly: true },
  ],
};
export function IncidentsPage() { return <ResourcePage config={config} />; }
