export interface Deployment {
  id: string;
  version: string;
  git_commit: string;
  image_digest: string | null;
  pipeline_id: string | null;

  status:
    | "pending"
    | "in_progress"
    | "success"
    | "failed"
    | "rolled_back";

  deployed_at: string | null;

  service: {
    id: string;
    name: string;
    environment: string;
  };

  created_at: string;
}