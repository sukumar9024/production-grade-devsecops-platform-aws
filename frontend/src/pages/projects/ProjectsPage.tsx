import { ResourcePage } from '../../components/ResourcePage';
import { column, dateColumn, type ResourceConfig } from '../../components/resourceConfig';
const config: ResourceConfig = {
  title: 'Projects', singular: 'Project', path: '/api/v1/projects', deletable: true,
  columns: [column('Name', 'name'), column('Description', 'description'), column('Created by', 'created_by.username'), dateColumn('Created', 'created_at')],
  fields: [{ name: 'name', label: 'Name', required: true, minLength: 3, maxLength: 150 }, { name: 'description', label: 'Description', type: 'textarea', maxLength: 2000 }],
};
export function ProjectsPage() { return <ResourcePage config={config} />; }
