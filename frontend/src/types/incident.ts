export interface Incident {
  id: string;
  title: string;
  description: string;

  severity:
    | "low"
    | "medium"
    | "high"
    | "critical";

  status:
    | "open"
    | "investigating"
    | "resolved"
    | "closed";

  detected_at: string;
  resolved_at: string | null;

  service: {
    id: string;
    name: string;
    environment: string;
  };
}