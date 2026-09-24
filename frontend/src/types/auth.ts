export interface Role {
  id: string;
  name: "Admin" | "Engineer" | "Viewer";
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  status: "active" | "disabled";
  is_verified: boolean;
  role: Role;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  identity: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
}