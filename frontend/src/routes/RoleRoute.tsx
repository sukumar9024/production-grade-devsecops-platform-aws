import {
  Navigate,
  Outlet,
} from "react-router-dom";

import { useAuth } from "../hooks/useAuth";


type Role =
  | "Admin"
  | "Engineer"
  | "Viewer";


interface RoleRouteProps {
  allowedRoles: Role[];
}


export function RoleRoute({
  allowedRoles,
}: RoleRouteProps) {
  const { user } = useAuth();

  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }

  if (
    !allowedRoles.includes(
      user.role.name
    )
  ) {
    return (
      <Navigate
        to="/unauthorized"
        replace
      />
    );
  }

  return <Outlet />;
}