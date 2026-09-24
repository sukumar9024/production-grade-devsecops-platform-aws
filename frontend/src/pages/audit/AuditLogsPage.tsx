import { ResourcePage } from '../../components/ResourcePage';
import { column, dateColumn, type ResourceConfig } from '../../components/resourceConfig';
const config: ResourceConfig = {
  title: 'Audit logs', singular: 'Audit log', path: '/api/v1/audit-logs',
  columns: [dateColumn('Timestamp', 'created_at'), column('Action', 'action'), column('User', 'user.username'), column('Resource', 'resource_type'), column('Resource ID', 'resource_id'), column('Request ID', 'request_id'), column('IP address', 'ip_address'), { label: 'Details', render: row => row.details ? <pre>{JSON.stringify(row.details, null, 2)}</pre> : '—' }],
};
export function AuditLogsPage() { return <ResourcePage config={config} />; }
