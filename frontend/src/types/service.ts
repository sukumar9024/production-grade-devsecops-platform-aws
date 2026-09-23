export interface Service {
  id: string;
  name: string;
  environment:
    | "dev"
    | "staging"
    | "production";
  version: string | null;
  status:
    | "unknown"
    | "healthy"
    | "degraded"
    | "unavailable";
}