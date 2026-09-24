export interface ProjectCreator {
  id: string;
  username: string;
  full_name: string | null;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  created_by: ProjectCreator;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string | null;
}

export interface ProjectUpdate {
  name?: string;
  description?: string | null;
}